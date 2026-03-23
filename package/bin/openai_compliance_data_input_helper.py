import json
import traceback
from splunklib import modularinput as smi
from datetime import datetime
from openai_consts import USER_CANVASES, USERS, CANVAS_CONTENT

from openai_helper import OpenAIHelper


def validate_input(definition: smi.ValidationDefinition):
    endpoint = definition.parameters.get("endpoint")

    if endpoint == "conversations":
        start_time = definition.parameters.get("start_time")

        if not start_time:
            raise ValueError("Please fill out the FROM field.")
    return


def get_conversations(data, checkpoint_value):
    conversations = []

    for event in data:
        messages = event.get("messages")

        if messages:
            messages_list = messages.get("data")

            for message in messages_list:
                content = message["content"]
                created_at = message["created_at"]

                # skip the message if it has no content or creation time
                if not content or not created_at:
                    continue

                # ignore the message if it was created before the previous run
                if created_at < checkpoint_value:
                    continue

                new_event = {
                    "object": event.get("object", ""),
                    "id": event.get("id", ""),
                    "workspace_id": event.get("workspace_id", ""),
                    "user_id": event.get("user_id", ""),
                    "user_email": event.get("user_email", ""),
                    "created_at": created_at,
                    "last_active_at": event.get("last_active_at", ""),
                    "title": event.get("title", ""),
                    "messages": {
                        "author": message.get("author", {}),
                        "content": content,
                    },
                    "files": message.get("files", {}),
                }

                conversations.append(new_event)
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
                if endpoint_arg == "conversations":
                    params["since_timestamp"] = checkpoint_value
                elif endpoint_arg in ["users", "projects", "gpts", "canvases"]:
                    params["after"] = checkpoint_value

            logger.debug(f"Params for {endpoint_arg}: {params}")

            if endpoint_arg == "canvases":
                # Retrieve the list of users first and then the canvas content.
                canvases, last_id = get_canvases(helper, api_key, workspace_id, params)

                if canvases:
                    for canvas in canvases:
                        sourcetype = f"openai:compliance:{endpoint_arg}"

                        event_writer.write_event(
                            smi.Event(
                                data=json.dumps(canvas),
                                index=input_item.get("index"),
                                sourcetype=sourcetype,
                            )
                        )

                    checkpoint.update(checkpoint_name, last_id)
                else:
                    logger.info(f"No users were found for workspace {workspace_id}")
                    return
            else:
                # get the data
                data, last_id = helper.make_request(
                    api_key, workspace_id, endpoint_arg, params
                )

                if not data:
                    logger.info(f"No data was found for {endpoint_arg} at this time.")
                    return

                is_checkpoint_saved = False

                if data:
                    sourcetype = f"openai:compliance:{endpoint_arg}"
                    event_count = 0

                    if endpoint_arg == "conversations":
                        conversations = get_conversations(data, checkpoint_value)

                        for conversation_event in conversations:
                            event_writer.write_event(
                                smi.Event(
                                    data=json.dumps(conversation_event),
                                    index=input_item.get("index"),
                                    sourcetype=sourcetype,
                                )
                            )

                            event_count += 1

                            current_ts = int(datetime.now().timestamp())

                            # save run time checkpoint after each event is saved
                            checkpoint.update(checkpoint_name, current_ts)

                            is_checkpoint_saved = True

                            logger.debug(
                                f"Last timestamp saved as checkpoint: {current_ts}"
                            )
                    else:
                        for event in data:
                            event_writer.write_event(
                                smi.Event(
                                    data=json.dumps(event),
                                    index=input_item.get("index"),
                                    sourcetype=sourcetype,
                                )
                            )

                            event_count += 1

                    if endpoint_arg != "conversations":
                        if not is_checkpoint_saved:
                            # For all other endpoints use last_id as checkpoint
                            checkpoint.update(checkpoint_name, last_id)
                            logger.info(f"Checkpoint updated with last_id: {last_id}")

                    logger.info(
                        f"Execution completed. A total of {event_count} new events were ingested."
                    )
        except Exception as e:
            logger.error(
                f"An error has ocurred in stream_events: {e}.  Traceback: {traceback.format_exc()}"
            )
