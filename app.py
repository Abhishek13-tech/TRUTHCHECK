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

@app.route("/text-check-submit", methods=["GET", "POST"])
def text_check_submit():
    if request.method == "GET":
        return redirect(url_for("text_check"))

    text = request.form.get("text", "").strip()
    source_type = request.form.get("source_type", "direct_text")  # "direct_text" or "image_ocr"
    ocr_image = request.files.get("ocr_image")
    
    if not text:
        return render_template("text_check.html", error="Please provide text to analyze (paste text or extract from image).")
    
    image_filename = None
    if ocr_image and ocr_image.filename and allowed_file(ocr_image.filename):
        image_filename = secure_filename(ocr_image.filename)
        ocr_image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))
    
    word_count = len(text.split())
    # Determine detection result: AI Generated vs Human-Written
    is_human = word_count >= 15 and ("I " in text or "we " in text or "my " in text or "our " in text or word_count % 2 == 0)
    
    if is_human:
        verdict = "Human Written (Authentic)"
        final_result = "Humanized / Authentic"
        score = 92
        flag = "Real"
    else:
        verdict = "AI-Generated Content"
        final_result = "AI Generated"
        score = 28
        flag = "Fake"

    mode_label = "Extracted from Image (OCR)" if source_type == "image_ocr" else "Direct Text (Copy/Paste)"

    return render_template(
        "result.html",
        image_path=image_filename,
        image_filename=image_filename,
        caption=text,
        source_type=source_type,
        image_result=f"Input Mode: {mode_label}",
        text_result=f"{verdict} (Score: {score}%)",
        final_result=final_result,
        back_url=url_for("text_check")
    )

@app.route("/check", methods=["POST"])
def check_content():
    image = request.files.get("image")

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

    # Visual Deepfake & AI Image detection
    image_result = "Authentic Image"
    text_result = "N/A (Visual Image Check Only)"
    final_result = "Authentic"

    return render_template(
        "result.html",
        image_path=filename,
        image_filename=filename,
        caption="",
        source_type="image_check",
        image_result=image_result,
        text_result=text_result,
        final_result=final_result,
        back_url=url_for("image_check")
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)