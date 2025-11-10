# srx-lib-azure

Lightweight wrappers over Azure SDKs used across SRX services.

What it includes:
- **Blob**: upload/download helpers, SAS URL generation
- **Email** (Azure Communication Services): simple async sender
- **Table**: simple CRUD helpers
- **Document Intelligence** (OCR): document analysis from URLs or bytes

## Install

PyPI (public):

- `pip install srx-lib-azure`

uv (pyproject):
```
[project]
dependencies = ["srx-lib-azure>=0.1.0"]
```

## Usage

Blob:
```
from srx_lib_azure.blob import AzureBlobService
blob = AzureBlobService()
url = await blob.upload_file(upload_file, "documents/report.pdf")
```

Email:
```
from srx_lib_azure.email import EmailService
svc = EmailService()
await svc.send_notification("user@example.com", "Subject", "Hello", html=False)
```

Table:
```
from srx_lib_azure.table import AzureTableService
store = AzureTableService()
store.ensure_table("events")
store.upsert_entity("events", {"PartitionKey":"p","RowKey":"r","EventType":"x"})
```

Document Intelligence (OCR):
```python
from srx_lib_azure import AzureDocumentIntelligenceService

# Initialize with endpoint and key
doc_service = AzureDocumentIntelligenceService(
    endpoint="https://your-resource.cognitiveservices.azure.com/",
    key="your-api-key"
)

# Analyze document from URL
result = await doc_service.analyze_document_from_url(
    url="https://example.com/document.pdf",
    model_id="prebuilt-read"  # or "prebuilt-layout", "prebuilt-invoice", etc.
)

# Analyze document from bytes
with open("document.pdf", "rb") as f:
    content = f.read()
result = await doc_service.analyze_document_from_bytes(
    file_content=content,
    model_id="prebuilt-read"
)

# Result structure:
# {
#     "success": True/False,
#     "content": "extracted text...",
#     "pages": [{"page_number": 1, "width": 8.5, ...}, ...],
#     "page_count": 10,
#     "confidence": 0.98,
#     "model_id": "prebuilt-read",
#     "metadata": {...},
#     "error": None  # or error message if failed
# }
```

## Environment Variables

- **Blob & Table**: `AZURE_STORAGE_CONNECTION_STRING` (required)
- **Email (ACS)**: `ACS_CONNECTION_STRING`, `EMAIL_SENDER`
- **Document Intelligence**: `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`, `AZURE_DOCUMENT_INTELLIGENCE_KEY`
- **Optional**: `AZURE_STORAGE_ACCOUNT_KEY`, `AZURE_BLOB_URL`, `AZURE_SAS_TOKEN`

## Optional Dependencies

All services are optional and won't break if their dependencies aren't installed:

```bash
# Base installation (includes all services by default)
pip install srx-lib-azure

# Or install only what you need - document intelligence is optional
pip install srx-lib-azure[document]  # Adds Document Intelligence support

# Install with all optional dependencies
pip install srx-lib-azure[all]
```

If you import a service without its required Azure SDK, it will log a warning but won't crash.

## Release

Tag `vX.Y.Z` to publish to GitHub Packages via Actions.

## License

Proprietary © SRX
