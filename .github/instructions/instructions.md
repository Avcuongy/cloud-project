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

# Web UI

## Page 1: Dashboard (Customer List) - MOST IMPORTANT

This is the central page where the instructor will spend the most time.

**Functions:**

- **Customer Table:** Display a list of customers retrieved from RDS.
- **Bulk Selection:** Checkboxes at the start of each row to select multiple customers.
- **Action Buttons:** "Add Customer", "Send Email/SMS to Selected", "Edit", and "Delete".
- **UI Tip:** Add a small search bar at the top to make the interface more user-friendly.

---

## Page 2: Add/Edit Customer Form

You can use the same layout for both creating new customers and updating existing information.

**Functions:**

- **Input Fields:** Full Name, Address, Phone, and Email.
- **Action Buttons:** "Save" and "Cancel".
- **UI Tip:** For a more professional feel (Single Page Application style), you can use a Modal (pop-up) instead of a separate page. However, using separate pages will provide more screenshots for your final report.

---

## Page 3: Message Composer

This page appears after you select customers on Page 1 and click "Send".

**Functions:**

- **Confirmation List:** Display the names of the selected customers.
- **Message Input:** A textarea to type the message content.
- **Delivery Method:** Toggle between Email (via SES) or SMS (via SNS).
- **Action Button:** "Send Now".

---

## Page 4: Communication Logs

This page is used to gain points for the "Monitoring" and "Integration" sections of the project.

**Functions:**

- **History Table:** Shows Customer Name - Content - Status (Pending/Success/Failed) - Timestamp.
- **Why it is needed:** During the demo, if a message is not delivered immediately (due to network lag or AWS Sandbox mode), you can use this log to show the instructor that the system has processed the request successfully.
