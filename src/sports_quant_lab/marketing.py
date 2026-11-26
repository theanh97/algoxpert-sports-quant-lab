"""Generate portfolio copy from real experiment outputs."""

from __future__ import annotations

from sports_quant_lab.constants import ROOT


def generate_marketing_assets(metrics, by_season, audit) -> None:
    content = ROOT / "content"
    website = ROOT / "website"
    content.mkdir(parents=True, exist_ok=True)
    website.mkdir(parents=True, exist_ok=True)
    best = metrics.sort_values("log_loss").iloc[0]
    seasons = ", ".join(map(str, audit["evaluation"]["test_seasons"]))
    method = str(best.display_name)
    n = int(best.n_matches)
    fitted = metrics.loc[metrics.model != "league_prior"]
    worse_count = int((fitted.log_loss > best.log_loss).sum())
    clearly_worse = fitted.loc[fitted.bootstrap_delta_log_loss_ci95_low > 0, "display_name"].tolist()
    clear_note = (
        f"All {worse_count} fitted variants had higher aggregate log loss than the league prior. "
        + ("Paired 95% intervals exclude zero for " + ", ".join(clearly_worse) + ". " if clearly_worse else "No paired interval excluded zero. ")
    )
    summary_en = (
        f"{method} recorded the lowest aggregate held-out log loss in this run: {best.log_loss:.4f} "
        f"over {n:,} matches in test seasons {seasons}. Its paired match-bootstrap difference "
        f"versus the league-prior baseline was {best.bootstrap_delta_log_loss_vs_prior:+.4f} "
        f"(95% interval {best.bootstrap_delta_log_loss_ci95_low:+.4f} to "
        f"{best.bootstrap_delta_log_loss_ci95_high:+.4f}). {clear_note} This is a historical sample result, "
        "not a claim of durable future edge, market outperformance, or betting profitability."
    )
    summary_vi = (
        f"{method} có log loss tổng hợp thấp nhất trong mẫu kiểm định của lần chạy này: "
        f"{best.log_loss:.4f} trên {n:,} trận ở các mùa {seasons}. Chênh lệch bootstrap ghép cặp "
        f"so với baseline tần suất giải là {best.bootstrap_delta_log_loss_vs_prior:+.4f} "
        f"(khoảng 95%: {best.bootstrap_delta_log_loss_ci95_low:+.4f} đến "
        f"{best.bootstrap_delta_log_loss_ci95_high:+.4f}). Cả {worse_count} biến thể đã fit đều có "
        "log loss tổng hợp cao hơn baseline. Đây là kết quả trong mẫu lịch sử, "
        "không phải cam kết lợi thế tương lai, vượt trội thị trường hay lợi nhuận cá cược."
    )

    posts = {
        "LinkedIn_EN.md": f"""# LinkedIn post (EN)

A prediction model is only interesting when its probabilities survive a time-respecting test.

{summary_en}

AlgoXpert Sports Quant Lab is an MLS research release built on {audit['regular_season_rows']:,} regular-season results from American Soccer Analysis (2013-2026 source coverage). It compares a league prior, Elo, team-identity logistic regression, and a Dixon-Coles goal model. Temperature scaling uses prior-season out-of-fold forecasts. The run checks temporal cutoffs, game-ID separation, probability bounds, and calibration.

The source snapshot has results but no timestamped market prices. The API also lacks archived point-in-time revisions. I make no market-edge, ROI, or arbitrage claim.

Code, audit, dashboard, notebook, reports, and charts: [repository link to add after publication].

#SportsAnalytics #QuantResearch #ProbabilityCalibration #MLS
""",
        "LinkedIn_VI.md": f"""# Bài LinkedIn (VI)

Một mô hình dự đoán chỉ đáng tin khi xác suất vượt qua phép kiểm định tôn trọng thời gian.

{summary_vi}

AlgoXpert Sports Quant Lab là nghiên cứu MLS có thể tái lập, dùng {audit['regular_season_rows']:,} kết quả mùa thường từ American Soccer Analysis (phạm vi 2013-2026). Benchmark gồm baseline tần suất, Elo, logistic theo đội và Dixon-Coles. Temperature scaling dùng dự báo out-of-fold của các mùa trước; quy trình kiểm tra mốc thời gian, mã trận, miền xác suất và calibration.

Snapshot không có giá thị trường kèm timestamp; API cũng không có phiên bản lịch sử tại từng thời điểm. Không tuyên bố lợi thế thị trường, ROI hay arbitrage.

Mã nguồn, audit, dashboard, notebook, report và biểu đồ: [bổ sung liên kết repo sau khi xuất bản].

#SportsAnalytics #QuantResearch #MLS #ProbabilityCalibration
""",
    }
    for filename, text in posts.items():
        (content / filename).write_text(text, encoding="utf-8")

    medium_en = f"""# A reproducible MLS forecasting benchmark starts with probability

Sports forecasting demos often lead with a hit rate. That number is easy to read, but it does not show whether a model's 70% forecasts happen about 70% of the time or whether future information leaked into testing.

AlgoXpert Sports Quant Lab makes those checks part of the research release.

## Data and boundaries

The case study uses {audit['regular_season_rows']:,} MLS regular-season results from American Soccer Analysis, with source coverage from 2013 through 2026. The API states that returned data are CC BY-SA 4.0, so the repository includes attribution and preserves share-alike for the data. The primary experiment excludes {audit['knockout_rows_in_full_time_snapshot']:,} records flagged as knockout games.

The snapshot contains scores and team identifiers, but no timestamped pre-match odds. Football-Data is not substituted: its current free-data terms restrict use to private individuals and exclude commercial use and automated data-training products. There is no market benchmark or betting-return claim.

## A time-respecting comparison

Each test season is held out as a whole. Models train only on earlier seasons: a league-frequency prior, Elo ratings, regularized team-identity logistic regression, and a Dixon-Coles goal model. Temperature scaling is fit on temporal out-of-fold forecasts from prior seasons. We report log loss, multiclass Brier score, ranked probability score, accuracy, calibration diagnostics, and paired bootstrap intervals against the league prior.

## What this run found

{summary_en}

That is a sample result, not a forecast of future performance. Per-season charts and calibration plots make variation visible alongside the aggregate score.

## What remains uncertain

ASA exposes `last_updated_utc` but no archived point-in-time versions. The split proves only earlier-season rows enter each fold; it cannot prove every historical record was unchanged at the original cutoff. Annual holdouts also do not simulate in-season updates, lineups, injuries, travel, or roster changes.

The release includes raw snapshots and hashes, an audit, Python package, results notebook with saved outputs, Streamlit dashboard, CI, figures, and PDF reports. Reproduce with `python -m pip install -e .[dev]`, `sports-quant run`, and `pytest`.

The goal is a result another analyst can inspect, challenge, and rerun.
"""
    medium_vi = f"""# Benchmark dự đoán MLS có thể tái lập bắt đầu từ xác suất

Demo dự đoán thể thao thường mở đầu bằng tỷ lệ đoán đúng. Con số đó không cho biết dự báo 70% có xảy ra gần 70% hay không, hoặc thông tin tương lai có lọt vào tập kiểm định.

AlgoXpert Sports Quant Lab đưa các bước kiểm tra đó vào bản nghiên cứu.

## Dữ liệu và giới hạn

Case study dùng {audit['regular_season_rows']:,} kết quả MLS mùa thường từ American Soccer Analysis, với phạm vi nguồn 2013-2026. API nêu giấy phép CC BY-SA 4.0; repo ghi công nguồn và giữ điều khoản share-alike cho dữ liệu. Nghiên cứu chính loại {audit['knockout_rows_in_full_time_snapshot']:,} trận knockout.

Snapshot có tỷ số và mã đội, không có odds trước trận kèm timestamp. Không dùng thay bằng Football-Data vì điều khoản miễn phí hiện tại giới hạn cho cá nhân, loại trừ sử dụng thương mại và sản phẩm huấn luyện tự động. Nghiên cứu không có benchmark thị trường hay tuyên bố lợi nhuận.

## So sánh theo thời gian

Toàn bộ mùa kiểm định được giữ riêng; mô hình chỉ học từ mùa trước. Benchmark gồm baseline tần suất, Elo, logistic theo đội và Dixon-Coles. Temperature scaling dùng dự báo out-of-fold theo thời gian từ các mùa trước. Báo cáo gồm log loss, Brier đa lớp, ranked probability score, accuracy, calibration và bootstrap ghép cặp so với baseline.

## Kết quả lần chạy này

{summary_vi}

Đây là kết quả trong mẫu, không phải cam kết tương lai. Biểu đồ theo mùa và calibration giúp nhìn thấy biến động mà điểm tổng hợp có thể che khuất.

## Điều còn chưa chắc chắn

ASA có `last_updated_utc` nhưng không cung cấp phiên bản lịch sử tại từng thời điểm. Split chứng minh chỉ dùng dữ liệu mùa trước, nhưng không thể xác nhận từng bản ghi chưa bị cập nhật sau thời điểm ban đầu. Holdout theo mùa cũng chưa mô phỏng cập nhật trong mùa, đội hình, chấn thương, di chuyển hay thay đổi nhân sự.

Bản phát hành gồm snapshot và hash, data audit, package Python, notebook kèm kết quả lưu sẵn, dashboard Streamlit, CI, biểu đồ và PDF. Tái lập bằng `python -m pip install -e .[dev]`, `sports-quant run`, rồi `pytest`.

Mục tiêu là kết quả mà nhà phân tích khác có thể kiểm tra, phản biện và chạy lại.
"""
    (content / "Medium_Article_EN.md").write_text(medium_en, encoding="utf-8")
    (content / "Medium_Article_VI.md").write_text(medium_vi, encoding="utf-8")

    reddit = f"""# Reddit draft (EN)

I built a reproducible MLS 1X2 probability study: {audit['regular_season_rows']:,} regular-season results from ASA (CC BY-SA 4.0), tested on seasons {seasons}. It compares a league prior, Elo, team-ID logistic regression, and regularized Dixon-Coles. Temperature scaling sees temporal OOF forecasts from earlier seasons only.

{summary_en}

The release includes source snapshots and hashes, an audit, per-season metrics, calibration and scoreline charts, a results notebook with saved outputs, dashboard, tests, and PDFs. I did not add odds: ASA has no market prices, and the public free-data terms for Football-Data do not fit this commercial training project. No ROI claim.

The important caveat is that ASA returns current records and `last_updated_utc`, not archived versions. The time split is explicit, but historical revision cannot be fully ruled out. I would value feedback on calibration, handling team expansion/relocation, or a market-data source with clear commercial rights.

[Repository link to add after publication]
"""
    reddit_vi = f"""# Bản nháp Reddit (VI)

Tôi xây nghiên cứu xác suất 1X2 MLS có thể tái lập: {audit['regular_season_rows']:,} kết quả mùa thường từ ASA (CC BY-SA 4.0), kiểm định ở các mùa {seasons}. Mô hình gồm baseline tần suất, Elo, logistic theo mã đội và Dixon-Coles. Temperature scaling chỉ dùng dự báo OOF theo thời gian của các mùa trước.

{summary_vi}

Repo gồm snapshot/hash, audit, metrics theo mùa, biểu đồ calibration/tỷ số, notebook kèm kết quả lưu sẵn, dashboard, tests và PDF. Không thêm odds: ASA không có giá thị trường, còn điều khoản dữ liệu miễn phí Football-Data không phù hợp với sản phẩm huấn luyện thương mại. Không tuyên bố ROI.

Giới hạn chính: ASA chỉ đưa bản ghi hiện tại và `last_updated_utc`, không có phiên bản lưu trữ. Split theo thời gian là rõ ràng nhưng không thể loại trừ sửa đổi dữ liệu lịch sử. Tôi muốn nhận góp ý về calibration, xử lý mở rộng/di dời đội, hoặc nguồn odds có quyền thương mại rõ ràng.

[Bổ sung liên kết repo sau khi xuất bản]
"""
    (content / "Reddit_EN.md").write_text(reddit, encoding="utf-8")
    (content / "Reddit_VI.md").write_text(reddit_vi, encoding="utf-8")

    (content / "B2B_Outreach_EN_VI.md").write_text(
        f"""# B2B outreach drafts

## English

Subject: A probability-first MLS research sample

Hi {{Name}},\n\nI have been building a reproducible MLS forecasting study focused on probability quality and verification. The current held-out sample covers {n:,} matches across seasons {seasons}. {summary_en}\n\nThe release includes model comparisons, prior-season calibration, a source audit, and a research dashboard. It is a technical sample rather than a claim of betting returns. If your team is evaluating sports analytics or forecasting workflows, I can share the case study and discuss how its data, validation gates, and reporting could map to your needs.\n\nBest,\nJack (Pham The Anh)\nAlgoXpert

## Tiếng Việt

Chủ đề: Case study MLS tập trung vào xác suất và kiểm chứng

Chào {{Tên}},\n\nTôi đang phát triển nghiên cứu dự đoán MLS có thể tái lập, tập trung vào chất lượng xác suất và verification. Mẫu kiểm định hiện có {n:,} trận qua các mùa {seasons}. {summary_vi}\n\nBản phát hành gồm benchmark mô hình, calibration chỉ dùng mùa trước, data audit và dashboard nghiên cứu. Đây là mẫu năng lực kỹ thuật, không phải tuyên bố lợi nhuận cá cược. Nếu đội ngũ đang đánh giá quy trình sports analytics hoặc forecasting, tôi có thể gửi case study và trao đổi cách điều chỉnh dữ liệu, cổng kiểm định và báo cáo theo nhu cầu.\n\nTrân trọng,\nJack (Pham The Anh)\nAlgoXpert
""",
        encoding="utf-8",
    )
    (content / "Demo_Video_Storyboard.md").write_text(
        f"""# Demo video storyboard (90 seconds)

| Time | Visual | Voiceover / on-screen copy |
|---|---|---|
| 0-08s | `artifacts/figures/portfolio_cover.png` | “A sports model is more than a hit rate. This is a reproducible probability workflow for MLS.” |
| 08-20s | `artifacts/figures/architecture_diagram.png` | “We retain a licensed source snapshot, hashes, coverage audit, and visible model flow.” |
| 20-34s | Dashboard benchmark tab | “Four model families are compared on held-out seasons using proper scores.” |
| 34-48s | `artifacts/figures/model_benchmark.png` | “The lowest observed log loss is {best.log_loss:.3f}; paired uncertainty is shown against the league prior.” |
| 48-60s | `artifacts/figures/calibration_curve.png` | “Calibration uses earlier-season out-of-fold forecasts, then gets checked on later seasons.” |
| 60-71s | `artifacts/figures/walk_forward.png` | “Season-level results show variation hidden by an aggregate number.” |
| 71-81s | `artifacts/figures/verification_report.png` | “Leakage gates pass. The missing historical source snapshots remain an explicit limitation.” |
| 81-90s | README and report PDFs | “No market-edge or ROI claim. Code, lineage, dashboard, notebook, and reports are ready to inspect.” |

Production note: record the real local dashboard after final review. Do not fabricate screenshots or add profit claims.
""",
        encoding="utf-8",
    )

    metric_rows = "".join(
        f"<tr><td>{r.display_name}</td><td>{r.log_loss:.4f}</td><td>{r.brier:.4f}</td><td>{r.accuracy:.1%}</td><td>{r.top_label_ece_10:.3f}</td></tr>"
        for r in metrics.sort_values("log_loss").itertuples()
    )
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MLS Soccer Forecasting Research | AlgoXpert Sports Quant Lab</title>
<meta name="description" content="A reproducible MLS soccer forecasting case study with walk-forward evaluation, probability calibration, Dixon-Coles modeling, and data leakage checks.">
<meta name="keywords" content="MLS soccer analytics, football prediction probabilities, Dixon-Coles model, sports quant research, probability calibration">
<meta property="og:title" content="MLS Probability Research | AlgoXpert Sports Quant Lab"><meta property="og:description" content="Walk-forward MLS research with calibrated probabilities and verification evidence."><meta property="og:type" content="article"><meta name="author" content="Jack (Pham The Anh), AlgoXpert"><meta name="robots" content="index,follow">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"TechArticle","headline":"Reproducible MLS Probability Research","author":{{"@type":"Person","name":"Jack (Pham The Anh)"}},"publisher":{{"@type":"Organization","name":"AlgoXpert"}},"datePublished":"2026-11-26","description":"An MLS forecasting study with walk-forward validation and probability verification."}}</script>
<style>:root{{--bg:#07111d;--panel:#0d1b2a;--line:#20354a;--text:#eaf4f6;--muted:#92a6b5;--teal:#35dfbd;--cyan:#47b9ff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.65 system-ui,sans-serif}}a{{color:var(--teal)}}header,main,footer{{max-width:1120px;margin:auto;padding:24px}}.eyebrow{{color:var(--teal);font-weight:700;letter-spacing:.12em;text-transform:uppercase;font-size:.78rem}}h1{{font-size:clamp(2.7rem,7vw,5.6rem);line-height:.98;margin:.55em 0}}h2{{font-size:1.8rem;margin-top:1.8em}}.hero{{padding:60px 24px 40px}}.lead{{font-size:1.22rem;color:#c4d3dc;max-width:800px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:28px 0}}.card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:20px}}.value{{font-size:1.8rem;font-weight:750}}.label{{font-size:.8rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}}figure{{margin:24px 0;background:var(--panel);border:1px solid var(--line);padding:14px;border-radius:12px}}figure img{{width:100%;height:auto;display:block}}figcaption{{color:var(--muted);font-size:.85rem;padding:8px 4px 0}}table{{border-collapse:collapse;width:100%;font-size:.92rem}}th,td{{border-bottom:1px solid var(--line);padding:10px;text-align:left}}th{{color:var(--teal)}}.notice{{border-left:3px solid var(--cyan);padding:12px 18px;background:var(--panel);color:#c4d3dc}}footer{{color:var(--muted);border-top:1px solid var(--line);margin-top:48px;font-size:.9rem}}@media(max-width:600px){{header,main,footer{{padding:18px}}.hero{{padding-top:45px}}}}</style>
</head><body><header><div class="eyebrow">AlgoXpert Research Initiative · MLS case study</div></header><main>
<section class="hero"><h1>Sports Quant Lab</h1><p class="lead">A reproducible MLS soccer forecasting study built around probability quality, walk-forward evidence, and explicit data limits.</p><p>{summary_en}</p></section>
<section class="grid" aria-label="Research summary"><div class="card"><div class="value">{audit['regular_season_rows']:,}</div><div class="label">Regular-season matches</div></div><div class="card"><div class="value">{len(audit['seasons'])}</div><div class="label">Seasons in source coverage</div></div><div class="card"><div class="value">{best.log_loss:.3f}</div><div class="label">Lowest held-out log loss · {method}</div></div><div class="card"><div class="value">{audit['verification']['status']}</div><div class="label">Verification gates</div></div></section>
<h2>What the study tests</h2><p>Four forecast families are compared: a league outcome prior, Elo ratings, regularized team-identity logistic regression, and a Dixon-Coles goal model. Each test season is held out as a whole and uses only earlier-season results for fitting. Temperature scaling uses temporal out-of-fold forecasts from earlier seasons.</p>
<figure><img src="../artifacts/figures/architecture_diagram.png" alt="Research system: ASA source snapshot, audit, models, prior-only calibration, verification and reports"><figcaption>Research architecture generated from the implemented pipeline.</figcaption></figure>
<h2>Benchmark and uncertainty</h2><p>Proper scores assess probabilistic forecasts; accuracy alone can hide poor confidence estimates. The chart reports log loss and paired-bootstrap intervals for the difference from the league prior.</p><figure><img src="../artifacts/figures/model_benchmark.png" alt="Held-out model log loss and paired bootstrap intervals versus league prior"><figcaption>Annual expanding-window test seasons {seasons}. Negative score differences favor a model; intervals crossing zero are inconclusive.</figcaption></figure>
<h2>Calibration and stability</h2><figure><img src="../artifacts/figures/calibration_curve.png" alt="Home, draw and away calibration curves for prior-season calibrated models"><figcaption>Reliability curves are calculated only on held-out predictions.</figcaption></figure><figure><img src="../artifacts/figures/walk_forward.png" alt="Log loss by model across annual MLS holdout seasons"><figcaption>Per-season results show variation alongside aggregate metrics.</figcaption></figure>
<h2>Data and responsible claims</h2><p>The source is the American Soccer Analysis public API, retrieved {audit['retrieved_utc']} and licensed under CC BY-SA 4.0. The study has results and team IDs, but no timestamped market odds. No market edge, betting return, or arbitrage claim is made.</p><p class="notice">The API exposes current records and last_updated_utc but no historical point-in-time versions. The experiment verifies season-level train/test separation; it cannot rule out every historical record revision. This is a research case study, not betting advice.</p>
<h2>Results</h2><table><thead><tr><th>Model</th><th>Log loss</th><th>Brier</th><th>Accuracy</th><th>Top-label ECE</th></tr></thead><tbody>{metric_rows}</tbody></table>
<h2>Explore the research</h2><ul><li><a href="../README.md">Repository and reproduction commands</a></li><li><a href="../artifacts/reports/technical_research_report.pdf">Technical research report (PDF)</a></li><li><a href="../artifacts/reports/upwork_portfolio_case_study.pdf">Portfolio case study (PDF)</a></li></ul></main><footer>Data by American Soccer Analysis · CC BY-SA 4.0 · Code under MIT · Snapshot retrieved 2026-11-26.</footer></body></html>"""
    (website / "index.html").write_text(html, encoding="utf-8")

    (ROOT / "README.md").write_text(
        f"""# AlgoXpert Sports Quant Lab

**AlgoXpert Research Initiative | MLS case study | Reproducible probability research**

This research release compares transparent three-way match probability models, checks calibration, and makes data lineage, temporal splits, uncertainty, and limitations inspectable. It is not a betting product.

## Current evidence
- ASA snapshot retrieved: **{audit['retrieved_utc']}** (American Soccer Analysis, CC BY-SA 4.0)
- Source coverage: **{audit['regular_season_rows']:,} regular-season matches**, seasons {min(audit['seasons'])}-{max(audit['seasons'])}
- Test seasons: **{seasons}** (annual expanding-window holdouts)
- Lowest aggregate held-out log loss: **{method}, {best.log_loss:.4f}** over {n:,} matches
- Paired bootstrap delta vs league prior: **{best.bootstrap_delta_log_loss_vs_prior:+.4f}** (95% interval {best.bootstrap_delta_log_loss_ci95_low:+.4f} to {best.bootstrap_delta_log_loss_ci95_high:+.4f})
- Verification gates: **{audit['verification']['status']}**

This is a historical sample result, not a claim of a durable future edge. ASA does not provide point-in-time historical versions, and the report states that limit. No odds benchmark, market outperformance, betting ROI, or arbitrage claim is included.

## Models and validation
- League outcome-frequency prior
- Elo ratings with fixed home advantage
- Regularized multinomial logistic regression over pre-match home/away team IDs
- Regularized Dixon-Coles goal model with a low-score correction
- Raw and prior-season out-of-fold temperature-scaled forecasts

Each complete test season is excluded from fitting. Calibration uses only temporally prior out-of-fold predictions. Scores include log loss, multiclass Brier score, ranked probability score, accuracy, calibration error, goal MAE/NLL, and paired match-bootstrap intervals.

## Reproduce locally
```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -e ".[dev]"
sports-quant run
pytest
ruff check src tests
streamlit run dashboard.py
```

Refresh data (internet required) with `sports-quant fetch --league mls`; then run `sports-quant run`. The checked-in raw snapshot keeps this study reproducible offline. Use `sports-quant audit` to inspect the source counts and hashes.

## Evidence files
- `artifacts/model_metrics.csv`, `artifacts/metrics_by_season.csv`, `artifacts/predictions.csv`
- `artifacts/data_audit.json`, `artifacts/calibration_oof_predictions.csv`, `artifacts/scoreline_distribution.csv`
- `artifacts/figures/` (cover, architecture, benchmark, calibration, scoreline, walk-forward, coverage, verification, collage)
- `artifacts/reports/technical_research_report.pdf`, `upwork_portfolio_case_study.pdf`, `verification_report.pdf`
- `notebooks/01_mls_walk_forward.ipynb` (result notebook with saved outputs)
- `content/` (English/Vietnamese LinkedIn, Medium, Reddit, outreach, and demo storyboard)
- `website/index.html` (local SEO case study)

## Data and license
The raw files are American Soccer Analysis API data under **CC BY-SA 4.0**. Attribute ASA and preserve share-alike for the data and adaptations. The project code is MIT licensed; see `data/README.md` and `LICENSE`. Football-Data is not used because its current public free-data terms exclude commercial and automated training-product use.

## Limitations
- Current ASA records include `last_updated_utc`, but no point-in-time history. Historical source revisions cannot be ruled out.
- Whole-season forecasts do not simulate in-season updates and use no lineup, injury, travel, player-level, or market data.
- Better scores in this sample do not show future profit or market inefficiency.

## References
- ASA API: https://app.americansocceranalysis.com/api/v1/openapi.json
- Dixon and Coles (1997), DOI: https://doi.org/10.1111/1467-9876.00065
- scikit-learn probability calibration: https://scikit-learn.org/stable/modules/calibration.html
- Football-Data terms (reviewed, not used): https://football-data.co.uk/data.php

Draft marketing assets are not published. Add the repository URL and editorially review all copy before posting.
""",
        encoding="utf-8",
    )

    (ROOT / "MARKETING_BRIEF.md").write_text(
        f"""# MARKETING_BRIEF.md - Sports Quant Lab

## Positioning
AlgoXpert Sports Quant Lab combines quantitative modeling with visible verification. The MLS case study emphasizes probability quality, chronological evaluation, provenance, uncertainty, and clear limits rather than a headline hit rate.

## Audiences and channels
- Sports analytics, quantitative research, prediction-market and data-product teams: technical case study and evidence pack.
- Upwork buyers: concise portfolio PDF with exact scope and artifacts.
- LinkedIn: short evidence-led post with a research chart.
- Medium: methods-first article on data rights, temporal design, calibration, and limitations.
- Reddit: transparent technical discussion that invites critique.
- Website: locally generated SEO case study for MLS probability modeling and calibration.

## Current result
{summary_en}

Source: ASA public API, CC BY-SA 4.0. Snapshot covers {audit['regular_season_rows']:,} regular-season matches, {min(audit['seasons'])}-{max(audit['seasons'])}. Evaluation test seasons: {seasons}. See `artifacts/data_audit.json` and `artifacts/model_metrics.csv`.

## Claims policy
State the evaluation window and score. Label the result as historical. Do not imply guaranteed accuracy, ROI, market outperformance, arbitrage, or real-time production. Attribute ASA and include the missing point-in-time revision history limitation. Drafts are not published.

## Draft inventory
English/Vietnamese LinkedIn, Medium and Reddit; bilingual B2B outreach; demo video storyboard; local website page.
""",
        encoding="utf-8",
    )

    (ROOT / "START_HERE.md").write_text(
        f"""# Start Here - AlgoXpert Sports Quant Lab

The MLS quantitative-modeling branch is implemented with real ASA data, a source audit, temporal model comparisons, prior-season calibration, dashboard, results notebook with saved outputs, CI, figures, and PDFs. Current verification status: **{audit['verification']['status']}**.

## First run
1. Install Python 3.10+.
2. Create/activate a virtual environment.
3. `python -m pip install -e .[dev]`
4. `sports-quant run` to recreate metrics, charts, reports, and marketing copy.
5. `pytest` and `ruff check src tests`.
6. `streamlit run dashboard.py` to explore the dashboard.

Refresh data separately with `sports-quant fetch --league mls`; it requires internet. The checked-in raw snapshot is available offline.

Start with `README.md`, `CODEX_HANDOFF.md`, `MARKETING_BRIEF.md`, `artifacts/reports/technical_research_report.pdf`, and `artifacts/reports/upwork_portfolio_case_study.pdf`.

This release excludes arbitrage execution, Redis, live data, odds, and publishing. ASA has no archived point-in-time versions; the reports state this limit.
""",
        encoding="utf-8",
    )
    (ROOT / "CODEX_HANDOFF.md").write_text(
        f"""# CODEX_HANDOFF.md - AlgoXpert Sports Quant Lab v1.0

## Implementation status
Implemented the MLS quantitative-modeling branch from the supplied brief: Python package, ASA data fetch and audit, four model families, prior-only temperature scaling, annual walk-forward evaluation, tests/CI, dashboard, results notebook with saved outputs, technical and portfolio PDFs, visual evidence, and English/Vietnamese content drafts.

## Acceptance evidence
- Real data: {audit['regular_season_rows']:,} regular-season matches; source snapshot and SHA-256 hashes are included.
- Model outputs and metrics: `artifacts/predictions.csv`, `artifacts/model_metrics.csv`, and `artifacts/metrics_by_season.csv`.
- Verification: `{audit['verification']['status']}`; detailed checks at `artifacts/data_audit.json`.
- Visual and commercial assets: `artifacts/figures/`, `artifacts/reports/`, `content/`, and `website/index.html`.
- Market benchmark/ROI: not claimed because the permitted ASA data has no market prices. Football-Data free-data terms are unsuitable for commercial automated training use.
- Publication: not performed.

## System map
`data/pipeline.py` handles ASA snapshots and audit; `models/predictors.py` implements prior/Elo/logistic/Dixon-Coles/temperature scaling; `research.py` creates temporal folds; `evaluation.py` scores probabilities; `visuals.py`, `reports.py`, and `marketing.py` generate the evidence and assets; `dashboard.py` reads run artifacts.

## Reproduce
`python -m pip install -e .[dev]` -> `sports-quant run` -> `pytest` -> `ruff check src tests` -> `streamlit run dashboard.py`.

## Limits
ASA does not expose archived point-in-time versions; historical source revision cannot be ruled out. Whole-season forecasts do not simulate in-season updates. Odds, execution, Redis, and public deployment remain outside this release.
""",
        encoding="utf-8",
    )

