import os
import requests
import zipfile
from pathlib import Path

DATA_URL = "https://github.com/VaibhavVetal2211/DL_practical/archive/refs/heads/main.zip"
DEST_DIR = Path.home() / ".pyytorch_data"

def download_data():
    """Download and extract the dataset zip to DEST_DIR.

    This function is idempotent: if the destination folder already
    contains the extracted directory we skip re-downloading.
    """
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = DEST_DIR / "pyytorch.zip"

    # If an expected marker exists (extracted folder), skip download.
    # The upstream zip extracts to a folder named 'DL_practical-main'.
    extracted_marker = DEST_DIR / "DL_practical-main"
    if extracted_marker.exists():
        print(f"✅ Data already present at: {extracted_marker} — skipping download")
        return

    r = requests.get(DATA_URL, stream=True, timeout=30)
    try:
        r.raise_for_status()
    except Exception as e:
        # remove partial file if any and re-raise
        if zip_path.exists():
            try:
                zip_path.unlink()
            except Exception:
                pass
        raise

    with open(zip_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if not chunk:
                continue
            f.write(chunk)

    # extract and remove the zip
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(DEST_DIR)
    try:
        os.remove(zip_path)
    except OSError:
        pass

    print(f"✅ Data downloaded to: {DEST_DIR}")
