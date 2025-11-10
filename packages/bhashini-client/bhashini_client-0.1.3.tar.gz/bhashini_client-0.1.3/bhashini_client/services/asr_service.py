from typing import Optional


class ASRService:
    """Service for Automatic Speech Recognition (ASR) operations."""
    
    def __init__(self, handler):
        """Initialize ASR service with a request handler.
        
        Args:
            handler: Request handler instance for making API calls.
        """
        self.handler = handler

    def transcribe(self, audio_url: str, source_lang: str, serviceId: Optional[str] = None, samplingRate: Optional[int] = None):
        """Transcribe audio from a URL to text using ASR.
        
        Converts speech audio to text using the Bhashini ASR service. The audio
        file should be accessible via a public URL.
        
        Args:
            audio_url (str): Public URL of the audio file to transcribe.
            source_lang (str): Source language code (e.g., "hi", "en", "te", "gu").
                Supported language codes can be found in the Bhashini documentation.
            serviceId (Optional[str]): Custom service ID for ASR. If not provided,
                defaults to "bhashini/ai4bharat/conformer-multilingual-asr".
            samplingRate (Optional[int]): Audio sampling rate in Hz. If not provided,
                defaults to 16000. Common values: 16000, 44100, 48000.
        
        Returns:
            str: Transcribed text from the audio file. Returns empty string if
                transcription fails or no output is received.
        
        Example:
            >>> service = ASRService(handler)
            >>> text = service.transcribe(
            ...     "https://example.com/audio.wav",
            ...     "hi"
            ... )
            >>> # With custom parameters
            >>> text = service.transcribe(
            ...     "https://example.com/audio.wav",
            ...     "hi",
            ...     serviceId="custom-service-id",
            ...     samplingRate=44100
            ... )
        """
        serviceId = serviceId or "bhashini/ai4bharat/conformer-multilingual-asr"
        samplingRate = samplingRate or 16000
        
        payload = {
            "pipelineTasks": [
                {
                    "taskType": "asr",
                    "config": {
                        "language": {"sourceLanguage": source_lang},
                        "serviceId": serviceId,
                        "samplingRate": samplingRate
                    }
                }
            ],
            "inputData": {"audio": [{"audioUri": audio_url}]}
        }
        result = self.handler.post(payload)
        return result.get("pipelineResponse", [{}])[0].get("output", [{}])[0].get("source", "")

# type file 5 supported in audio, sampling rate, de-noiser, speaker diarization, punctuation, serviceID, transcription subtitle, hotword list - aplha | beta,  audio content,
