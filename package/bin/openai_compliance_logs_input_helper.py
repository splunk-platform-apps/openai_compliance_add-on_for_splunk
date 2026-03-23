import json
from splunklib import modularinput as smi
import requests

from openai_helper import OpenAIHelper
from openai_consts import OPENAI_COMPLIANCE_API_BASE_URL, LIST_FILES, GET_FILE_CONTENT


def validate_input(definition: smi.ValidationDefinition):
    return


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
            endpoint_arg = LIST_FILES

            # arguments provided by the user
            # get the start_time for the param: after and convert it to the format: 2025-09-23T00:58:39
            start_time_arg = input_item.get("start_time")
            start_time_arg = start_time_arg.replace("Z", "")
            logger.debug(f"start_time_arg: {start_time_arg}")

            event_type = input_item.get("event_type")
            logger.debug(f"event_type: {event_type}")

            checkpoint_name = f"{normalized_input_name}_checkpoint"

            api_key, workspace_id = helper.get_account_data(
                "openai_compliance_addon_for_splunk_account"
            )

            checkpoint_value = helper.get_checkpoint_for_request(
                checkpoint_name, endpoint_arg, start_time_arg
            )

            logger.debug(f"Using {checkpoint_value} as checkpoint for {endpoint_arg}")

            params = {"limit": 100, "after": checkpoint_value, "event_type": event_type}

            logger.debug(f"Params for {endpoint_arg}: {params}")

            # get the log files list
            log_files, last_end_time = helper.make_request(
                api_key, workspace_id, endpoint_arg, params
            )
            logger.debug(f"before: last_end_time: {last_end_time}")

            if last_end_time is not None and "Z" in last_end_time:
                last_end_time = last_end_time.replace("Z", "")

            logger.debug(f"after: last_end_time: {last_end_time}")

            if not log_files:
                logger.info(f"No data was found for {endpoint_arg} at this time.")
                return

            is_checkpoint_saved = False

            if log_files:
                count = 0
                for log_file in log_files:
                    # Download the file
                    log_file_id = log_file.get("id")

                    if not log_file_id:
                        continue

                    url = (
                        OPENAI_COMPLIANCE_API_BASE_URL.format(workspace_id=workspace_id)
                        + "/"
                        + GET_FILE_CONTENT.format(log_file_id=log_file_id)
                    )

                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    }

                    response = requests.get(url, params=params, headers=headers)

                    logger.debug(f"response from request: {response}")

                    response.raise_for_status()

                    file_content = response.text

                    events = file_content.splitlines()

                    for event in events:
                        event = json.loads(event)
                        logger.debug(f"Event: {type(event)} {event}")

                        # Write the file content into Splunk
                        sourcetype = "openai:compliance:logs"

                        if event.get("type"):
                            sourcetype = (
                                f"openai:compliance:{event.get('type').lower()}"
                            )

                        logger.debug(f"Sourcetype: {sourcetype}")

                        event_writer.write_event(
                            smi.Event(
                                data=json.dumps(event),
                                index=input_item.get("index"),
                                sourcetype=sourcetype,
                            )
                        )

                        count += 1

                if not is_checkpoint_saved:
                    # save last_id as checkpoint
                    checkpoint.update(checkpoint_name, last_end_time)
                logger.info(
                    f"Execution completed. A total of {count} new events were ingested."
                )
        except Exception as e:
            logger.error(f"An error has ocurred in stream_events - {e}")
