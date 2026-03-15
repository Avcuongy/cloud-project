import os
from datetime import datetime, timedelta

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
    session,
)
from flask_sqlalchemy import SQLAlchemy


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def create_app() -> Flask:
    # Disable Flask's default static route for the entire "app" folder
    app = Flask(
        __name__,
        static_folder=None,
        template_folder=os.path.join("app", "pages"),
    )

    # Database configuration
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is required but not set. "
            "Vui lòng cấu hình chuỗi kết nối MySQL qua biến môi trường."
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    # Session auto-expire after 3 hours of inactivity
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=3)

    db = SQLAlchemy(app)

    # AWS clients (optional)
    aws_region = os.getenv("AWS_REGION", "ap-southeast-1")
    ses_sender = os.getenv("SES_SENDER_EMAIL")
    sns_sender_id = os.getenv("SNS_SENDER_ID", "CloudApp")

    ses_client = boto3.client("ses", region_name=aws_region)
    sns_client = boto3.client("sns", region_name=aws_region)

    class User(db.Model):  # type: ignore[misc]
        __tablename__ = "USERS"

        user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        full_name = db.Column(db.String(255), nullable=False)
        user_name = db.Column(db.String(100), nullable=False, unique=True)
        password = db.Column(db.String(255), nullable=False)
        phone_number = db.Column(db.String(20))
        email_address = db.Column(db.String(150), nullable=False, unique=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

        def to_dict(self) -> dict:
            return {
                "id": self.user_id,
                "fullName": self.full_name,
                "userName": self.user_name,
                "email": self.email_address,
                "createdAt": (self.created_at or datetime.utcnow()).isoformat(),
            }

    class Customer(db.Model):  # type: ignore[misc]
        __tablename__ = "CUSTOMERS"

        customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        full_name = db.Column(db.String(255), nullable=False)
        address = db.Column(db.Text)
        phone_number = db.Column(db.String(20))
        email_address = db.Column(db.String(150))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

        def to_dict(self) -> dict:
            return {
                "id": self.customer_id,
                "fullName": self.full_name,
                "address": self.address or "",
                "phone": self.phone_number or "",
                "email": self.email_address or "",
                "createdAt": (self.created_at or datetime.utcnow()).isoformat(),
            }

    class CommunicationLog(db.Model):  # type: ignore[misc]
        __tablename__ = "LOGS"

        log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        customer_id = db.Column(
            db.Integer,
            db.ForeignKey("CUSTOMERS.customer_id", ondelete="CASCADE"),
            nullable=False,
        )
        type = db.Column(db.Enum("SMS", "EMAIL", name="comm_type"), nullable=False)
        status = db.Column(
            db.Enum("Pending", "Success", "Failed", name="comm_status"),
            default="Pending",
        )
        message_id = db.Column(db.String(255))
        sent_at = db.Column(db.DateTime, default=datetime.utcnow)

        # Rely on database ON DELETE CASCADE instead of setting customer_id to NULL
        # to avoid IntegrityError when deleting a customer that has logs.
        customer = db.relationship(
            Customer,
            backref=db.backref("logs", passive_deletes=True),
            passive_deletes=True,
        )

        def to_dict(self) -> dict:
            return {
                "id": self.log_id,
                "customerId": self.customer_id,
                "customerName": self.customer.full_name if self.customer else "",
                "type": self.type,
                "status": self.status,
                "messageId": self.message_id or "",
                "sentAt": (self.sent_at or datetime.utcnow()).isoformat(),
            }

    # Routes to serve pages
    @app.route("/")
    def index():
        return redirect(url_for("login_page"))

    @app.route("/login")
    def login_page():
        return render_template("login.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/composer")
    def composer():
        return render_template("composer.html")

    @app.route("/logs")
    def logs_page():
        return render_template("logs.html")

    # Static assets (JS, CSS)
    @app.route("/scripts/<path:filename>")
    def scripts(filename: str):
        return send_from_directory(os.path.join("app", "scripts"), filename)

    @app.route("/styles/<path:filename>")
    def styles(filename: str):
        return send_from_directory(os.path.join("app", "styles"), filename)

    @app.route("/assets/<path:filename>")
    def assets(filename: str):
        return send_from_directory("assets", filename)

    # Simple auth guard so only logged-in users
    @app.before_request
    def require_login():
        endpoint = request.endpoint

        # Skip checks for static files or public endpoints
        public_endpoints = {
            "index",
            "login_page",
            "api_login",
            "api_logout",
            "static",
            "scripts",
            "styles",
            "assets",
            "health",
        }

        if not endpoint or endpoint in public_endpoints:
            return None

        if "user_id" not in session:
            # For API calls, return JSON 401 instead of redirect
            if request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized"}), 401
            return redirect(url_for("login_page"))

    # API: Auth
    @app.route("/api/login", methods=["POST"])
    def api_login():
        payload = request.get_json(force=True) or {}
        username = (payload.get("userName") or payload.get("username") or "").strip()
        password = (payload.get("password") or "").strip()

        if not username or not password:
            return jsonify({"error": "userName and password are required"}), 400

        user = User.query.filter_by(user_name=username).first()
        if not user or user.password != password:
            return jsonify({"error": "Sai tài khoản hoặc mật khẩu"}), 401

        # Clear session to prevent fixation, then set new session data
        session.clear()
        session.permanent = True
        session["user_id"] = user.user_id
        session["user_name"] = user.user_name
        return jsonify({"ok": True, "user": user.to_dict()})

    @app.route("/api/logout", methods=["POST"])
    def api_logout():
        session.clear()
        return jsonify({"ok": True})

    # API: Customers
    @app.route("/api/customers", methods=["GET"])
    def list_customers():
        customers = Customer.query.order_by(Customer.created_at.desc()).all()
        return jsonify([c.to_dict() for c in customers])

    @app.route("/api/customers", methods=["POST"])
    def create_customer():
        payload = request.get_json(force=True) or {}
        full_name = (payload.get("fullName") or "").strip()
        if not full_name:
            return jsonify({"error": "fullName is required"}), 400

        customer = Customer(
            full_name=full_name,
            address=(payload.get("address") or "").strip(),
            phone_number=(payload.get("phone") or "").strip(),
            email_address=(payload.get("email") or "").strip(),
        )
        db.session.add(customer)
        db.session.commit()
        return jsonify(customer.to_dict()), 201

    @app.route("/api/customers/<int:customer_id>", methods=["PUT"])
    def update_customer(customer_id: int):
        customer = Customer.query.get_or_404(customer_id)
        payload = request.get_json(force=True) or {}
        full_name = (payload.get("fullName") or "").strip()
        if not full_name:
            return jsonify({"error": "fullName is required"}), 400

        customer.full_name = full_name
        customer.address = (payload.get("address") or "").strip()
        customer.phone_number = (payload.get("phone") or "").strip()
        customer.email_address = (payload.get("email") or "").strip()
        db.session.commit()
        return jsonify(customer.to_dict())

    @app.route("/api/customers/<int:customer_id>", methods=["DELETE"])
    def delete_customer(customer_id: int):
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        return "", 204

    def get_sender_email() -> str | None:
        """Return base sender email.

        Priority:
        1. Email by user currently logged in (if any).
        2. Any user in the system (take the first one).
        3. Fallback to SES_SENDER_EMAIL environment variable.
        """

        # 1.
        user_id = session.get("user_id")
        if user_id:
            user = User.query.get(user_id)
            if user and user.email_address:
                return user.email_address

        # 2.
        user = User.query.order_by(User.user_id.asc()).first()
        if user and user.email_address:
            return user.email_address

        # 3.
        return ses_sender

    def get_sms_sender_id() -> str:
        """Return SMS SenderID for AWS SNS.

        Priority:
        1. User name of the currently logged-in user (if any).
        2. Fallback to SNS_SENDER_ID environment variable (default "CloudApp").
        """

        user_id = session.get("user_id")
        if user_id:
            user = User.query.get(user_id)
            if user and getattr(user, "user_name", None):
                raw = "".join(ch for ch in user.user_name if ch.isalnum())
                if raw:
                    return raw[:11]

        return sns_sender_id

    # API: Logs
    @app.route("/api/logs", methods=["GET"])
    def list_logs():
        logs = CommunicationLog.query.order_by(CommunicationLog.sent_at.desc()).all()
        return jsonify([l.to_dict() for l in logs])

    @app.route("/api/logs", methods=["POST"])
    def create_logs():
        payload = request.get_json(force=True) or {}
        customer_ids = payload.get("customerIds") or []
        message_type = (payload.get("type") or "EMAIL").upper()
        message_body = (payload.get("message") or "").strip()
        if message_type not in {"SMS", "EMAIL"}:
            return jsonify({"error": "type must be SMS or EMAIL"}), 400

        if not message_body:
            return jsonify({"error": "message is required"}), 400

        if not isinstance(customer_ids, list) or not customer_ids:
            return jsonify({"error": "customerIds must be a non-empty list"}), 400

        created_logs = []
        now = datetime.utcnow()

        def send_email(customer: Customer) -> tuple[str, str]:
            """
            Send email via AWS SES. Returns (status, message_id).
            """
            sender_email = get_sender_email()
            if not sender_email or not customer.email_address:
                # Fallback: mark as failed when SES or email is not configured
                fake_id = f"EMAIL-{int(now.timestamp())}-{customer.customer_id}"
                return "Failed", fake_id

            try:
                response = ses_client.send_email(
                    Source=sender_email,
                    Destination={"ToAddresses": [customer.email_address]},
                    Message={
                        "Subject": {
                            "Data": "Thông báo khách hàng",
                            "Charset": "UTF-8",
                        },
                        "Body": {
                            "Text": {
                                "Data": message_body,
                                "Charset": "UTF-8",
                            }
                        },
                    },
                )
                message_id = response.get("MessageId", "")
                return "Success", message_id or "SES_UNKNOWN_ID"
            except (BotoCoreError, ClientError) as exc:  # pragma: no cover - external
                app.logger.exception("Failed to send email via SES", exc_info=exc)
                return "Failed", "SES_ERROR"

        def send_sms(customer: Customer) -> tuple[str, str]:
            """Send SMS via AWS SNS. Returns (status, message_id)."""
            if not customer.phone_number:
                fake_id = f"SMS-{int(now.timestamp())}-{customer.customer_id}"
                return "Failed", fake_id

            try:
                sender_id = get_sms_sender_id()
                attributes = {
                    "AWS.SNS.SMS.SenderID": {
                        "DataType": "String",
                        "StringValue": sender_id,
                    },
                }
                response = sns_client.publish(
                    PhoneNumber=customer.phone_number,
                    Message=message_body,
                    MessageAttributes=attributes,
                )
                message_id = response.get("MessageId", "")
                return "Success", message_id or "SNS_UNKNOWN_ID"
            except (BotoCoreError, ClientError) as exc:
                app.logger.exception("Failed to send SMS via SNS", exc_info=exc)
                return "Failed", "SNS_ERROR"

        for cid in customer_ids:
            customer = Customer.query.get(cid)
            if not customer:
                continue

            if message_type == "EMAIL":
                status, message_id = send_email(customer)
            else:  # SMS
                status, message_id = send_sms(customer)

            log = CommunicationLog(
                customer_id=customer.customer_id,
                type=message_type,
                status=status,
                message_id=message_id,
                sent_at=now,
            )
            db.session.add(log)
            created_logs.append(log)

        db.session.commit()
        return jsonify([l.to_dict() for l in created_logs]), 201

    # Simple health endpoint for AWS
    @app.route("/health")
    def health():
        return {"status": "ok"}

    # Attach db to app for shell / migrations if needed
    app.db = db  # type: ignore[attr-defined]
    app.Customer = Customer  # type: ignore[attr-defined]
    app.CommunicationLog = CommunicationLog  # type: ignore[attr-defined]

    return app


app = create_app()
application = app


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=True,
        use_reloader=False,
    )
