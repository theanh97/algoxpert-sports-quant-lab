import json

from sports_quant_lab.data.pipeline import load_and_audit


def test_data_pipeline_filters_knockouts_and_maps_teams(tmp_path):
    games = [
        {
            "game_id": "g1",
            "date_time_utc": "2020-01-01 20:00:00 UTC",
            "last_updated_utc": "2020-01-02 00:00:00 UTC",
            "home_score": 2,
            "away_score": 1,
            "home_team_id": "h",
            "away_team_id": "a",
            "season_name": "2020",
            "status": "FullTime",
            "knockout_game": False,
        },
        {
            "game_id": "g2",
            "date_time_utc": "2020-11-01 20:00:00 UTC",
            "last_updated_utc": "2020-11-02 00:00:00 UTC",
            "home_score": 0,
            "away_score": 0,
            "home_team_id": "h",
            "away_team_id": "a",
            "season_name": "2020",
            "status": "FullTime",
            "knockout_game": True,
        },
    ]
    teams = [
        {"team_id": "h", "team_name": "Home FC"},
        {"team_id": "a", "team_name": "Away FC"},
    ]
    game_path = tmp_path / "asa_mls_games_2026-11-26.json"
    team_path = tmp_path / "asa_mls_teams_2026-11-26.json"
    game_path.write_text(json.dumps(games), encoding="utf-8")
    team_path.write_text(json.dumps(teams), encoding="utf-8")

    matches, audit = load_and_audit(game_path, team_path)
    assert len(matches) == 1
    assert matches.iloc[0].home_team == "Home FC"
    assert matches.iloc[0].outcome == "H"
    assert audit["raw_rows"] == 2
    assert audit["regular_season_rows"] == 1
    assert audit["knockout_rows_in_full_time_snapshot"] == 1
    assert audit["unmapped_team_ids"] == []

