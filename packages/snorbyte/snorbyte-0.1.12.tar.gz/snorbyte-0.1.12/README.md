# snorbyte

Snorbyte TTS client with **streaming**, **PCM ring-buffer playback**, and **ffplay/ffmpeg required** for compressed live playback/encoding.

## DEPENDENCIES (VERY IMPORTANT)

We **require** both `ffplay` and `ffmpeg` to be available on your system **PATH**.
We also use `sounddevice` for PCM playback, which depends on **PortAudio** (OS package) on Linux.

### Windows

**Option A (winget)**
```powershell
winget install -e --id Gyan.FFmpeg
```

**Option B (chocolatey)**
```powershell
choco install ffmpeg
```

**Verify**

After install, ensure the ffmpeg/bin folder is on your PATH.
```powershell
ffmpeg -version
ffplay -version
```

### Linux

**Debian/Ubuntu**
```powershell
sudo apt-get update
sudo apt-get install -y ffmpeg libportaudio2
```

**Verify**
```powershell
ffmpeg -version
ffplay -version
```

## INSTALL PACKAGE
```powershell
pip install snorbyte
```

## API CALL USAGE
```python
from snorbyte import Snorbyte

def consume_stream(b: bytes):
    # b is raw stream bytes (PCM aligned for fmt="pcm", raw MP3/WAV chunks otherwise)
    print(f"chunk {len(b)} bytes")

client = Snorbyte(
    api_key="<YOUR-API-KEY>",
)

path, data, info = client.tts(
    utterance="दोस्त, दिल टूटा है तो क्या, रात भर प्लेलिस्ट रोएगी पर सुबह धूप आएगी, खुद से वादा कर—जो गया, जाने दे, जो आएगा, मुस्कुराकर अपनाएंगे।",
    speaker_id=233,
    speaker_name="",
    tone="Encouraging",
    speed=1.00,
    chunk_size=8192,
    denoise=True,
    stream=True,
    stream_bytes_callback=consume_stream,
    fmt="pcm",               # "mp3" | "wav" | "pcm"
    play=True,
    save_to="out.mp3",      # optional; auto-name if omitted
    temperature=0.0,
    top_p=1.0,
    repetition_penalty=1.05,
)

print("Saved to:", path)
print("Bytes in memory:", len(data) if data else None)
print("Info (ms):", info["latency_ms"])
```

## WEBSOCKET CALL USAGE
```python
from temp.snorbyte import Snorbyte   # e.g., "from snorbyte import Snorbyte"
import time

API_KEY    = "<YOUR-API-KEY>"


def consume_stream(b: bytes):
    print(f"chunk {len(b)} bytes")


def main():
    client = Snorbyte(
        api_key=API_KEY,
        ipv4_only=True,
    )

    client.ws_connect()

    try:
        path1, info1 = client.ws_send(
            utterance="ग्रुप प्रोजेक्ट में हर कोई अपना हिस्सा टाइम पर दे दे तो प्रेज़ेंटेशन शाइन करेगी, वरना आख़िरी रात को हड़बड़ी में स्लाइड्स बिगड़ जाती हैं, तो चलो एक शेड्यूल फिक्स करते हैं और डेडलाइन से पहले एक ड्राई-रन करके फीडबैक फ्रीज़ कर देते हैं।",
            speaker_id=228,
            tone="Encouraging",
            speed=1.00,
            denoise=False,
            fmt="pcm",               
            save_to="demo_out_1.wav",
            stream_bytes_callback=consume_stream,
            play=True,               
        )
        print("[WS] saved:", path1)
        print("[WS] metrics:", info1.get("latency_ms", {}))

        path1, info1 = client.ws_send(
            utterance="ठीक है, फिर शाम को रिपोर्ट भेज दूँगा; आप बस मेट्रिक्स देख लेना और अपना फीडबैक बता देना।",
            speaker_id=49,
            tone="",                 # or "Encouraging"/"Consoling" for Charan/Shreeja only
            speed=1.00,
            denoise=True,
            fmt="pcm",               
            save_to="demo_out_1.mp3",
            stream_bytes_callback=consume_stream,
            play=True,               
            timeout=30,
        )
        print("[WS] saved:", path1)
        print("[WS] metrics:", info1.get("latency_ms", {}))

        path1, info1 = client.ws_send(
            utterance="देख भाई, धीरे-धीरे कर ना, फालतू टेंशन मत ले, जो काम समय से हो सकता है, उसे जबरदस्ती धक्का देकर बिगाड़ने से अच्छा है, आराम से कर, रोज़ थोड़ा-थोड़ा बढ़ेगा।",
            speaker_id=67,
            tone="",                 # or "Encouraging"/"Consoling" for Charan/Shreeja only
            speed=1.00,
            denoise=False,
            fmt="pcm",               
            save_to="demo_out_1.wav",
            stream_bytes_callback=consume_stream,
            play=False,               
            timeout=30,
        )
        print("[WS] saved:", path1)
        print("[WS] metrics:", info1.get("latency_ms", {}))



    finally:
        time.sleep(2)
        client.ws_close()
        client.close()
        print("[WS] closed")

if __name__ == "__main__":
    main()
```

