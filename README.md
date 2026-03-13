## Domain

- Local: [link](http://127.0.0.1:5000/)
- Public: [Link](http://13.213.11.214/)

## Sender Email

The system follows this priority to select the sender's email:

1. **Logged-in User:** The email of the current user (must be AWS-verified).
2. **First User:** If no user is logged in, use the email of the first user found in the `USERS` table.
3. **Fallback:** If both options are unavailable, use the `SES_SENDER_EMAIL` environment variable.

## Sender ID for SMS (SNS)

The SenderID for AWS SNS follows this priority:

1. **Username:** The `user_name` of the logged-in user (must be registered with AWS).
2. **Fallback:** If the username is missing or empty, use the `SNS_SENDER_ID` environment variable.
