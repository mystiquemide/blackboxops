from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.demo_agent import run_demo_incident
from app.postmortem import generate_postmortem

if __name__ == "__main__":
    replay = run_demo_incident()
    postmortem = generate_postmortem(replay)
    print(postmortem.markdown)
