import shutil
from pathlib import Path

# Define source and destination directories
repo_root = Path(__file__).resolve().parent.parent
destination_dir = repo_root / "src" / "netzero_metrics_reference_data" / "data"

# Ensure destination directory exists
destination_dir.mkdir(parents=True, exist_ok=True)

# List of file extensions to copy
extensions = [".csv", ".json", ".yaml", ".txt"]

# Copy matching files from repo root to destination
for file_path in repo_root.iterdir():
    if file_path.is_file() and any(file_path.name.endswith(ext) for ext in extensions):
        dst_path = destination_dir / file_path.name
        shutil.copy2(file_path, dst_path)
