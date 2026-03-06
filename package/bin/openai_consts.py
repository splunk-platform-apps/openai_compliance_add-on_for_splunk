ADDON_NAME = "openai_compliance_addon_for_splunk"
OPENAI_COMPLIANCE_API_BASE_URL = (
    "https://api.chatgpt.com/v1/compliance/workspaces/{workspace_id}"
)
CONVERSATIONS = "/conversations"
USERS = "users"
PROJECTS = "projects"
GPTS = "gpts"
USER_CANVASES = "users/{user_id}/canvases"
CANVAS_CONTENT = "users/{user_id}/canvas/{textdoc_id}"
LIST_FILES = "logs"
GET_FILE_CONTENT = "logs/{log_file_id}"
