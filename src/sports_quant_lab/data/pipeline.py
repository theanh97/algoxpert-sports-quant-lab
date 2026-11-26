"""Fetch, normalize, and audit ASA match data without hiding source limits."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

from sports_quant_lab.constants import ASA_API, RAW_DIR


def fetch_snapshot(league: str = "mls", snapshot_date: str | None = None) -> tuple[Path, Path]:
    """Download public ASA match and team snapshots into data/raw."""
    day = snapshot_date or pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    urls = (
        (f"{ASA_API}/{league}/games?status=FullTime", RAW_DIR / f"asa_{league}_games_{day}.json"),
        (f"{ASA_API}/{league}/teams", RAW_DIR / f"asa_{league}_teams_{day}.json"),
    )
    paths: list[Path] = []
    for url, path in urls:
        request = Request(url, headers={"User-Agent": "AlgoXpert-Sports-Quant-Lab/1.0"})
        with urlopen(request, timeout=60) as response:
            path.write_bytes(response.read())
        paths.append(path)
    return paths[0], paths[1]


def latest_snapshot(league: str = "mls") -> tuple[Path, Path]:
    """Return the most recent dated local snapshot pair."""
    games = sorted(RAW_DIR.glob(f"asa_{league}_games_*.json"))
    teams = sorted(RAW_DIR.glob(f"asa_{league}_teams_*.json"))
    if not games or not teams:
        raise FileNotFoundError("No ASA snapshot found; run `sports-quant fetch` first.")
    game_path = games[-1]
    date_key = game_path.stem.rsplit("_", 1)[-1]
    team_path = RAW_DIR / f"asa_{league}_teams_{date_key}.json"
    if not team_path.exists():
        team_path = teams[-1]
    return game_path, team_path


def _read_json(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig") as file:
        result = json.load(file)
    if not isinstance(result, list):
        raise TypeError(f"Expected a JSON array in {path}")
    return result


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_and_audit(games_path: Path, teams_path: Path) -> tuple[pd.DataFrame, dict]:
    """Normalize match rows and return machine-readable source/quality evidence."""
    raw = _read_json(games_path)
    team_rows = _read_json(teams_path)
    names = {str(row["team_id"]): row["team_name"] for row in team_rows}
    rows = pd.DataFrame(raw)
    required = {
        "game_id", "date_time_utc", "home_score", "away_score", "home_team_id",
        "away_team_id", "season_name", "status",
    }
    missing_columns = sorted(required - set(rows.columns))
    if missing_columns:
        raise ValueError(f"ASA response is missing required fields: {missing_columns}")

    raw_count = len(rows)
    status_counts = rows["status"].fillna("<missing>").value_counts().to_dict()
    missing_scores = int(rows[["home_score", "away_score"]].isna().any(axis=1).sum())
    missing_date = int(rows["date_time_utc"].isna().sum())
    duplicate_count = int(rows.duplicated("game_id", keep="last").sum())
    rows = rows.sort_values("last_updated_utc" if "last_updated_utc" in rows else "date_time_utc")
    rows = rows.drop_duplicates("game_id", keep="last").copy()
    rows["date_time_utc"] = pd.to_datetime(rows["date_time_utc"], utc=True, errors="coerce")
    if "last_updated_utc" in rows:
        rows["last_updated_utc"] = pd.to_datetime(
            rows["last_updated_utc"], utc=True, errors="coerce"
        )
    else:
        rows["last_updated_utc"] = pd.NaT
    rows["season"] = pd.to_numeric(rows["season_name"], errors="coerce").astype("Int64")
    rows["home_score"] = pd.to_numeric(rows["home_score"], errors="coerce")
    rows["away_score"] = pd.to_numeric(rows["away_score"], errors="coerce")
    rows["knockout_game"] = rows.get("knockout_game", False)
    rows["knockout_game"] = rows["knockout_game"].fillna(False).astype(bool)
    rows["home_team_id"] = rows["home_team_id"].astype(str)
    rows["away_team_id"] = rows["away_team_id"].astype(str)
    rows["home_team"] = rows["home_team_id"].map(names)
    rows["away_team"] = rows["away_team_id"].map(names)
    unknown_team_ids = sorted(
        set(rows.loc[rows.home_team.isna(), "home_team_id"])
        | set(rows.loc[rows.away_team.isna(), "away_team_id"])
    )
    rows["home_team"] = rows["home_team"].fillna(rows["home_team_id"])
    rows["away_team"] = rows["away_team"].fillna(rows["away_team_id"])
    rows = rows.loc[
        (rows.status == "FullTime")
        & rows.home_score.notna()
        & rows.away_score.notna()
        & rows.date_time_utc.notna()
        & rows.season.notna()
        & rows.home_team_id.ne(rows.away_team_id)
    ].copy()
    rows["season"] = rows["season"].astype(int)
    rows["home_score"] = rows["home_score"].astype(int)
    rows["away_score"] = rows["away_score"].astype(int)
    rows["outcome"] = "D"
    rows.loc[rows.home_score > rows.away_score, "outcome"] = "H"
    rows.loc[rows.home_score < rows.away_score, "outcome"] = "A"
    rows["match_date_utc"] = rows["date_time_utc"].dt.date.astype(str)
    rows = rows.sort_values(["date_time_utc", "game_id"]).reset_index(drop=True)

    coverage = (
        rows.assign(match_type=np.where(rows.knockout_game, "Knockout", "Regular season"))
        .groupby(["season", "match_type"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    coverage_by_season = [
        {str(key): int(value) if pd.notna(value) else 0 for key, value in row.items()}
        for row in coverage.to_dict(orient="records")
    ]
    regular = rows.loc[~rows.knockout_game].copy().reset_index(drop=True)
    team_ids = set(regular.home_team_id) | set(regular.away_team_id)
    seasons = sorted(regular.season.unique().tolist())
    audit = {
        "source": "American Soccer Analysis public API",
        "source_license": "CC BY-SA 4.0",
        "retrieved_utc": games_path.stem.rsplit("_", 1)[-1],
        "games_endpoint": f"{ASA_API}/mls/games?status=FullTime",
        "teams_endpoint": f"{ASA_API}/mls/teams",
        "games_file": str(games_path).replace("\\", "/"),
        "teams_file": str(teams_path).replace("\\", "/"),
        "games_sha256": sha256(games_path),
        "teams_sha256": sha256(teams_path),
        "raw_rows": raw_count,
        "status_counts": {str(k): int(v) for k, v in status_counts.items()},
        "duplicate_game_ids_removed": duplicate_count,
        "missing_score_rows_in_raw": missing_scores,
        "missing_date_rows_in_raw": missing_date,
        "knockout_rows_in_full_time_snapshot": int(rows.knockout_game.sum()),
        "regular_season_rows": len(regular),
        "unique_regular_season_game_ids": int(regular.game_id.nunique()),
        "seasons": seasons,
        "first_match_utc": regular.date_time_utc.min().isoformat() if len(regular) else None,
        "last_match_utc": regular.date_time_utc.max().isoformat() if len(regular) else None,
        "unique_team_ids": len(team_ids),
        "unmapped_team_ids": unknown_team_ids,
        "outcome_counts": {k: int(v) for k, v in regular.outcome.value_counts().items()},
        "coverage_by_season": coverage_by_season,
        "goal_range_home": [int(regular.home_score.min()), int(regular.home_score.max())],
        "goal_range_away": [int(regular.away_score.min()), int(regular.away_score.max())],
        "point_in_time_revision_limit": (
            "API exposes last_updated_utc but no historical record versions; this snapshot cannot "
            "prove what a consumer knew at every historical cutoff."
        ),
    }
    return regular, audit

