# Bản nháp Reddit (VI)

Tôi xây nghiên cứu xác suất 1X2 MLS có thể tái lập: 5,732 kết quả mùa thường từ ASA (CC BY-SA 4.0), kiểm định ở các mùa 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026. Mô hình gồm baseline tần suất, Elo, logistic theo mã đội và Dixon-Coles. Temperature scaling chỉ dùng dự báo OOF theo thời gian của các mùa trước.

League prior có log loss tổng hợp thấp nhất trong mẫu kiểm định của lần chạy này: 1.0609 trên 3,641 trận ở các mùa 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026. Chênh lệch bootstrap ghép cặp so với baseline tần suất giải là +0.0000 (khoảng 95%: +0.0000 đến +0.0000). Cả 6 biến thể đã fit đều có log loss tổng hợp cao hơn baseline. Đây là kết quả trong mẫu lịch sử, không phải cam kết lợi thế tương lai, vượt trội thị trường hay lợi nhuận cá cược.

Repo gồm snapshot/hash, audit, metrics theo mùa, biểu đồ calibration/tỷ số, notebook kèm kết quả lưu sẵn, dashboard, tests và PDF. Không thêm odds: ASA không có giá thị trường, còn điều khoản dữ liệu miễn phí Football-Data không phù hợp với sản phẩm huấn luyện thương mại. Không tuyên bố ROI.

Giới hạn chính: ASA chỉ đưa bản ghi hiện tại và `last_updated_utc`, không có phiên bản lưu trữ. Split theo thời gian là rõ ràng nhưng không thể loại trừ sửa đổi dữ liệu lịch sử. Tôi muốn nhận góp ý về calibration, xử lý mở rộng/di dời đội, hoặc nguồn odds có quyền thương mại rõ ràng.

[Bổ sung liên kết repo sau khi xuất bản]
