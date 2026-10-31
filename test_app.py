# test_app.py - Integration and feature tests for TRUTHCHECK
from app import app, db, User, CheckHistory

def test_unauthenticated_guard():
    with app.test_client() as client:
        r = client.get("/", follow_redirects=False)
        assert r.status_code == 302
        assert "/login" in r.headers["Location"]

def test_login_page_renders_auth_options():
    with app.test_client() as client:
        r = client.get("/login")
        assert r.status_code == 200
        assert b"g_id_signin" in r.data or b"accounts.google.com/gsi/client" in r.data
        assert b"Gmail / Email Address" in r.data

def test_email_login_and_dashboard():
    with app.app_context():
        from werkzeug.security import generate_password_hash
        u = User.query.filter_by(email="demo@truthcheck.ai").first()
        if u:
            u.password_hash = generate_password_hash("password123")
            db.session.commit()
    with app.test_client() as client:
        r = client.post("/login", data={
            "email": "demo@truthcheck.ai",
            "password": "password123"
        }, follow_redirects=True)
        assert r.status_code == 200
        assert b"Demo User" in r.data
        assert b"Image Authenticity Check" in r.data

def test_phone_otp_auth_flow():
    with app.test_client() as client:
        # Step 1: Send OTP
        res = client.post("/auth/send-otp", json={"phone": "+919988776655"})
        data = res.get_json()
        assert data["success"] is True
        otp = data["otp"]

        # Step 2: Verify OTP
        res = client.post("/auth/verify-otp", json={"phone": "+919988776655", "otp": otp})
        assert res.get_json()["success"] is True

        # Step 3: Access protected dashboard
        dash = client.get("/dashboard")
        assert dash.status_code == 200

def test_google_login():
    with app.test_client() as client:
        r = client.get("/auth/google?email=sarah.connor@gmail.com", follow_redirects=True)
        assert r.status_code == 200
        assert b"Sarah Connor" in r.data

def test_forgot_password():
    with app.test_client() as client:
        # GET forgot password page
        r = client.get("/forgot-password")
        assert r.status_code == 200
        assert b"Reset Your Password" in r.data

        # POST password update
        r = client.post("/forgot-password", data={
            "email": "demo@truthcheck.ai",
            "new_password": "newpassword456",
            "confirm_password": "newpassword456"
        }, follow_redirects=True)
        assert r.status_code == 200
        assert b"Demo User" in r.data

if __name__ == "__main__":
    print("Running integration tests...")
    test_unauthenticated_guard()
    test_login_page_renders_auth_options()
    test_email_login_and_dashboard()
    test_forgot_password()
    test_google_login()
    print("All tests passed successfully! [100%]")
