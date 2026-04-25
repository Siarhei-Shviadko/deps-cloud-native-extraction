PROJECT_NAME = "cloud-native-extraction"
DESCRIPTION = "Service for communicating between Deps and Cloud Native Extraction services"
V1_PREFIX = "/v1"
BASE_API_PREFIX = "/api/cloud-native-extraction"
V1_API_PREFIX = BASE_API_PREFIX + V1_PREFIX
SWAGGER_DOC_URL = "/docs"

DOCUMENTS_EXCHANGER = "Documents"
DOCUMENT_TYPE_EXCHANGER = "DocumentType"
EXTRACTOR_EXCHANGER = "Extractor"

EVENTS_QUEUE = "cloud-native-extraction-events"
COMMANDS_QUEUE = "cloud-native-extraction-commands"

COMMANDS_CHANNEL = "CloudNativeExtractionCommands"
COMMANDS_REPLIES_CHANNEL = "CloudNativeExtractionCommandsReplies"
