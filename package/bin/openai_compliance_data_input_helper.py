import json
import traceback
from splunklib import modularinput as smi
from datetime import datetime
from openai_consts import (
    LIST_FILES,
    USER_CANVASES,
    USERS,
    CANVAS_CONTENT,
)

from openai_helper import OpenAIHelper


def validate_input(definition: smi.ValidationDefinition):
    endpoint = definition.parameters.get("endpoint")

    if endpoint == "conversations":
        start_time = definition.parameters.get("start_time")

        if not start_time:
            raise ValueError("Please fill out the FROM field.")
    return


def get_conversations(helper, api_key, workspace_id, checkpoint_value):
    conversations = []

    params = {
        "limit": 100,
        "after": checkpoint_value,
        "event_type": "CONVERSATION_MESSAGE",
    }

    # get the list of log files
    log_files, last_end_time = helper.make_request(
        api_key, workspace_id, LIST_FILES, params
    )

    if not log_files:
        return []

    # get the content from each file
    events = helper.get_log_files_content(api_key, workspace_id, log_files)

    for event in events:
        event = json.loads(event)

        message = event.get("message", {})

        conversation = event.get("conversation", None)

        content = message.get("content", None)

        # check for content and conversation objects - if their content is empty ignore that event
        if not content or not conversation:
            continue

        conversations.append(event)

    return conversations


def get_canvases(helper, api_key, workspace_id, params):
    users, last_id = helper.make_request(api_key, workspace_id, USERS, params)

    canvases = []

    if users:
        for user in users:
            user_id = user["id"]
            user_canvases_endpoint = USER_CANVASES.format(user_id=user_id)

            # Get each canvas from each user
            user_canvases, last_user_canvas_id = helper.make_request(
                api_key, workspace_id, user_canvases_endpoint, {}
            )

            if user_canvases:
                for canvas in user_canvases:
                    canvas_id = canvas["id"]
                    canvas_content_endpoint = CANVAS_CONTENT.format(
                        user_id=user_id, textdoc_id=canvas_id
                    )

                    # Get the canvas content
                    canvas_content, last_content_id = helper.make_request(
                        api_key, workspace_id, canvas_content_endpoint, {}
                    )

                    if canvas_content:
                        canvases.append(canvas_content)

    return canvases, last_id


def stream_events(inputs: smi.InputDefinition, event_writer: smi.EventWriter):
    for input_name, input_item in inputs.inputs.items():
        normalized_input_name = input_name.split("/")[-1]
        session_key = inputs.metadata["session_key"]
        account_name = input_item.get("account")

        try:
            # Initialize Helper
            helper = OpenAIHelper(
                normalized_input_name, session_key, input_item, account_name
            )
            checkpoint = helper.checkpointer
            logger = helper.logger

            # arguments provided by the user
            start_time_arg = input_item.get("start_time")
            endpoint_arg = input_item.get("endpoint")

            checkpoint_name = f"{normalized_input_name}_checkpoint"

            api_key, workspace_id = helper.get_account_data(
                "openai_compliance_addon_for_splunk_account"
            )

            checkpoint_value = helper.get_checkpoint_for_request(
                checkpoint_name, endpoint_arg, start_time_arg
            )

            logger.debug(
                f"Ingesting data from {endpoint_arg} endpoint - Workspace: {workspace_id}."
            )

            logger.debug(f"Using {checkpoint_value} as checkpoint for {endpoint_arg}")

            params = {"limit": 450}

            if checkpoint_value:
                params["after"] = checkpoint_value

            logger.debug(f"Params for {endpoint_arg}: {params}")

            event_count = 0
            sourcetype = f"openai:compliance:{endpoint_arg}"

            if endpoint_arg == "canvases":
                canvases, last_id = get_canvases(helper, api_key, workspace_id, params)

                if not canvases:
                    logger.info(f"No canvases found for workspace {workspace_id}")
                    return

                for canvas in canvases:
                    event_writer.write_event(
                        smi.Event(
                            data=json.dumps(canvas),
                            index=input_item.get("index"),
                            sourcetype=sourcetype,
                        )
                    )

                    event_count += 1

                checkpoint.update(checkpoint_name, last_id)
                logger.debug(f"New checkpoint saved for canvases: {last_id}")
            elif endpoint_arg == "conversations":
                conversations = get_conversations(
                    helper, api_key, workspace_id, checkpoint_value
                )

                if not conversations:
                    logger.info(f"No conversations found for workspace {workspace_id}")
                    return

                for conversation_event in conversations:
                    conversation_details = conversation_event["conversation"]
                    created_at = conversation_details["created_at"]

                    created_at_ts = datetime.strptime(
                        created_at, "%Y-%m-%dT%H:%M:%SZ"
                    ).timestamp()

                    event_writer.write_event(
                        smi.Event(
                            data=json.dumps(conversation_event),
                            index=input_item.get("index"),
                            sourcetype=sourcetype,
                            time=created_at_ts,
                        )
                    )

                    event_count += 1

                new_check_point_value = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

                checkpoint.update(checkpoint_name, new_check_point_value)

                logger.debug(
                    f"New checkpoint saved for conversations: {new_check_point_value}"
                )
            else:
                # get the data
                data, last_id = helper.make_request(
                    api_key, workspace_id, endpoint_arg, params
                )

                if not data:
                    logger.info(f"No data found for {endpoint_arg} at this time.")
                    return

                for event in data:
                    event_writer.write_event(
                        smi.Event(
                            data=json.dumps(event),
                            index=input_item.get("index"),
                            sourcetype=sourcetype,
                        )
                    )

                    event_count += 1

                checkpoint.update(checkpoint_name, last_id)
                logger.debug(f"New checkpoint saved for {endpoint_arg}: {last_id}")

            logger.info(
                f"Execution completed. A total of {event_count} new events were ingested."
            )
        except Exception as e:
            logger.error(
                f"An error has ocurred in stream_events: {e}.  Traceback: {traceback.format_exc()}"
            )
