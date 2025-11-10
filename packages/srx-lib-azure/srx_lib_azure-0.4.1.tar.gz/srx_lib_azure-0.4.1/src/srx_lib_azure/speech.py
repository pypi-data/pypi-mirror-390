import asyncio
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Callable, AsyncGenerator

from loguru import logger

# Optional import - gracefully handle if azure-cognitiveservices-speech is not installed
try:
    import azure.cognitiveservices.speech as speechsdk
    SPEECH_SDK_AVAILABLE = True
except ImportError:
    SPEECH_SDK_AVAILABLE = False
    logger.warning(
        "azure-cognitiveservices-speech not installed. "
        "Install with: pip install srx-lib-azure[speech]"
    )


class AzureSpeechService:
    """Azure Speech Service for audio transcription.

    Provides audio-to-text transcription using Azure Cognitive Services Speech SDK.
    Supports continuous recognition for longer audio files and language selection.

    Configuration can be passed explicitly via constructor or fallback to environment variables.
    Operations will error if SDK is not installed or required credentials are missing.
    """

    def __init__(
        self,
        *,
        speech_key: Optional[str] = None,
        speech_region: Optional[str] = None,
        speech_endpoint: Optional[str] = None,
        warn_if_unconfigured: bool = False,
    ) -> None:
        """Initialize Azure Speech Service.

        Args:
            speech_key: Azure Speech API key (falls back to AZURE_SPEECH_KEY env var)
            speech_region: Azure region (falls back to AZURE_SPEECH_REGION env var)
            speech_endpoint: Optional custom endpoint (falls back to AZURE_SPEECH_ENDPOINT env var)
            warn_if_unconfigured: Whether to warn at initialization if not configured
        """
        self.speech_key = speech_key or os.getenv("AZURE_SPEECH_KEY")
        self.speech_region = speech_region or os.getenv("AZURE_SPEECH_REGION")
        self.speech_endpoint = speech_endpoint or os.getenv("AZURE_SPEECH_ENDPOINT")

        if warn_if_unconfigured and not self.speech_key:
            logger.warning(
                "Azure Speech credentials not configured; transcription operations may fail."
            )

    def _check_availability(self) -> None:
        """Check if Speech SDK is available and credentials are configured."""
        if not SPEECH_SDK_AVAILABLE:
            raise RuntimeError(
                "azure-cognitiveservices-speech package not installed. "
                "Install with: pip install srx-lib-azure[speech]"
            )
        if not self.speech_key:
            raise RuntimeError(
                "Azure Speech credentials not configured. "
                "Provide speech_key or set AZURE_SPEECH_KEY environment variable."
            )
        if not self.speech_region and not self.speech_endpoint:
            raise RuntimeError(
                "Azure Speech region or endpoint not configured. "
                "Provide speech_region or speech_endpoint, or set AZURE_SPEECH_REGION environment variable."
            )

    def _preprocess_audio(self, input_path: str) -> str:
        """Convert audio to 16kHz mono WAV format for optimal Azure Speech processing.

        Args:
            input_path: Path to input audio file

        Returns:
            Path to preprocessed WAV file

        Raises:
            RuntimeError: If ffmpeg is not available or conversion fails
        """
        try:
            # Check if ffmpeg is available
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise RuntimeError(
                "ffmpeg not found. Please install ffmpeg for audio preprocessing."
            ) from e

        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
            output_path = tf.name

        try:
            # Convert to 16kHz mono WAV
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    input_path,
                    "-ar",
                    "16000",  # 16kHz sample rate
                    "-ac",
                    "1",  # Mono
                    "-y",  # Overwrite output file
                    output_path,
                ],
                capture_output=True,
                check=True,
            )
            logger.info(f"Preprocessed audio: {input_path} -> {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            # Clean up on error
            if os.path.exists(output_path):
                os.unlink(output_path)
            raise RuntimeError(f"Audio preprocessing failed: {e.stderr.decode()}") from e

    async def transcribe_audio_to_markdown(
        self,
        audio_path: str,
        language: str = "id-ID",
        preprocess: bool = True,
        on_recognizing: Optional[Callable[[str], None]] = None,
        on_recognized: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Transcribe audio file to markdown-formatted text.

        Args:
            audio_path: Path to audio file (mp3, m4a, wav, etc.)
            language: BCP-47 language code (default: 'id-ID' for Indonesian)
                     Common codes: 'en-US', 'id-ID', 'ms-MY', 'zh-CN', 'ja-JP'
            preprocess: Whether to preprocess audio to 16kHz mono WAV (recommended)
            on_recognizing: Optional callback for intermediate recognition results
            on_recognized: Optional callback for final recognition results

        Returns:
            Markdown-formatted transcription text

        Raises:
            RuntimeError: If SDK not available, credentials missing, or transcription fails
        """
        self._check_availability()

        # Preprocess audio if requested
        wav_path = audio_path
        cleanup_wav = False
        if preprocess:
            wav_path = self._preprocess_audio(audio_path)
            cleanup_wav = True

        try:
            # Configure Azure Speech
            if self.speech_endpoint:
                speech_config = speechsdk.SpeechConfig(
                    subscription=self.speech_key,
                    endpoint=self.speech_endpoint,
                )
            else:
                speech_config = speechsdk.SpeechConfig(
                    subscription=self.speech_key,
                    region=self.speech_region,
                )

            # Configure audio input
            audio_config = speechsdk.audio.AudioConfig(filename=wav_path)

            # Create speech recognizer with language
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config,
                language=language,
            )

            # Event-driven continuous recognition
            paragraphs: list[str] = []
            current: list[str] = []
            done = asyncio.get_event_loop().create_future()

            def recognizing_handler(evt):
                """Handle intermediate recognition results."""
                if evt.result.reason == speechsdk.ResultReason.RecognizingSpeech:
                    logger.debug(f"Recognizing: {evt.result.text}")
                    if on_recognizing:
                        on_recognizing(evt.result.text)

            def recognized_handler(evt):
                """Handle final recognition results."""
                if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    text = evt.result.text.strip()
                    if text:
                        current.append(text)
                        logger.debug(f"Recognized: {text}")
                        if on_recognized:
                            on_recognized(text)
                elif evt.result.reason == speechsdk.ResultReason.NoMatch:
                    logger.debug("No speech recognized")

            def session_stopped(evt):
                """Handle session stop."""
                logger.info("Session stopped")
                if current:
                    paragraphs.append(" ".join(current))
                if not done.done():
                    done.set_result(True)

            def canceled(evt):
                """Handle cancellation."""
                if evt.reason == speechsdk.CancellationReason.Error:
                    error_msg = f"Transcription error: {evt.error_details}"
                    logger.error(error_msg)
                    if not done.done():
                        done.set_exception(RuntimeError(error_msg))
                else:
                    logger.info("Transcription canceled")
                    if not done.done():
                        done.set_result(True)

            # Connect event handlers
            recognizer.recognizing.connect(recognizing_handler)
            recognizer.recognized.connect(recognized_handler)
            recognizer.session_stopped.connect(session_stopped)
            recognizer.canceled.connect(canceled)

            # Start continuous recognition
            logger.info(f"Starting transcription for {audio_path} (language: {language})")
            recognizer.start_continuous_recognition_async().get()

            # Wait for completion (max 15 minutes timeout)
            try:
                await asyncio.wait_for(done, timeout=900)
            except asyncio.TimeoutError:
                raise RuntimeError("Transcription timeout (15 minutes exceeded)")

            # Stop recognition
            recognizer.stop_continuous_recognition_async().get()

            # Format as markdown with bullet points
            if not paragraphs:
                logger.warning("No transcription results")
                return ""

            markdown = "\n\n".join(f"- {para}" for para in paragraphs)
            logger.info(f"Transcription completed: {len(paragraphs)} paragraphs")
            return markdown

        finally:
            # Clean up preprocessed WAV file
            if cleanup_wav and os.path.exists(wav_path):
                try:
                    os.unlink(wav_path)
                    logger.debug(f"Cleaned up temporary file: {wav_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up {wav_path}: {e}")

    async def transcribe_audio_bytes(
        self,
        audio_bytes: bytes,
        file_extension: str = ".mp3",
        language: str = "id-ID",
    ) -> str:
        """Transcribe audio from bytes to markdown-formatted text.

        Args:
            audio_bytes: Audio file content as bytes
            file_extension: File extension (for format detection)
            language: BCP-47 language code (default: 'id-ID' for Indonesian)

        Returns:
            Markdown-formatted transcription text

        Raises:
            RuntimeError: If SDK not available, credentials missing, or transcription fails
        """
        # Write bytes to temporary file
        with tempfile.NamedTemporaryFile(
            suffix=file_extension,
            delete=False,
        ) as tf:
            tf.write(audio_bytes)
            temp_path = tf.name

        try:
            return await self.transcribe_audio_to_markdown(
                temp_path,
                language=language,
                preprocess=True,
            )
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception as e:
                    logger.warning(f"Failed to clean up {temp_path}: {e}")

    async def transcribe_audio_streaming(
        self,
        audio_path: str,
        language: str = "id-ID",
        preprocess: bool = True,
    ) -> AsyncGenerator[dict, None]:
        """Transcribe audio file with real-time streaming of intermediate and final results.

        Args:
            audio_path: Path to audio file (mp3, m4a, wav, etc.)
            language: BCP-47 language code (default: 'id-ID' for Indonesian)
            preprocess: Whether to preprocess audio to 16kHz mono WAV (recommended)

        Yields:
            Dict with keys:
            - type: "recognizing" | "recognized" | "completed" | "error"
            - text: The transcribed text (for recognizing/recognized types)
            - markdown: Full markdown content (for completed type)
            - error: Error message (for error type)

        Raises:
            RuntimeError: If SDK not available, credentials missing, or transcription fails
        """
        self._check_availability()

        # Preprocess audio if requested
        wav_path = audio_path
        cleanup_wav = False
        if preprocess:
            wav_path = self._preprocess_audio(audio_path)
            cleanup_wav = True

        try:
            # Configure Azure Speech
            if self.speech_endpoint:
                speech_config = speechsdk.SpeechConfig(
                    subscription=self.speech_key,
                    endpoint=self.speech_endpoint,
                )
            else:
                speech_config = speechsdk.SpeechConfig(
                    subscription=self.speech_key,
                    region=self.speech_region,
                )

            # Configure audio input
            audio_config = speechsdk.audio.AudioConfig(filename=wav_path)

            # Create speech recognizer with language
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config,
                language=language,
            )

            # Event-driven continuous recognition with queue for streaming
            paragraphs: list[str] = []
            current: list[str] = []
            queue = asyncio.Queue()
            loop = asyncio.get_event_loop()
            done = loop.create_future()

            def recognizing_handler(evt):
                """Handle intermediate recognition results."""
                if evt.result.reason == speechsdk.ResultReason.RecognizingSpeech:
                    logger.debug(f"Recognizing: {evt.result.text}")
                    # Use call_soon_threadsafe to schedule from sync callback
                    loop.call_soon_threadsafe(
                        queue.put_nowait, {"type": "recognizing", "text": evt.result.text}
                    )

            def recognized_handler(evt):
                """Handle final recognition results."""
                if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    text = evt.result.text.strip()
                    if text:
                        current.append(text)
                        logger.debug(f"Recognized: {text}")
                        # Use call_soon_threadsafe to schedule from sync callback
                        loop.call_soon_threadsafe(
                            queue.put_nowait, {"type": "recognized", "text": text}
                        )
                elif evt.result.reason == speechsdk.ResultReason.NoMatch:
                    logger.debug("No speech recognized")

            def session_stopped(evt):
                """Handle session stop."""
                logger.info("Session stopped")
                if current:
                    paragraphs.append(" ".join(current))
                if not done.done():
                    loop.call_soon_threadsafe(done.set_result, True)

            def canceled(evt):
                """Handle cancellation."""
                if evt.reason == speechsdk.CancellationReason.Error:
                    error_msg = f"Transcription error: {evt.error_details}"
                    logger.error(error_msg)
                    # Use call_soon_threadsafe to schedule from sync callback
                    loop.call_soon_threadsafe(
                        queue.put_nowait, {"type": "error", "error": error_msg}
                    )
                    if not done.done():
                        loop.call_soon_threadsafe(done.set_exception, RuntimeError(error_msg))
                else:
                    logger.info("Transcription canceled")
                    if not done.done():
                        loop.call_soon_threadsafe(done.set_result, True)

            # Connect event handlers
            recognizer.recognizing.connect(recognizing_handler)
            recognizer.recognized.connect(recognized_handler)
            recognizer.session_stopped.connect(session_stopped)
            recognizer.canceled.connect(canceled)

            # Start continuous recognition
            logger.info(
                f"Starting streaming transcription for {audio_path} (language: {language})"
            )
            recognizer.start_continuous_recognition_async().get()

            # Stream results as they come in
            try:
                while not done.done():
                    try:
                        # Wait for next event with short timeout
                        event = await asyncio.wait_for(queue.get(), timeout=0.5)
                        yield event
                    except asyncio.TimeoutError:
                        continue

                # Wait for final completion
                await asyncio.wait_for(done, timeout=900)

                # Process any remaining events in queue
                while not queue.empty():
                    event = await queue.get()
                    yield event

            except asyncio.TimeoutError:
                yield {"type": "error", "error": "Transcription timeout (15 minutes exceeded)"}
                raise RuntimeError("Transcription timeout (15 minutes exceeded)")

            # Stop recognition
            recognizer.stop_continuous_recognition_async().get()

            # Format final markdown
            if paragraphs:
                markdown = "\n\n".join(f"- {para}" for para in paragraphs)
                logger.info(f"Streaming transcription completed: {len(paragraphs)} paragraphs")
                yield {"type": "completed", "markdown": markdown}
            else:
                logger.warning("No transcription results")
                yield {"type": "completed", "markdown": ""}

        finally:
            # Clean up preprocessed WAV file
            if cleanup_wav and os.path.exists(wav_path):
                try:
                    os.unlink(wav_path)
                    logger.debug(f"Cleaned up temporary file: {wav_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up {wav_path}: {e}")
