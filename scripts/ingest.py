from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rag.config import ensure_stage_dirs, load_config
from rag.loader import load_documents, scrape_documents


def main() -> None:
    parser = argparse.ArgumentParser(description="MF FAQ ingest")
    parser.add_argument("--until", default="load", choices=["scrape", "load"])
    parser.add_argument("--config", default=str(ROOT / "config.yaml"))
    args = parser.parse_args()

    cfg = load_config(args.config)
    ensure_stage_dirs(cfg)

    if args.until == "scrape":
        docs = scrape_documents(cfg)
        print(f"scraped {len(docs)} allowlisted page(s)")
        for doc in docs:
            print(f"  {doc['doc_id']}: {doc['url']}")
        return

    if args.until == "load":
        index = ROOT / cfg.get("paths", {}).get("stages", "data/stages") / "02_clean" / "docs.jsonl"
        if not index.exists():
            print("no scraped files yet; scraping allowlisted URLs first")
            scrape_documents(cfg)
        docs = load_documents(cfg)
        print(f"loaded {len(docs)} document(s) from disk")
        for doc in docs:
            print(f"  {doc['doc_id']}: {len(doc['text'])} chars | {doc['url']}")
        return

    print("ingest step not implemented")


if __name__ == "__main__":
    main()
