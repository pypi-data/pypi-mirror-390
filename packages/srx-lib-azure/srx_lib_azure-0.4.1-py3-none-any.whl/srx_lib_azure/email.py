import os
import logging
from typing import Dict, Any

try:
    from azure.communication.email.aio import EmailClient
    from azure.core.exceptions import (
        ClientAuthenticationError,
        HttpResponseError,
        ServiceRequestError,
    )
except Exception:  # pragma: no cover - optional dependency at import time
    EmailClient = None  # type: ignore
    ClientAuthenticationError = None  # type: ignore
    HttpResponseError = None  # type: ignore
    ServiceRequestError = None  # type: ignore

logger = logging.getLogger(__name__)


class EmailService:
    """Thin wrapper over Azure Communication Services EmailClient.

    Does not raise on missing configuration to keep the library optional.
    If not configured, send calls are skipped with a warning and a 'skipped' status.
    """

    def __init__(
        self,
        *,
        connection_string: str | None = None,
        sender_address: str | None = None,
        warn_if_unconfigured: bool = False,
    ):
        self.connection_string = connection_string or os.getenv("ACS_CONNECTION_STRING")
        self.sender_address = sender_address or os.getenv("EMAIL_SENDER")
        if not self.connection_string or not self.sender_address or EmailClient is None:
            self.email_client = None
            if warn_if_unconfigured:
                logger.warning(
                    "EmailService not configured (missing ACS_CONNECTION_STRING/EMAIL_SENDER or azure SDK). Calls will be skipped."
                )
        else:
            try:
                self.email_client = EmailClient.from_connection_string(self.connection_string)
            except Exception as e:
                self.email_client = None
                logger.warning("EmailService initialization failed: %s", e)

    async def send_notification(
        self, recipient: str, subject: str, body: str, html: bool = False
    ) -> Dict[str, Any]:
        """Send an email notification via Azure Communication Services.

        Args:
            recipient: Email address of the recipient
            subject: Email subject line
            body: Email body content
            html: If True, send as HTML; otherwise plain text

        Returns:
            Dict with status, message, and optional message_id
            - status: "success" | "error" | "skipped"
            - message: Human-readable message
            - message_id: Azure message ID (only on success)
        """
        if not self.email_client or not self.sender_address:
            logger.warning("Email skipped: service not configured")
            return {"status": "skipped", "message": "Email service not configured"}

        message = {
            "content": {"subject": subject},
            "recipients": {"to": [{"address": recipient}]},
            "senderAddress": self.sender_address,
        }
        if html:
            message["content"]["html"] = body
        else:
            message["content"]["plainText"] = body

        try:
            poller = await self.email_client.begin_send(message)
            result = await poller.result()
            message_id = result.get("id")
            if message_id:
                logger.info("Email sent to %s with Message ID: %s", recipient, message_id)
                return {
                    "status": "success",
                    "message": "Email sent successfully",
                    "message_id": message_id,
                }
            logger.error("Failed to send email. Result: %s", result)
            return {"status": "error", "message": f"Failed to send email: {result}"}
        except ClientAuthenticationError as e:
            # Auth errors should not be retried - they need credential fixes
            logger.error("Authentication failed sending email to %s: %s", recipient, e)
            return {"status": "error", "message": f"Authentication failed: {e}"}
        except HttpResponseError as e:
            # Azure service errors (rate limits, invalid recipient, etc.)
            logger.error(
                "Azure service error sending email to %s: %s - %s",
                recipient,
                e.status_code,
                e.message,
            )
            return {
                "status": "error",
                "message": f"Azure service error ({e.status_code}): {e.message}",
            }
        except ServiceRequestError as e:
            # Network/connection errors - may be retryable
            logger.error("Network error sending email to %s: %s", recipient, e)
            return {"status": "error", "message": f"Network error: {e}"}
        except Exception as e:
            # Catch-all for unexpected errors
            logger.error("Unexpected error sending email to %s: %s", recipient, e)
            return {"status": "error", "message": f"Unexpected error: {e}"}
