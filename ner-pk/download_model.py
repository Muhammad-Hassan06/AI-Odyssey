import time
import sys
from huggingface_hub import hf_hub_download

print("Resuming download of xlm-roberta-base model.safetensors...")
for attempt in range(1, 10):
    try:
        print(f"Attempt {attempt}...")
        path = hf_hub_download(
            repo_id="xlm-roberta-base",
            filename="model.safetensors",
            resume_download=True,
            etag_timeout=120
        )
        print("Success! Downloaded to:", path)
        sys.exit(0)
    except Exception as e:
        print(f"Attempt {attempt} failed with error: {e}")
        time.sleep(3)

print("Failed after all attempts.")
sys.exit(1)
