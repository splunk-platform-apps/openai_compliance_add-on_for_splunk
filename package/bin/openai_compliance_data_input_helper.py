import json
import traceback
from splunklib import modularinput as smi
from openai_consts import (
    USER_CANVASES,
    USERS,
    CANVAS_CONTENT,
)

from openai_helper import OpenAIHelper


def validate_input(definition: smi.ValidationDefinition):
    return


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
            endpoint_arg = input_item.get("endpoint")

            checkpoint_name = f"{normalized_input_name}_checkpoint"

            api_key, workspace_id = helper.get_account_data(
                "openai_compliance_addon_for_splunk_account"
            )

            checkpoint_value = helper.get_checkpoint_for_request(
                checkpoint_name, endpoint_arg, start_time_arg=None
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
