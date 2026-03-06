# Requirements

Implement a web application with the following features:

Core Functionalities:

- Manage customer contact information:
  - Full Name
  - Address
  - Phone Number
  - Email Address
- Create, Read, Update, Delete (CRUD) customer records
- User-friendly web-based interface (UI)

Communication Features:

- Send SMS to customers
- Send Email to customers
- Allow selection of individual or multiple customers for communication

# Web: html, css, js + python (flask)

## Backend:

- Công nghệ: Amazon EC2
- Mục đích:
  - Chạy server
  - Xử lý logic
  - Giao tiếp database
  - Gửi SMS/email

## Database:

- Công nghệ: Amazon RDS (Cơ sở dữ liệu quan hệ)
- Mục đích:
  - Lưu thông tin khách hàng
  - Thực hiện CRUD
  - Đảm bảo dữ liệu không mất khi server restart

## Messaging:

- Công nghệ:
  - Amazon SES – Chuyên gửi mail
  - Amazon SNS – Chuyên gửi sms
- Mục đích:
  - Gửi email marketing
  - Gửi SMS thông báo
  - Tích hợp API vào backend

## Security:

- Công nghệ:
  - AWS IAM
  - Security Groups
- Mục đích:
  - Phân quyền truy cập
  - Chặn truy cập trái phép
  - Bảo vệ database

## Monitoring:

- Công nghệ: Amazon CloudWatch
- Mục đích:
  - Xem log
  - Phát hiện lỗi
  - Theo dõi hiệu năng

# Database ERD (Entity-Relationship Diagram)

erDiagram
CUSTOMERS ||--o{ COMMUNICATION_LOGS : "receives"

    CUSTOMERS {
        int customer_id PK
        string full_name
        string address
        string phone_number
        string email_address
        datetime created_at
    }

    COMMUNICATION_LOGS {
        int log_id PK
        int customer_id FK
        string type "SMS / EMAIL"
        string status "Pending / Success / Failed"
        string message_id "AWS Tracking ID"
        datetime sent_at
    }
