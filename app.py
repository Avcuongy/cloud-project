import os
from datetime import datetime

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def create_app() -> Flask:
    app = Flask(
        __name__,
        static_folder=os.path.join("app"),
        template_folder=os.path.join("app", "pages"),
    )

    # Database configuration
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Fallback to local MySQL on default port; adjust via env when deploying
        db_url = "mysql+pymysql://user:password@localhost/manager"

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db = SQLAlchemy(app)

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
        __tablename__ = "COMMUNICATION_LOGS"

        log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        customer_id = db.Column(
            db.Integer, db.ForeignKey("CUSTOMERS.customer_id"), nullable=False
        )
        type = db.Column(db.Enum("SMS", "EMAIL", name="comm_type"), nullable=False)
        status = db.Column(
            db.Enum("Pending", "Success", "Failed", name="comm_status"),
            default="Pending",
        )
        message_id = db.Column(db.String(255))
        sent_at = db.Column(db.DateTime, default=datetime.utcnow)

        customer = db.relationship(Customer, backref="logs")

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
        return redirect(url_for("dashboard"))

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
        if message_type not in {"SMS", "EMAIL"}:
            return jsonify({"error": "type must be SMS or EMAIL"}), 400

        if not isinstance(customer_ids, list) or not customer_ids:
            return jsonify({"error": "customerIds must be a non-empty list"}), 400

        created_logs = []
        now = datetime.utcnow()
        for cid in customer_ids:
            customer = Customer.query.get(cid)
            if not customer:
                continue
            # In a real integration, you would call AWS SES/SNS here and get message_id
            message_id = f"{message_type}-{int(now.timestamp())}-{cid}"
            log = CommunicationLog(
                customer_id=customer.customer_id,
                type=message_type,
                status="Success",
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
application = app  # for some AWS platforms (Elastic Beanstalk, etc.)


if __name__ == "__main__":
    # For local development only. In production use gunicorn/uwsgi.
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
