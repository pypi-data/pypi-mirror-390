from typing import Optional


class NMTService:
    """Service for Neural Machine Translation (NMT) operations."""
    
    def __init__(self, handler):
        """Initialize NMT service with a request handler.
        
        Args:
            handler: Request handler instance for making API calls.
        """
        self.handler = handler

    def translate(self, text: str, source_lang: str, target_lang: str, serviceId: Optional[str] = None, numTranslation: Optional[str] = None):
        """Translate text from source language to target language.
        
        Translates text using the Bhashini Neural Machine Translation service.
        Supports translation between multiple Indian languages and English.
        
        Args:
            text (str): Text to be translated.
            source_lang (str): Source language code (e.g., "hi", "en", "te", "gu").
                Supported language codes can be found in the Bhashini documentation.
            target_lang (str): Target language code (e.g., "hi", "en", "te", "gu").
                Supported language codes can be found in the Bhashini documentation.
            serviceId (Optional[str]): Custom service ID for translation. If not provided,
                defaults to "ai4bharat/indictrans-v2-all-gpu--t4".
            numTranslation (Optional[str]): Enable number translation. Accepts "True" or "False"
                as string values. If not provided, defaults to "True". When enabled,
                numbers in the text are translated to the target language format.
        
        Returns:
            str: Translated text in the target language. Returns empty string if
                translation fails or no output is received.
        
        Example:
            >>> service = NMTService(handler)
            >>> translated = service.translate(
            ...     "Hello, how are you?",
            ...     "en",
            ...     "hi"
            ... )
            >>> # With custom parameters
            >>> translated = service.translate(
            ...     "Hello, how are you?",
            ...     "en",
            ...     "hi",
            ...     serviceId="custom-service-id",
            ...     numTranslation="False"
            ... )
        """
        serviceId = serviceId or "ai4bharat/indictrans-v2-all-gpu--t4"
        numTranslation = numTranslation or "True"
        
        config = {
            "language": {
                "sourceLanguage": source_lang,
                "targetLanguage": target_lang
            },
            "serviceId": serviceId,
            "numTranslation": numTranslation
        }
        
        payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": config
                }
            ],
            "inputData": {"input": [{"source": text}]}
        }
        result = self.handler.post(payload)
        return result.get("pipelineResponse", [{}])[0].get("output", [{}])[0].get("target", "")


## add service id, glossary, profinnity filter, , num trnaslation