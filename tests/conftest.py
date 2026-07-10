"""Put src/ on the path so both the atap package and the flat extended modules import."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
