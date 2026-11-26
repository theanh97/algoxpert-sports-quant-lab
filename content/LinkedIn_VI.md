# Bài LinkedIn (VI)

Một mô hình dự đoán chỉ đáng tin khi xác suất vượt qua phép kiểm định tôn trọng thời gian.

League prior có log loss tổng hợp thấp nhất trong mẫu kiểm định của lần chạy này: 1.0609 trên 3,641 trận ở các mùa 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026. Chênh lệch bootstrap ghép cặp so với baseline tần suất giải là +0.0000 (khoảng 95%: +0.0000 đến +0.0000). Cả 6 biến thể đã fit đều có log loss tổng hợp cao hơn baseline. Đây là kết quả trong mẫu lịch sử, không phải cam kết lợi thế tương lai, vượt trội thị trường hay lợi nhuận cá cược.

AlgoXpert Sports Quant Lab là nghiên cứu MLS có thể tái lập, dùng 5,732 kết quả mùa thường từ American Soccer Analysis (phạm vi 2013-2026). Benchmark gồm baseline tần suất, Elo, logistic theo đội và Dixon-Coles. Temperature scaling dùng dự báo out-of-fold của các mùa trước; quy trình kiểm tra mốc thời gian, mã trận, miền xác suất và calibration.

Snapshot không có giá thị trường kèm timestamp; API cũng không có phiên bản lịch sử tại từng thời điểm. Không tuyên bố lợi thế thị trường, ROI hay arbitrage.

Mã nguồn, audit, dashboard, notebook, report và biểu đồ: [bổ sung liên kết repo sau khi xuất bản].

#SportsAnalytics #QuantResearch #MLS #ProbabilityCalibration
