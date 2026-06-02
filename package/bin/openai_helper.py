import requests
import logging

from solnlib import conf_manager, log
from solnlib.modular_input import checkpointer
from openai_consts import ADDON_NAME, GET_FILE_CONTENT, OPENAI_COMPLIANCE_API_BASE_URL


def set_logger(input_name: str, session_key: str) -> logging.Logger:
    normalized_input_name = input_name.split("/")[-1]

    logger = log.Logs().get_logger(f"{ADDON_NAME.lower()}_{normalized_input_name}")

    log_level = conf_manager.get_log_level(
        logger=logger,
        session_key=session_key,
        app_name=ADDON_NAME,
        conf_name="openai_compliance_addon_for_splunk_settings",
    )

    logger.setLevel(log_level)

    log.modular_input_start(logger, normalized_input_name)

    return logger


class OpenAIHelper:
    def __init__(self, input_name, session_key, config, account_name):
        self.input_name = input_name
        self.session_key = session_key
        self.config = config
        self.account_name = account_name
        self.logger = set_logger(input_name, session_key)
        self.checkpointer = checkpointer.KVStoreCheckpointer(
            collection_name=f"{ADDON_NAME}_checkpointer",
            session_key=session_key,
            app=ADDON_NAME,
        )

    def get_account_data(self, conf_filename):
        cfm = conf_manager.ConfManager(
            self.session_key,
            ADDON_NAME,
            realm=f"__REST_CREDENTIAL__#{ADDON_NAME}#configs/conf-{conf_filename}",
        )

        account_conf_file = cfm.get_conf(conf_filename)

        api_key = account_conf_file.get(self.account_name).get("api_key")
        workspace_id = account_conf_file.get(self.account_name).get("workspace_id")
        return api_key, workspace_id

    def get_checkpoint_for_request(self, checkpoint_name, endpoint, start_time_arg):
        last_record_checkpoint_value = self.checkpointer.get(checkpoint_name)

        checkpoint_value = None

        # There's a value already stored as checkpoint
        if last_record_checkpoint_value is not None:
            checkpoint_value = last_record_checkpoint_value
        else:
            # During the first run of the input only the conversations and logs endpoints requires a start_time param, the rest of the endpoints don't need it
            if endpoint == "logs" or endpoint == "conversations":
                checkpoint_value = start_time_arg

        return checkpoint_value

    def make_request(self, api_key, workspace_id, endpoint, params):
        try:
            compliance_data = []
            last_index = None

            URL = (
                OPENAI_COMPLIANCE_API_BASE_URL.format(workspace_id=workspace_id)
                + "/"
                + endpoint
            )

            self.logger.debug(f"URL: {URL}")

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            while True:
                response = requests.get(URL, params=params, headers=headers)

                response.raise_for_status()

                result = response.json()

                data = result.get("data", None)

                if not data:
                    break

                compliance_data.extend(data)
                has_more = result.get("has_more", False)
                last_index = result.get("last_id") or result.get("last_end_time")

                if has_more and last_index:
                    # Update params to fetch next page
                    params["after"] = last_index
                else:
                    break

            return compliance_data, last_index

        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise

    def get_log_files_content(self, api_key, workspace_id, log_files):
        result = []

        try:
            for log_file in log_files:
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

                response = requests.get(url, headers=headers)

                self.logger.debug(f"response from request: {response}")

                response.raise_for_status()

                file_content = response.text

                events = file_content.splitlines()

                result.extend(events)
            return result
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise
