from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

# --- Auth Routes ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Simulate auth logic, redirect to dashboard
        return redirect(url_for("dashboard"))
    return render_template("auth/login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Simulate registration logic, redirect to dashboard
        return redirect(url_for("dashboard"))
    return render_template("auth/register.html")

# --- Dashboard & Core Pages ---
@app.route("/")
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/history")
def history():
    return render_template("history.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/about")
def about():
    return render_template("about.html")

# --- Checkers ---
@app.route("/image-check")
def image_check():
    return render_template("image_check.html")

@app.route("/text-check")
def text_check():
    return render_template("text_check.html")

@app.route("/text-check-submit", methods=["POST"])
def text_check_submit():
    text = request.form.get("text", "").strip()
    if not text:
        return render_template("text_check.html", error="Please enter some text to analyze.")
    
    # Simulate AI analysis for text
    text_result = "Authentic Text" if len(text) > 50 else "Fake / Misleading Text"
    final_result = "Real" if len(text) > 50 else "Fake"
    
    return render_template(
        "result.html",
        image_path=None,
        caption=text,
        image_result="N/A (Text Analysis Only)",
        text_result=text_result,
        final_result=final_result
    )

@app.route("/video-check")
def video_check():
    return render_template("video_check.html")

@app.route("/check", methods=["POST"])
def check_content():
    image = request.files.get("image")
    caption = request.form.get("caption", "").strip()

    if not image or image.filename == "":
        return render_template(
            "image_check.html",
            error="Please upload an image."
        )

    if not allowed_file(image.filename):
        return render_template(
            "image_check.html",
            error="Only PNG, JPG, JPEG and WEBP images are allowed."
        )

    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image.save(image_path)

    # AI modules will be connected here in the next phase
    image_result = "Authentic Image" 
    text_result = "Authentic Text" if caption else "N/A"
    final_result = "Authentic"

    return render_template(
        "result.html",
        image_path=image_path,
        caption=caption,
        image_result=image_result,
        text_result=text_result,
        final_result=final_result
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)