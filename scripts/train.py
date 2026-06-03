import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.adapters.ml.training import train_and_save
from app.infrastructure.config import Settings


def main() -> None:
    settings = Settings()
    metrics = train_and_save(settings.dataset_path, settings.artifacts_dir)
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
