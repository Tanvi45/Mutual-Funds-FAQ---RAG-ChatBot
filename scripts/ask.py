from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rag.config import load_config


def main() -> None:
    load_config()
    print("ask not implemented")


if __name__ == "__main__":
    main()
