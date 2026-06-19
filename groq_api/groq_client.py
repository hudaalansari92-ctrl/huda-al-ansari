import logging
from typing import Optional

logger = logging.getLogger(__name__)


class GroqClient:
    """
    Groq API Client — manages connection and chat calls
    Fallback: returns None if API is unavailable
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model = model
        self._client = None
        self._available = False

        if api_key:
            self._init_client()

    def _init_client(self):
        """Initialize Groq client"""
        try:
            from groq import Groq
            self._client = Groq(api_key=self.api_key)
            self._available = True
            logger.info("Groq client initialized successfully")
        except ImportError:
            logger.warning("groq package not installed. Run: pip install groq")
            self._available = False
        except Exception as e:
            logger.warning(f"Failed to initialize Groq client: {e}")
            self._available = False

    def set_api_key(self, api_key: str):
        """Update API key and reinitialize"""
        self.api_key = api_key
        self._init_client()

    @property
    def is_available(self) -> bool:
        return self._available and self._client is not None

    def chat(self, system_prompt: str, user_message: str,
             temperature: float = 0.3, max_tokens: int = 1024) -> Optional[str]:
        """
        Send a chat request to Groq API

        Args:
            system_prompt: System instructions
            user_message: User/data message
            temperature: Creativity (0.0-1.0), low = more precise
            max_tokens: Max response length

        Returns:
            Response text or None if failed
        """
        if not self.is_available:
            logger.warning("Groq client not available, skipping API call")
            return None

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            result = response.choices[0].message.content
            logger.info(f"Groq API response received ({len(result)} chars)")
            return result

        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            return None

    def transcribe(self, audio_file, language: str = 'ar') -> Optional[str]:
        """
        Transcribe audio using Groq Whisper API

        Args:
            audio_file: Audio file-like object (e.g. from st.audio_input)
            language: Language code ('ar' or 'en')

        Returns:
            Transcribed text or None if failed
        """
        if not self.is_available:
            logger.warning("Groq client not available for transcription")
            return None

        try:
            lang_code = 'ar' if language == 'ar' else 'en'
            transcription = self._client.audio.transcriptions.create(
                file=("audio.webm", audio_file.read()),
                model="whisper-large-v3-turbo",
                language=lang_code
            )
            result = transcription.text
            logger.info(f"Transcription successful ({len(result)} chars)")
            return result
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None
