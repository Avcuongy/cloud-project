# aws

1. Thiết lập AWS credentials (ví dụ qua biến môi trường):

   ```bash
   setx AWS_ACCESS_KEY_ID "<your_access_key_id>"
   setx AWS_SECRET_ACCESS_KEY "<your_secret_access_key>"
   setx AWS_REGION "ap-southeast-1"
   setx SES_SENDER_EMAIL "no-reply@your-domain.com"
   setx SNS_SENDER_ID "YourBrand"
   ```

2. Verify email và (nếu cần) domain gửi trong AWS SES.
3. Đảm bảo tài khoản AWS ở chế độ production (không còn trong SES sandbox nếu muốn gửi đến địa chỉ tự do).
4. Chạy ứng dụng:
   ```bash
   python app.py
   ```
