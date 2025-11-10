import os
import io
import asyncio
from typing import Dict, Any, Optional

from loguru import logger

try:
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, AnalyzeResult
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import (
        ClientAuthenticationError,
        HttpResponseError,
        ServiceRequestError,
    )
except Exception:  # pragma: no cover - optional dependency at import time
    DocumentIntelligenceClient = None  # type: ignore
    AnalyzeDocumentRequest = None  # type: ignore
    AnalyzeResult = None  # type: ignore
    AzureKeyCredential = None  # type: ignore
    ClientAuthenticationError = None  # type: ignore
    HttpResponseError = None  # type: ignore
    ServiceRequestError = None  # type: ignore


class AzureDocumentIntelligenceService:
    """Wrapper for Azure Document Intelligence (OCR/Document Analysis).

    Does not raise on missing configuration to keep the library optional.
    If not configured, analysis calls return error responses with descriptive messages.
    """

    def __init__(
        self,
        *,
        endpoint: Optional[str] = None,
        key: Optional[str] = None,
        warn_if_unconfigured: bool = False,
    ):
        """Initialize Document Intelligence service.

        Args:
            endpoint: Azure Document Intelligence endpoint URL
            key: Azure Document Intelligence API key
            warn_if_unconfigured: Whether to log a warning if not configured
        """
        self.endpoint = endpoint or os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        self.key = key or os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

        if not self.endpoint or not self.key or DocumentIntelligenceClient is None:
            self.client = None
            if warn_if_unconfigured:
                logger.warning(
                    "AzureDocumentIntelligenceService not configured "
                    "(missing endpoint/key or azure-ai-documentintelligence SDK). "
                    "Calls will return error responses."
                )
        else:
            try:
                self.client = DocumentIntelligenceClient(
                    endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
                )
            except Exception as e:
                self.client = None
                logger.warning("DocumentIntelligenceClient initialization failed: %s", e)

    async def analyze_document_from_url(
        self, url: str, model_id: str = "prebuilt-read"
    ) -> Dict[str, Any]:
        """Analyze a document from a URL using Azure Document Intelligence.

        Args:
            url: URL of the document to analyze (must be accessible to Azure)
            model_id: Model to use (default: "prebuilt-read" for OCR)
                     Other options: "prebuilt-layout", "prebuilt-invoice", etc.

        Returns:
            Dict with analysis results:
            - success (bool): Whether analysis succeeded
            - content (str | None): Extracted text content
            - pages (list[dict] | None): Page information
            - page_count (int | None): Total number of pages
            - confidence (float | None): Average OCR confidence (0-1)
            - model_id (str | None): Model used
            - metadata (dict | None): Additional metadata
            - error (str | None): Error message if failed
        """
        if not self.client:
            logger.warning("Document analysis from URL skipped: service not configured")
            return {
                "success": False,
                "error": "Document Intelligence service not configured",
            }

        try:
            logger.info(f"Starting document analysis from URL: {url} (model: {model_id})")

            # Run the blocking operation in a thread pool
            poller = await asyncio.to_thread(
                self.client.begin_analyze_document,
                model_id,
                AnalyzeDocumentRequest(url_source=url),
            )

            # Wait for the result
            result: AnalyzeResult = await asyncio.to_thread(poller.result)

            logger.info(
                f"Document analysis completed (model: {model_id}, pages: {len(result.pages or [])})"
            )

            return self._format_result(result, model_id)

        except ClientAuthenticationError as e:
            logger.error(f"Authentication failed for document analysis: {e}")
            return {"success": False, "error": f"Authentication failed: {e}"}
        except HttpResponseError as e:
            logger.error(f"Azure service error analyzing document: {e.status_code} - {e.message}")
            return {
                "success": False,
                "error": f"Azure service error ({e.status_code}): {e.message}",
            }
        except ServiceRequestError as e:
            logger.error(f"Network error analyzing document: {e}")
            return {"success": False, "error": f"Network error: {e}"}
        except Exception as e:
            logger.error(f"Unexpected error analyzing document from URL: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    async def analyze_document_from_bytes(
        self, file_content: bytes, model_id: str = "prebuilt-read"
    ) -> Dict[str, Any]:
        """Analyze a document from bytes using Azure Document Intelligence.

        Args:
            file_content: Document content as bytes (PDF, image, etc.)
            model_id: Model to use (default: "prebuilt-read" for OCR)

        Returns:
            Dict with analysis results (same format as analyze_document_from_url)
        """
        if not self.client:
            logger.warning("Document analysis from bytes skipped: service not configured")
            return {
                "success": False,
                "error": "Document Intelligence service not configured",
            }

        try:
            logger.info(
                f"Starting document analysis from bytes (size: {len(file_content)} bytes, model: {model_id})"
            )

            # Create a file-like object from bytes
            file_stream = io.BytesIO(file_content)

            # Run the blocking operation in a thread pool
            poller = await asyncio.to_thread(
                self.client.begin_analyze_document,
                model_id,
                body=file_stream,
            )

            # Wait for the result
            result: AnalyzeResult = await asyncio.to_thread(poller.result)

            logger.info(
                f"Document analysis completed (model: {model_id}, pages: {len(result.pages or [])})"
            )

            return self._format_result(result, model_id)

        except ClientAuthenticationError as e:
            logger.error(f"Authentication failed for document analysis: {e}")
            return {"success": False, "error": f"Authentication failed: {e}"}
        except HttpResponseError as e:
            logger.error(f"Azure service error analyzing document: {e.status_code} - {e.message}")
            return {
                "success": False,
                "error": f"Azure service error ({e.status_code}): {e.message}",
            }
        except ServiceRequestError as e:
            logger.error(f"Network error analyzing document: {e}")
            return {"success": False, "error": f"Network error: {e}"}
        except Exception as e:
            logger.error(f"Unexpected error analyzing document from bytes: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    def _format_result(self, result: AnalyzeResult, model_id: str) -> Dict[str, Any]:
        """Format the AnalyzeResult into a dict response.

        Args:
            result: Azure Document Intelligence AnalyzeResult
            model_id: Model ID used for analysis

        Returns:
            Formatted dict with extracted content and metadata
        """
        # Extract all text content
        content_parts: list[str] = []
        pages_info: list[Dict[str, Any]] = []
        total_confidence = 0.0
        confidence_count = 0

        if result.pages:
            for page in result.pages:
                # Collect page info
                page_info = {
                    "page_number": page.page_number,
                    "width": page.width,
                    "height": page.height,
                    "unit": page.unit,
                    "lines_count": len(page.lines or []),
                    "words_count": len(page.words or []),
                }
                pages_info.append(page_info)

                # Extract text from lines
                if page.lines:
                    for line in page.lines:
                        content_parts.append(line.content)
                        # Track confidence if available
                        if hasattr(line, "confidence") and line.confidence is not None:
                            total_confidence += line.confidence
                            confidence_count += 1

        # Combine all content with newlines
        full_content = "\n".join(content_parts)

        # Calculate average confidence
        avg_confidence = total_confidence / confidence_count if confidence_count > 0 else None

        # Build metadata
        metadata: Dict[str, Any] = {
            "content_format": (
                result.content_format if hasattr(result, "content_format") else None
            ),
            "api_version": result.api_version if hasattr(result, "api_version") else None,
        }

        # Add languages if detected
        if hasattr(result, "languages") and result.languages:
            metadata["languages"] = [
                {"locale": lang.locale, "confidence": lang.confidence} for lang in result.languages
            ]

        # Add styles if detected (e.g., handwriting)
        if hasattr(result, "styles") and result.styles:
            metadata["has_handwriting"] = any(
                style.is_handwritten for style in result.styles if hasattr(style, "is_handwritten")
            )

        return {
            "success": True,
            "content": full_content if full_content else None,
            "pages": pages_info if pages_info else None,
            "page_count": len(pages_info) if pages_info else None,
            "confidence": avg_confidence,
            "model_id": model_id,
            "metadata": metadata,
        }
