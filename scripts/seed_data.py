from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    (ROOT / "data" / "blackbox_events.jsonl").write_text("", encoding="utf-8")
    print("Seed files are already included in data/. Event store reset.")
