"""Command line entry points."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from sports_quant_lab.constants import ARTIFACTS_DIR, ROOT
from sports_quant_lab.data.pipeline import fetch_snapshot, latest_snapshot, load_and_audit
from sports_quant_lab.research import run_research


def main() -> None:
    parser = argparse.ArgumentParser(prog="sports-quant", description="AlgoXpert Sports Quant Lab")
    subparsers = parser.add_subparsers(dest="command", required=True)
    fetch = subparsers.add_parser("fetch", help="Download an ASA match and team snapshot")
    fetch.add_argument("--league", default="mls", help="ASA API league slug, default: mls")
    fetch.add_argument("--snapshot-date", help="Filename date (YYYY-MM-DD); defaults to today UTC")
    run = subparsers.add_parser("run", help="Run the walk-forward research and build report artifacts")
    run.add_argument("--games", help="Optional local match JSON path")
    run.add_argument("--teams", help="Optional local team JSON path")
    run.add_argument("--eval-start-season", type=int, default=2019)
    audit = subparsers.add_parser("audit", help="Normalize a local snapshot and print source/data audit")
    audit.add_argument("--games", help="Optional local match JSON path")
    audit.add_argument("--teams", help="Optional local team JSON path")
    dashboard = subparsers.add_parser("dashboard", help="Start the local Streamlit dashboard")
    dashboard.add_argument("--port", type=int, default=8501)
    args = parser.parse_args()

    if args.command == "fetch":
        game_path, team_path = fetch_snapshot(args.league, args.snapshot_date)
        print(f"Saved {game_path}\nSaved {team_path}")
    elif args.command == "run":
        games = Path(args.games) if args.games else None
        teams = Path(args.teams) if args.teams else None
        result = run_research(games, teams, args.eval_start_season)
        print(result["metrics"].to_string(index=False))
        print(f"\nVerification: {result['audit']['verification']['status']}")
        print(f"Artifacts: {ARTIFACTS_DIR}")
    elif args.command == "audit":
        if args.games and args.teams:
            games, teams = Path(args.games), Path(args.teams)
        else:
            games, teams = latest_snapshot()
        matches, result = load_and_audit(games, teams)
        result["normalized_regular_season_rows"] = len(matches)
        print(json.dumps(result, indent=2, default=str))
    elif args.command == "dashboard":
        command = [sys.executable, "-m", "streamlit", "run", str(ROOT / "dashboard.py"), "--server.port", str(args.port)]
        subprocess.run(command, cwd=ROOT, check=False)


if __name__ == "__main__":
    main()
