# Benchmark dự đoán MLS có thể tái lập bắt đầu từ xác suất

Demo dự đoán thể thao thường mở đầu bằng tỷ lệ đoán đúng. Con số đó không cho biết dự báo 70% có xảy ra gần 70% hay không, hoặc thông tin tương lai có lọt vào tập kiểm định.

AlgoXpert Sports Quant Lab đưa các bước kiểm tra đó vào bản nghiên cứu.

## Dữ liệu và giới hạn

Case study dùng 5,732 kết quả MLS mùa thường từ American Soccer Analysis, với phạm vi nguồn 2013-2026. API nêu giấy phép CC BY-SA 4.0; repo ghi công nguồn và giữ điều khoản share-alike cho dữ liệu. Nghiên cứu chính loại 266 trận knockout.

Snapshot có tỷ số và mã đội, không có odds trước trận kèm timestamp. Không dùng thay bằng Football-Data vì điều khoản miễn phí hiện tại giới hạn cho cá nhân, loại trừ sử dụng thương mại và sản phẩm huấn luyện tự động. Nghiên cứu không có benchmark thị trường hay tuyên bố lợi nhuận.

## So sánh theo thời gian

Toàn bộ mùa kiểm định được giữ riêng; mô hình chỉ học từ mùa trước. Benchmark gồm baseline tần suất, Elo, logistic theo đội và Dixon-Coles. Temperature scaling dùng dự báo out-of-fold theo thời gian từ các mùa trước. Báo cáo gồm log loss, Brier đa lớp, ranked probability score, accuracy, calibration và bootstrap ghép cặp so với baseline.

## Kết quả lần chạy này

League prior có log loss tổng hợp thấp nhất trong mẫu kiểm định của lần chạy này: 1.0609 trên 3,641 trận ở các mùa 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026. Chênh lệch bootstrap ghép cặp so với baseline tần suất giải là +0.0000 (khoảng 95%: +0.0000 đến +0.0000). Cả 6 biến thể đã fit đều có log loss tổng hợp cao hơn baseline. Đây là kết quả trong mẫu lịch sử, không phải cam kết lợi thế tương lai, vượt trội thị trường hay lợi nhuận cá cược.

Đây là kết quả trong mẫu, không phải cam kết tương lai. Biểu đồ theo mùa và calibration giúp nhìn thấy biến động mà điểm tổng hợp có thể che khuất.

## Điều còn chưa chắc chắn

ASA có `last_updated_utc` nhưng không cung cấp phiên bản lịch sử tại từng thời điểm. Split chứng minh chỉ dùng dữ liệu mùa trước, nhưng không thể xác nhận từng bản ghi chưa bị cập nhật sau thời điểm ban đầu. Holdout theo mùa cũng chưa mô phỏng cập nhật trong mùa, đội hình, chấn thương, di chuyển hay thay đổi nhân sự.

Bản phát hành gồm snapshot và hash, data audit, package Python, notebook kèm kết quả lưu sẵn, dashboard Streamlit, CI, biểu đồ và PDF. Tái lập bằng `python -m pip install -e .[dev]`, `sports-quant run`, rồi `pytest`.

Mục tiêu là kết quả mà nhà phân tích khác có thể kiểm tra, phản biện và chạy lại.
