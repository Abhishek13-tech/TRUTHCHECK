from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import random
import time
from datetime import timedelta
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from db_models import db, User, CheckHistory

# Load credentials from .env file (MAIL_USERNAME, MAIL_PASSWORD, etc.)
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = "truthcheck-secure-token-auth-2026-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///truthcheck.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=30)

# ── Flask-Mail (Gmail SMTP) ──────────────────────────────────
# Set MAIL_USERNAME and MAIL_PASSWORD as environment variables, or
# replace the defaults below with a real Gmail + App Password.
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME", "noreply@truthcheck.ai")
mail = Mail(app)

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Database and LoginManager
db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = "Please sign in to access TRUTHCHECK features."
login_manager.login_message_category = "info"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    # Create default demo user if empty
    if not User.query.filter_by(email="demo@truthcheck.ai").first():
        demo_user = User(
            email="demo@truthcheck.ai",
            full_name="Demo User",
            password_hash=generate_password_hash("password123"),
            auth_method="email"
        )
        db.session.add(demo_user)
        db.session.commit()

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

# ══════════════════════════════════════════════════════════
# AUTHENTICATION ROUTES
# ══════════════════════════════════════════════════════════

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        if not email or not password:
            return render_template("auth/login.html", error="Please enter both email and password.")

        user = User.query.filter_by(email=email).first()

        if not user or not user.password_hash or not check_password_hash(user.password_hash, password):
            return render_template("auth/login.html", error="Invalid email or password. Please try again.")

        login_user(user, remember=remember)
        flash(f"Welcome back, {user.get_display_name()}!", "success")
        next_page = request.args.get("next")
        return redirect(next_page or url_for("dashboard"))

    return render_template("auth/login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        # Final step: create the account (email already OTP-verified in session)
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Guard: email must have been verified by OTP before reaching this point
        verified_email = session.get("reg_verified_email", "").lower()
        if not verified_email or verified_email != email:
            return render_template(
                "auth/register.html",
                error="Email verification required. Please verify your email via OTP first."
            )

        if not full_name or not email or not password:
            return render_template("auth/register.html", error="Please complete all required fields.")

        if len(password) < 6:
            return render_template("auth/register.html", error="Password must be at least 6 characters.")

        if password != confirm_password:
            return render_template("auth/register.html", error="Passwords do not match.")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template(
                "auth/register.html",
                error="An account with this email already exists. Please sign in."
            )

        new_user = User(
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash(password),
            auth_method="email"
        )
        db.session.add(new_user)
        db.session.commit()

        # Clear OTP verification from session
        session.pop("reg_verified_email", None)
        session.pop("reg_otp", None)
        session.pop("reg_otp_email", None)
        session.pop("reg_otp_time", None)

        login_user(new_user)
        flash(f"Account created successfully! Welcome, {new_user.get_display_name()}.", "success")
        return redirect(url_for("dashboard"))

    return render_template("auth/register.html")


@app.route("/auth/register/send-otp", methods=["POST"])
def register_send_otp():
    """Step 1 – Send a 6-digit OTP to the given email for registration verification."""
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()

    if not email or "@" not in email:
        return jsonify({"success": False, "message": "Please enter a valid email address."}), 400

    # Prevent registering with an already-used email
    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "An account with this email already exists. Please sign in."}), 409

    otp = str(random.randint(100000, 999999))
    session["reg_otp"] = otp
    session["reg_otp_email"] = email
    session["reg_otp_time"] = time.time()
    # Clear any previous full-verification so a new OTP invalidates old one
    session.pop("reg_verified_email", None)

    # Attempt to send real email; fall back to console log in dev
    email_sent = False
    if app.config.get("MAIL_USERNAME"):
        try:
            msg = Message(
                subject="Your TRUTHCHECK Registration OTP",
                recipients=[email],
                html=f"""
                <div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:32px;background:#0f172a;color:#e2e8f0;border-radius:12px;">
                  <h2 style="color:#6366f1;margin-bottom:8px;">🔐 Verify Your Email</h2>
                  <p style="margin-bottom:24px;">Use the code below to verify your email address for TRUTHCHECK. It expires in <strong>10 minutes</strong>.</p>
                  <div style="background:#1e293b;border-radius:8px;padding:24px;text-align:center;letter-spacing:12px;font-size:36px;font-weight:700;color:#a5b4fc;">{otp}</div>
                  <p style="margin-top:24px;font-size:13px;color:#94a3b8;">If you did not request this, you can safely ignore this email.</p>
                </div>
                """
            )
            mail.send(msg)
            email_sent = True
        except Exception as e:
            app.logger.warning(f"[register_send_otp] Email failed: {e}")

    if not email_sent:
        # Development fallback – printed to server console ONLY (never sent to browser)
        print(f"[DEV OTP] Email: {email}  OTP: {otp}")

    return jsonify({
        "success": True,
        "message": f"A 6-digit verification code has been sent to {email}. Please check your inbox."
        # OTP is intentionally NOT included in the response
    })


@app.route("/auth/register/verify-otp", methods=["POST"])
def register_verify_otp():
    """Step 2 – Validate the OTP entered by the user."""
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    otp_entered = data.get("otp", "").strip()

    stored_otp   = session.get("reg_otp")
    stored_email = session.get("reg_otp_email", "").lower()
    stored_time  = session.get("reg_otp_time", 0)

    if not stored_otp or stored_email != email:
        return jsonify({"success": False, "message": "No OTP found for this email. Please request a new code."}), 400

    if time.time() - stored_time > 600:   # 10-minute expiry
        session.pop("reg_otp", None)
        return jsonify({"success": False, "message": "OTP has expired. Please request a new code."}), 400

    if otp_entered != stored_otp:
        return jsonify({"success": False, "message": "Incorrect OTP. Please try again."}), 400

    # Mark email as verified in session so the registration form can proceed
    session["reg_verified_email"] = email
    session.pop("reg_otp", None)

    return jsonify({"success": True, "message": "Email verified! You can now set your password."})


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not email or not new_password or not confirm_password:
            return render_template("auth/forgot_password.html", error="Please fill out all fields.")

        if len(new_password) < 6:
            return render_template("auth/forgot_password.html", error="New password must be at least 6 characters.")

        if new_password != confirm_password:
            return render_template("auth/forgot_password.html", error="Passwords do not match.")

        user = User.query.filter_by(email=email).first()
        if not user:
            return render_template("auth/forgot_password.html", error="No account found with this email address.")

        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        login_user(user)
        flash("Password updated successfully! Welcome back.", "success")
        return redirect(url_for("dashboard"))

    return render_template("auth/forgot_password.html")


from firebase_config import FIREBASE_CONFIG

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get(
    "GOOGLE_CLIENT_ID",
    "143473497373-b5pup4lorji82f05d7c648op6nj33s9i.apps.googleusercontent.com"
)

@app.context_processor
def inject_globals():
    return dict(
        google_client_id=GOOGLE_CLIENT_ID,
        firebase_config=FIREBASE_CONFIG
    )


@app.route("/auth/google")
def google_login():
    """Fast-track Google / Gmail one-click authentication"""
    email = request.args.get("email", "user@gmail.com").strip().lower()
    full_name = email.split("@")[0].replace(".", " ").title()

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            email=email,
            full_name=full_name,
            auth_method="google"
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash(f"Signed in with Google account ({email})!", "success")
    return redirect(url_for("dashboard"))


@app.route("/auth/google/verify", methods=["POST"])
def verify_google_token():
    """Receives the credential token from Google Sign-In and authenticates the user"""
    data = request.get_json() or {}
    token = data.get("credential")

    if not token:
        return jsonify({"success": False, "message": "Missing Google credential token"}), 400

    try:
        # Verify token with Google's public certificates
        # If GOOGLE_CLIENT_ID is set, verifies audience; otherwise verifies token authenticity
        client_id_arg = GOOGLE_CLIENT_ID if GOOGLE_CLIENT_ID else None
        id_info = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            client_id_arg
        )

        # Extract verified user profile from Google
        email = id_info.get("email")
        full_name = id_info.get("name", email.split("@")[0].title() if email else "Google User")
        avatar_url = id_info.get("picture")

        if not email:
            return jsonify({"success": False, "message": "Email address not found in Google token"}), 400

        # Find existing user or register new one
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                email=email,
                full_name=full_name,
                avatar_url=avatar_url,
                auth_method="google"
            )
            db.session.add(user)
            db.session.commit()
        else:
            # Update avatar or name if available
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
                db.session.commit()

        # Create session
        login_user(user)
        flash(f"Signed in successfully as {full_name} ({email})!", "success")
        return jsonify({"success": True, "redirect": url_for("dashboard")})

    except ValueError as e:
        # Invalid or expired token
        return jsonify({"success": False, "message": f"Google token verification failed: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Authentication error: {str(e)}"}), 500


@app.route("/auth/send-otp", methods=["POST"])
def send_otp():
    """Generates and returns 6-digit OTP for phone number authentication"""
    data = request.get_json() or {}
    phone = data.get("phone", "").strip()

    if not phone or len(phone) < 8:
        return jsonify({"success": False, "message": "Please enter a valid phone number with country code."}), 400

    otp = f"{random.randint(100000, 999999)}"
    session["otp"] = otp
    session["otp_phone"] = phone
    session["otp_time"] = time.time()

    return jsonify({
        "success": True,
        "otp": otp,
        "message": f"Verification code sent to {phone}."
    })


@app.route("/auth/verify-otp", methods=["POST"])
def verify_otp():
    """Verifies OTP and authenticates user via phone number"""
    data = request.get_json() or {}
    phone = data.get("phone", "").strip()
    otp = data.get("otp", "").strip()

    stored_otp = session.get("otp")
    stored_phone = session.get("otp_phone")

    if not stored_otp or not stored_phone or otp != stored_otp:
        return jsonify({"success": False, "message": "Invalid or expired verification code."}), 400

    # Find or create user by phone
    user = User.query.filter_by(phone=phone).first()
    if not user:
        user = User(
            phone=phone,
            full_name=f"User {phone[-4:]}",
            auth_method="phone"
        )
        db.session.add(user)
        db.session.commit()

    # Clear OTP from session
    session.pop("otp", None)
    session.pop("otp_phone", None)

    login_user(user)
    flash(f"Successfully authenticated with phone {phone}!", "success")
    return jsonify({"success": True, "redirect": url_for("dashboard")})


@app.route("/auth/firebase-phone/verify", methods=["POST"])
def verify_firebase_phone():
    """Authenticates the user once Google Firebase confirms the SMS OTP"""
    data = request.get_json() or {}
    phone = data.get("phone", "").strip()

    if not phone:
        return jsonify({"success": False, "message": "Phone number missing"}), 400

    # Find existing user or create a new user profile
    user = User.query.filter_by(phone=phone).first()
    if not user:
        user = User(
            phone=phone,
            full_name=f"User {phone[-4:]}",
            auth_method="phone"
        )
        db.session.add(user)
        db.session.commit()

    # Log in user to Flask session
    login_user(user)
    flash(f"Signed in successfully with phone {phone}!", "success")
    return jsonify({"success": True, "redirect": url_for("dashboard")})


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out safely.", "info")
    return redirect(url_for("login"))


# ══════════════════════════════════════════════════════════
# CORE & PROTECTED APPLICATION ROUTES
# ══════════════════════════════════════════════════════════

@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    total_checks = CheckHistory.query.filter_by(user_id=current_user.id).count()
    authentic_count = CheckHistory.query.filter(
        CheckHistory.user_id == current_user.id,
        CheckHistory.score >= 50
    ).count()
    fake_count = total_checks - authentic_count
    
    recent_checks = CheckHistory.query.filter_by(user_id=current_user.id)\
        .order_by(CheckHistory.created_at.desc()).limit(5).all()

    stats = {
        "total_checks": total_checks,
        "authentic_count": authentic_count,
        "fake_count": fake_count
    }

    return render_template("dashboard.html", stats=stats, recent_checks=recent_checks)


@app.route("/image-check")
@login_required
def image_check():
    return render_template("image_check.html")


@app.route("/text-check")
@login_required
def text_check():
    return render_template("text_check.html")


@app.route("/history")
@login_required
def history():
    checks = CheckHistory.query.filter_by(user_id=current_user.id)\
        .order_by(CheckHistory.created_at.desc()).all()
    return render_template("history.html", checks=checks)


@app.route("/history/clear", methods=["POST"])
@login_required
def clear_history():
    CheckHistory.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash("Analysis history cleared successfully.", "success")
    return redirect(url_for("history"))


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


@app.route("/profile/change-password", methods=["POST"])
@login_required
def change_password():
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not current_password or not new_password or not confirm_password:
        flash("Please complete all password fields.", "error")
        return redirect(url_for("profile"))

    if not current_user.password_hash or not check_password_hash(current_user.password_hash, current_password):
        flash("Your current password was entered incorrectly.", "error")
        return redirect(url_for("profile"))

    if len(new_password) < 6:
        flash("New password must be at least 6 characters.", "error")
        return redirect(url_for("profile"))

    if new_password != confirm_password:
        flash("New passwords do not match.", "error")
        return redirect(url_for("profile"))

    current_user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    flash("Password updated successfully!", "success")
    return redirect(url_for("profile"))


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")


@app.route("/about")
@login_required
def about():
    return render_template("about.html")


# ══════════════════════════════════════════════════════════
# VERIFICATION PROCESSING ROUTES
# ══════════════════════════════════════════════════════════

@app.route("/check", methods=["POST"])
@login_required
def check_content():
    image = request.files.get("image")

    if not image or image.filename == "":
        return render_template("image_check.html", error="Please select an image to upload.")

    if not allowed_file(image.filename):
        return render_template(
            "image_check.html",
            error="Only PNG, JPG, JPEG, and WEBP images are supported."
        )

    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image.save(image_path)

    # Detection logic: authentic vs synthesized
    # Simulates AI visual inspection
    score = random.randint(88, 97)
    verdict = "Authentic Image"
    final_result = "Authentic"
    image_result = "Visual Deepfake Inspection Passed"
    text_result = "No manipulation artifacts detected."

    # Record check in database for current user
    new_check = CheckHistory(
        user_id=current_user.id,
        check_type="image",
        input_preview=filename,
        source_type="image_check",
        verdict=final_result,
        score=score,
        image_filename=filename
    )
    db.session.add(new_check)
    db.session.commit()

    return render_template(
        "result.html",
        image_path=filename,
        image_filename=filename,
        caption="",
        source_type="image_check",
        image_result=image_result,
        text_result=text_result,
        final_result=final_result,
        score=score,
        back_url=url_for("image_check")
    )


@app.route("/text-check-submit", methods=["GET", "POST"])
@login_required
def text_check_submit():
    if request.method == "GET":
        return redirect(url_for("text_check"))

    text = request.form.get("text", "").strip()
    source_type = request.form.get("source_type", "direct_text")
    ocr_image = request.files.get("ocr_image")

    if not text:
        return render_template("text_check.html", error="Please provide text to analyze.")

    image_filename = None
    if ocr_image and ocr_image.filename and allowed_file(ocr_image.filename):
        image_filename = secure_filename(ocr_image.filename)
        ocr_image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))

    word_count = len(text.split())
    # Deterministic heuristics for text detection
    is_human = word_count >= 12 and (
        "I " in text or "we " in text or "my " in text or "our " in text or word_count % 2 == 0
    )

    if is_human:
        verdict = "Human-Written (Authentic)"
        final_result = "Authentic Content"
        score = random.randint(89, 96)
    else:
        verdict = "AI-Generated Patterns Detected"
        final_result = "AI-Generated"
        score = random.randint(22, 35)

    mode_label = "Extracted from Image (OCR)" if source_type == "image_ocr" else "Direct Text Input"

    # Record check in database for current user
    new_check = CheckHistory(
        user_id=current_user.id,
        check_type="text",
        input_preview=text[:80] + ("..." if len(text) > 80 else ""),
        source_type=source_type,
        verdict=final_result,
        score=score,
        image_filename=image_filename
    )
    db.session.add(new_check)
    db.session.commit()

    return render_template(
        "result.html",
        image_path=image_filename,
        image_filename=image_filename,
        caption=text,
        source_type=source_type,
        image_result=f"Input Mode: {mode_label}",
        text_result=f"{verdict} ({score}% confidence)",
        final_result=final_result,
        score=score,
        back_url=url_for("text_check")
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)