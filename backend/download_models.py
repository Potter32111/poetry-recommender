import os
import urllib.request
import zipfile
import sys
import time

MODELS_DIR = "models_vosk"
MODELS = {
    "ru": "https://huggingface.co/rhasspy/vosk-models/resolve/main/ru/vosk-model-small-ru-0.22.zip",
    "en": "https://huggingface.co/rhasspy/vosk-models/resolve/main/en/vosk-model-small-en-us-0.15.zip",
}

def download_file(url, path):
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0'}
    )
    with urllib.request.urlopen(req, timeout=30) as response, open(path, 'wb') as out_file:
        total_length = int(response.getheader('content-length', 0))
        downloaded = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        start_time = time.time()
        
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)
            downloaded += len(chunk)
            
            elapsed = time.time() - start_time
            speed = downloaded / elapsed / (1024 * 1024) if elapsed > 0 else 0
            
            if total_length:
                percent = (downloaded / total_length) * 100
                sys.stdout.write(f"\r  Downloaded {downloaded/(1024*1024):.1f}MB of {total_length/(1024*1024):.1f}MB ({percent:.1f}%) at {speed:.1f} MB/s ")
            else:
                sys.stdout.write(f"\r  Downloaded {downloaded/(1024*1024):.1f}MB at {speed:.1f} MB/s ")
            sys.stdout.flush()
        print()

def main():
    os.makedirs(MODELS_DIR, exist_ok=True)
    for lang, url in MODELS.items():
        # Check if any folder starting with 'vosk-model-small-[lang]' exists
        lang_prefix = f"vosk-model-small-{lang}"
        existing = [d for d in os.listdir(MODELS_DIR) if d.startswith(lang_prefix) and os.path.isdir(os.path.join(MODELS_DIR, d))]
        
        if existing:
            print(f"=> Model for {lang} already exists ({existing[0]}), skipping.")
            continue

        zip_path = os.path.join(MODELS_DIR, f"{lang}.zip")
        print(f"\n=> Downloading {lang} model from {url}...")
        try:
            download_file(url, zip_path)
            print(f"=> Extracting {lang} model...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(MODELS_DIR)
            os.remove(zip_path)
        except Exception as e:
            print(f"\nFailed to download {lang} model: {e}")
            if os.path.exists(zip_path):
                os.remove(zip_path)
    print("\nModel setup complete!")

if __name__ == "__main__":
    main()
