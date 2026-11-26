from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
ARTIFACTS_DIR = ROOT / "artifacts"
FIGURES_DIR = ARTIFACTS_DIR / "figures"
REPORTS_DIR = ARTIFACTS_DIR / "reports"
OUTCOMES = ("H", "D", "A")
OUTCOME_LABELS = {"H": "Home win", "D": "Draw", "A": "Away win"}
ASA_API = "https://app.americansocceranalysis.com/api/v1"

