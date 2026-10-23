# Hệ thống Quiz trắc nghiệm sử dụng Docker

**Sinh viên:** Dương Tiến Dũng  
**Mã sinh viên:** DTC245200789

## 1. Giới thiệu

Dự án xây dựng hệ thống thi trắc nghiệm trực tuyến sử dụng Python Flask,
PostgreSQL và Docker Compose. Hệ thống được tổ chức thành các dịch vụ riêng
biệt nhằm hỗ trợ triển khai, quản lý và giám sát.

## 2. Công nghệ sử dụng

- Python và Flask: xây dựng ứng dụng web và API.
- PostgreSQL: lưu trữ dữ liệu câu hỏi.
- Docker và Docker Compose: đóng gói và triển khai dịch vụ.
- Nginx: reverse proxy.
- Prometheus và Grafana: giám sát hệ thống.
- Loki và Promtail: thu thập và quản lý log.

## 3. Chức năng chính

- Hiển thị câu hỏi trắc nghiệm.
- Nhận câu trả lời và tính kết quả.
- Cung cấp API.
- Kiểm tra tình trạng hoạt động qua health check.
- Cung cấp metrics phục vụ giám sát.

## 4. Cài đặt và chạy

Tạo file cấu hình môi trường từ mẫu:

    cp .env.example .env
    chmod 600 .env

Chỉnh sửa mật khẩu trong file .env trước khi chạy.

Khởi động hệ thống:

    docker compose up --build -d

Kiểm tra trạng thái:

    docker compose ps

Xem nhật ký:

    docker compose logs --tail=100

Dừng hệ thống:

    docker compose down

## 5. Cấu trúc dự án

- app.py: ứng dụng Flask.
- init_db.py: khởi tạo cơ sở dữ liệu.
- templates/: giao diện web.
- Dockerfile: cấu hình image ứng dụng.
- compose.yaml: cấu hình dịch vụ Docker.
- nginx/: cấu hình Nginx.
- monitoring/: cấu hình giám sát và logging.
- .env.example: mẫu biến môi trường.
- .gitignore: danh sách file Git bỏ qua.

## 6. An toàn thông tin

Không đưa file .env, mật khẩu thật, thông tin xác thực hoặc dữ liệu cá nhân
lên GitHub. Chỉ sử dụng file .env.example để cung cấp mẫu cấu hình.

## 7. Tác giả

Dương Tiến Dũng  
Mã sinh viên: DTC245200789
