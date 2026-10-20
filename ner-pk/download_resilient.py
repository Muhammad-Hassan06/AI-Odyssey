import os
import sys
import requests
import time

URL = "https://huggingface.co/xlm-roberta-base/resolve/main/model.safetensors"
# Destination in HF cache blobs
BLOBS_DIR = os.path.expanduser(r"~/.cache/huggingface/hub/models--xlm-roberta-base/blobs")
SNAPSHOT_DIR = os.path.expanduser(r"~/.cache/huggingface/hub/models--xlm-roberta-base/snapshots/e73636d4f797dec63c3081bb6ed5c7b0bb3f2089")
TARGET_HASH = "6fd4797bc397c3b8b55d6bb5740366b57e6a3ce91c04c77f22aafc0c128e6feb"

target_blob = os.path.join(BLOBS_DIR, TARGET_HASH)
incomplete_blob = target_blob + ".incomplete"
snapshot_file = os.path.join(SNAPSHOT_DIR, "model.safetensors")

if os.path.exists(target_blob) and os.path.getsize(target_blob) == 1115567652:
    print(f"Already complete: {target_blob}")
    sys.exit(0)

os.makedirs(BLOBS_DIR, exist_ok=True)
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

EXPECTED_SIZE = 1115567652
CHUNK_SIZE = 2 * 1024 * 1024  # 2MB

print(f"Target file: {incomplete_blob}")
print(f"Expected size: {EXPECTED_SIZE} bytes ({EXPECTED_SIZE / 1e6:.1f} MB)")

retries = 0
max_retries = 30

while retries < max_retries:
    curr_size = os.path.getsize(incomplete_blob) if os.path.exists(incomplete_blob) else 0
    print(f"Current progress: {curr_size} / {EXPECTED_SIZE} bytes ({curr_size / EXPECTED_SIZE * 100:.2f}%)")
    
    if curr_size >= EXPECTED_SIZE:
        print("Download complete!")
        if os.path.exists(target_blob):
            os.remove(target_blob)
        os.rename(incomplete_blob, target_blob)
        # On windows, copy to snapshot if symlink not permitted
        import shutil
        print(f"Copying to snapshot {snapshot_file}...")
        shutil.copyfile(target_blob, snapshot_file)
        print("All done!")
        sys.exit(0)
        
    headers = {"Range": f"bytes={curr_size}-"}
    try:
        with requests.get(URL, headers=headers, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(incomplete_blob, "ab") as f:
                last_log = time.time()
                for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        curr_size += len(chunk)
                        if time.time() - last_log > 5:
                            print(f"Progress: {curr_size / EXPECTED_SIZE * 100:.1f}% ({curr_size / 1e6:.1f} MB)")
                            last_log = time.time()
    except Exception as e:
        print(f"Interrupted: {e}. Retrying in 3s...")
        retries += 1
        time.sleep(3)

print("Exceeded max retries.")
sys.exit(1)
