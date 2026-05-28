import json
from splunklib import modularinput as smi

from openai_helper import OpenAIHelper
from openai_consts import LIST_FILES


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

            if last_end_time is not None and "Z" in last_end_time:
                last_end_time = last_end_time.replace("Z", "")

            if not log_files:
                logger.info(f"No data found for {endpoint_arg} at this time.")
                return

            events = helper.get_log_files_content(api_key, workspace_id, log_files)

            count = 0

            for event in events:
                event = json.loads(event)
                logger.debug(f"Event: {type(event)} {event}")

                # Write the file content into Splunk
                sourcetype = "openai:compliance:logs"

                if event.get("type"):
                    sourcetype = f"openai:compliance:{event.get('type').lower()}"

                logger.debug(f"Sourcetype: {sourcetype}")

                event_writer.write_event(
                    smi.Event(
                        data=json.dumps(event),
                        index=input_item.get("index"),
                        sourcetype=sourcetype,
                    )
                )

                count += 1

            checkpoint.update(checkpoint_name, last_end_time)

            logger.debug(f"Last timestamp saved as checkpoint: {last_end_time}")

            logger.info(
                f"Execution completed. A total of {count} new events were ingested."
            )
        except Exception as e:
            logger.error(f"An error has ocurred in stream_events - {e}")
