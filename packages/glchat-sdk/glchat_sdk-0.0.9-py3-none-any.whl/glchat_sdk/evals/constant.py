"""Constants for the GLChat evals.

Authors:
    Christina Alexandra (christina.alexandra@gdplabs.id)

References:
    NONE
"""

import encodings


class GLChatSearchTypes:
    """GLChat search types used for configuration."""

    NORMAL = "normal"
    SEARCH = "search"
    WEB = "web"
    DEEP_RESEARCH = "deep_research"
    ESSENTIALS_DEEP_RESEARCH = "essentials_deep_research"
    COMPREHENSIVE_DEEP_RESEARCH = "comprehensive_deep_research"


class GLChatFieldNames:
    """GLChat field names used in API requests and responses."""

    BASE_URL = "base_url"
    API_KEY = "api_key"
    CHATBOT_ID = "chatbot_id"
    MESSAGE = "message"
    USER_ID = "user_id"
    TITLE = "title"
    CONVERSATION_ID = "conversation_id"
    MODEL_NAME = "model_name"
    ANONYMIZE_LM = "anonymize_lm"
    SEARCH_TYPE = "search_type"
    INCLUDE_STATES = "include_states"
    CHAT_HISTORY = "chat_history"
    FILES = "files"
    QUESTION_ID = "question_id"
    QUERY = "query"
    ENABLE_PII = "enable_pii"
    ID = "id"
    STATUS = "status"
    DATA_TYPE = "data_type"
    PARENT_ID = "parent_id"
    DATA_VALUE = "data_value"
    AI_MESSAGE = "ai_message"
    DEANONYMIZED_CONTENT = "deanonymized_content"
    DEANONYMIZED_MAPPING = "deanonymized_mapping"
    CONTEXT = "context"
    ATTACHMENTS = "attachments"
    EXPIRY_DAYS = "expiry_days"
    CONVERSATION = "conversation"
    CONNECTORS = "connectors"


class GLChatDataTypes:
    """GLChat data types used in SSE responses."""

    MEDIA_MAPPING = "media_mapping"
    STATES = "states"
    DEANONYMIZED_DATA = "deanonymized_data"
    RESPONSE = "response"
    DATA = "data"
    ASSISTANT_MESSAGE_ID = "assistant_message_id"


class GLChatEnvVars:
    """GLChat environment variables."""

    GLCHAT_BASE_URL = "GLCHAT_BASE_URL"
    GLCHAT_API_KEY = "GLCHAT_API_KEY"


class GLChatSSEKeys:
    """GLChat Server-Sent Events keys and prefixes."""

    DATA_PREFIX = "data:"
    UNKERR_ERROR = "UNKERR"


class GLChatHTTPKeys:
    """GLChat HTTP headers and authentication keys."""

    AUTHORIZATION = "Authorization"
    BEARER = "Bearer"


class GLChatDefaults:
    """GLChat default values."""

    USERNAME = "tester_eval1@glair.ai"
    MODEL_NAME = None
    QUESTION_ID = "unknown"
    PROJECT_NAME = "glchat_beta"
    UTF8_ENCODING = encodings.utf_8.getregentry().name
    CONNECTOR_WEB = '["web"]'
    OUTPUT_DIR = "glchat_sdk/evals_outputs"


class GLChatResponseKeys:
    """GLChat response dictionary keys."""

    GENERATED_RESPONSE = "generated_response"
    GENERATED_RESPONSE_URL = "generated_response_url"
    RETRIEVED_CONTEXT = "retrieved_context"
    EXPECTED_RESPONSE = "expected_response"
    METADATA = "metadata"


class GeneralKeys:
    """General keys used in the SDK."""

    TAGS = "tags"
    EVALUATION_TAG = "evaluation"
    GLCHAT_TAG = "glchat"
    TAG = "tag"
    PROJECT_NAME = "project_name"


class EnvironmentVariables:
    """Environment variables used in the SDK."""

    LANGFUSE_PUBLIC_KEY = "LANGFUSE_PUBLIC_KEY"
    LANGFUSE_SECRET_KEY = "LANGFUSE_SECRET_KEY"
    LANGFUSE_HOST = "LANGFUSE_HOST"
    GOOGLE_SHEETS_CLIENT_EMAIL = "GOOGLE_SHEETS_CLIENT_EMAIL"
    GOOGLE_SHEETS_PRIVATE_KEY = "GOOGLE_SHEETS_PRIVATE_KEY"
    GLCHAT_BASE_URL = "GLCHAT_BASE_URL"
    GLCHAT_API_KEY = "GLCHAT_API_KEY"
    OPENAI_API_KEY = "OPENAI_API_KEY"
    GOOGLE_API_KEY = "GOOGLE_API_KEY"


REQUIRED_ENV_VARS = [
    EnvironmentVariables.LANGFUSE_PUBLIC_KEY,
    EnvironmentVariables.LANGFUSE_SECRET_KEY,
    EnvironmentVariables.LANGFUSE_HOST,
    EnvironmentVariables.GOOGLE_SHEETS_CLIENT_EMAIL,
    EnvironmentVariables.GOOGLE_SHEETS_PRIVATE_KEY,
    EnvironmentVariables.GLCHAT_BASE_URL,
    EnvironmentVariables.GLCHAT_API_KEY,
    EnvironmentVariables.OPENAI_API_KEY,
    EnvironmentVariables.GOOGLE_API_KEY,
]
