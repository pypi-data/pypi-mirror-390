from .blob import AzureBlobService
from .document import AzureDocumentIntelligenceService
from .email import EmailService
from .table import AzureTableService

# Optional import - only available if speech extra is installed
try:
    from .speech import AzureSpeechService
    __all__ = [
        "AzureBlobService",
        "AzureDocumentIntelligenceService",
        "AzureTableService",
        "EmailService",
        "AzureSpeechService",
    ]
except ImportError:
    # Speech SDK not installed - service not available
    __all__ = [
        "AzureBlobService",
        "AzureDocumentIntelligenceService",
        "AzureTableService",
        "EmailService",
    ]
