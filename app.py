from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os

from modules.image_detector import detect_image
from modules.text_analysis import analyze_text
from modules.result_aggregator import aggregate_results


app = Flask(__name__)


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "uploads"
)

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# HELPER FUNCTION
# =========================================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# AUTH ROUTES
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "auth/login.html"
    )


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "auth/register.html"
    )


# =========================================================
# MAIN PAGES
# =========================================================

@app.route("/")
@app.route("/dashboard")
def dashboard():

    return render_template(
        "dashboard.html"
    )


@app.route("/history")
def history():

    return render_template(
        "history.html"
    )


@app.route("/profile")
def profile():

    return render_template(
        "profile.html"
    )


@app.route("/settings")
def settings():

    return render_template(
        "settings.html"
    )


@app.route("/about")
def about():

    return render_template(
        "about.html"
    )


# =========================================================
# CHECKER PAGES
# =========================================================

@app.route("/image-check")
def image_check():

    return render_template(
        "image_check.html"
    )


@app.route("/text-check")
def text_check():

    return render_template(
        "text_check.html"
    )


@app.route("/video-check")
def video_check():

    return render_template(
        "video_check.html"
    )


# =========================================================
# TEXT ONLY CHECK
# =========================================================

@app.route(
    "/text-check-submit",
    methods=["POST"]
)
def text_check_submit():

    text = request.form.get(
        "text",
        ""
    ).strip()

    # -----------------------------
    # VALIDATION
    # -----------------------------

    if not text:

        return render_template(
            "text_check.html",
            error="Please enter some text to analyze."
        )

    # -----------------------------
    # TEXT ANALYSIS
    # -----------------------------

    try:

        text_result = analyze_text(
            text
        )

    except Exception as e:

        return render_template(
            "text_check.html",
            error=f"Text analysis failed: {str(e)}"
        )

    # -----------------------------
    # FINAL TEXT RESULT
    # -----------------------------

    final_result = (
        text_result
        .get("ai_detection", {})
        .get(
            "label",
            "Analysis Completed"
        )
    )

    # -----------------------------
    # RESULT PAGE
    # -----------------------------

    return render_template(

        "result.html",

        # No image in text-only check
        image_filename=None,

        caption=text,

        image_result=None,

        text_result=text_result,

        overall_result=None,

        final_result=final_result
    )


# =========================================================
# IMAGE + TEXT CHECK
# =========================================================

@app.route(
    "/check",
    methods=["POST"]
)
def check_content():

    # =====================================================
    # GET INPUTS
    # =====================================================

    image = request.files.get(
        "image"
    )

    caption = request.form.get(
        "caption",
        ""
    ).strip()


    # =====================================================
    # IMAGE VALIDATION
    # =====================================================

    if not image or image.filename == "":

        return render_template(
            "image_check.html",
            error="Please upload an image."
        )


    if not allowed_file(
        image.filename
    ):

        return render_template(
            "image_check.html",
            error=(
                "Only PNG, JPG, JPEG and WEBP "
                "images are allowed."
            )
        )


    # =====================================================
    # SAVE IMAGE
    # =====================================================

    filename = secure_filename(
        image.filename
    )

    image_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    image.save(
        image_path
    )


    # =====================================================
    # IMAGE ANALYSIS
    # =====================================================

    try:

        image_result = detect_image(
            image_path
        )

    except Exception as e:

        image_result = {

            "status": "error",

            "label": "Image Analysis Failed",

            "message": str(e),

            "ai_probability": 0,

            "real_probability": 0
        }


    # =====================================================
    # TEXT ANALYSIS
    # =====================================================

    if caption:

        try:

            text_result = analyze_text(
                caption
            )

        except Exception as e:

            text_result = {

                "ai_detection": {

                    "label":
                    "Text Analysis Failed",

                    "confidence": 0
                },

                "similarity_results": [],

                "highest_match": None,

                "error": str(e)
            }

    else:

        text_result = {

            "ai_detection": {

                "label":
                "No Text Provided",

                "confidence": 0
            },

            "similarity_results": [],

            "highest_match": None
        }


    # =====================================================
    # OVERALL ANALYSIS
    # =====================================================

    try:

        overall_result = aggregate_results(

            image_result,

            text_result
        )

    except Exception as e:

        overall_result = {

            "status": "error",

            "label":
            "Overall Analysis Failed",

            "score": 0,

            "message": str(e)
        }


    # =====================================================
    # FINAL RESULT
    # =====================================================

    final_result = overall_result.get(

        "label",

        "Analysis Completed"
    )


    # =====================================================
    # RESULT PAGE
    # =====================================================

    return render_template(

        "result.html",

        # IMPORTANT:
        # Only filename is sent to HTML.
        # NOT Windows filesystem path.

        image_filename=filename,

        caption=caption,

        image_result=image_result,

        text_result=text_result,

        overall_result=overall_result,

        final_result=final_result
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(

        debug=True,

        port=5000
    )