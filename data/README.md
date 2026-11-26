# MLS source snapshot

The raw files in this folder were retrieved from the American Soccer Analysis
(ASA) public API on 2026-11-26. The API states that its returned data is licensed
under Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).
Attribute American Soccer Analysis and keep redistributed data and adaptations
under the same license. The source license applies to the data, not to the
project's MIT-licensed code.

- Matches: `raw/asa_mls_games_2026-11-26.json` from
  `https://app.americansocceranalysis.com/api/v1/mls/games?status=FullTime`
- Team names: `raw/asa_mls_teams_2026-11-26.json` from
  `https://app.americansocceranalysis.com/api/v1/mls/teams`
- API documentation and license statement:
  `https://app.americansocceranalysis.com/api/v1/openapi.json`
- Snapshot SHA-256 values and audit counts: `artifacts/data_audit.json`

The fixture snapshot contains 5,998 completed matches across MLS seasons
2013–2026, including 266 matches flagged as knockout games. The primary
experiment excludes knockout games and uses 5,732 regular-season matches.
Coverage is the API's coverage, not a claim of complete league records. ASA's
`last_updated_utc` values are retained for audit, but the API does not provide
historical point-in-time versions of records or pre-match market timestamps.

Football-Data is not used in this project: its current data page restricts the
free files to private individuals and excludes commercial use and automated
data-training products. No market-odds benchmark is therefore claimed.

