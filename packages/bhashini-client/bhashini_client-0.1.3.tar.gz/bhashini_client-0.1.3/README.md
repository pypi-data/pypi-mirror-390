# bhashini-client

A simple Python client library for interacting with [Bhashini](https://bhashini.gov.in/) inference APIs.  
Currently supports:
- **ASR** (Automatic Speech Recognition)
- **NMT** (Machine Translation)
- **TTS** (Text-to-Speech)

---

## 🚀 Installation

```bash
pip install bhashini-client
```

## Example Usage
```bash
from bhashini_client import BhashiniClient
client = BhashiniClient(api_key="api-key")
print(client.asr("audio url", "source Language"))
print(client.nmt("input text", "source Language", "Target Language"))
