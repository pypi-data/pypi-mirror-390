"""
Client-side constants - minimal set needed by schemas and client code.

These are the constants required by the client package (schemas, helpers, client).
The full server constants module (mirix.constants) imports from here and adds
additional server-only constants.
"""

# Default organization and user IDs (needed by schemas)
DEFAULT_ORG_ID = "org-00000000-0000-4000-8000-000000000000"
DEFAULT_USER_ID = "user-00000000-0000-4000-8000-000000000000"

# Embedding constants
MAX_EMBEDDING_DIM = 4096  # maximum supported embedding size - do NOT change or else DBs will need to be reset
DEFAULT_EMBEDDING_CHUNK_SIZE = 300
MIN_CONTEXT_WINDOW = 4096

# Memory limits
CORE_MEMORY_BLOCK_CHAR_LIMIT: int = 5000

# Function/Tool constants
FUNCTION_RETURN_CHAR_LIMIT = 60000  # ~300 words
TOOL_CALL_ID_MAX_LEN = 29

# Tool module names
COMPOSIO_TOOL_TAG_NAME = "composio"
MIRIX_CORE_TOOL_MODULE_NAME = "mirix.functions.function_sets.base"
MIRIX_MEMORY_TOOL_MODULE_NAME = "mirix.functions.function_sets.memory_tools"
MIRIX_EXTRA_TOOL_MODULE_NAME = "mirix.functions.function_sets.extras"

# Message defaults
DEFAULT_MESSAGE_TOOL = "send_message"
DEFAULT_MESSAGE_TOOL_KWARG = "message"

# LLM model token limits
LLM_MAX_TOKENS = {
    "DEFAULT": 8192,
    ## OpenAI models: https://platform.openai.com/docs/models/overview
    "chatgpt-4o-latest": 128000,
    "gpt-4o-2024-08-06": 128000,
    "gpt-4-turbo-preview": 128000,
    "gpt-4o": 128000,
    "gpt-3.5-turbo-instruct": 16385,
    "gpt-4-0125-preview": 128000,
    "gpt-3.5-turbo-0125": 16385,
    "gpt-4-turbo-2024-04-09": 128000,
    "gpt-4-turbo": 8192,
    "gpt-4o-2024-05-13": 128000,
    "gpt-4o-mini": 128000,
    "gpt-4o-mini-2024-07-18": 128000,
    "gpt-4-1106-preview": 128000,
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-0613": 8192,
    "gpt-4-32k-0613": 32768,
    "gpt-4-0314": 8192,  # legacy
    "gpt-4-32k-0314": 32768,  # legacy
    "gpt-3.5-turbo-1106": 16385,
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-16k": 16385,
    "gpt-3.5-turbo-0613": 4096,  # legacy
    "gpt-3.5-turbo-16k-0613": 16385,  # legacy
    "gpt-3.5-turbo-0301": 4096,  # legacy
}
