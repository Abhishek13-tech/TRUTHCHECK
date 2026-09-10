from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from modules.text_detector import detect_text
from modules.image_detector import detect_image
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


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/check", methods=["POST"])
def check_content():

    image = request.files.get("image")
    caption = request.form.get("caption", "").strip()

    if not image or image.filename == "":
        return render_template(
            "index.html",
            error="Please upload an image."
        )

    if not allowed_file(image.filename):
        return render_template(
            "index.html",
            error="Only PNG, JPG, JPEG and WEBP images are allowed."
        )

    filename = secure_filename(image.filename)

    image_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    image.save(image_path)

    # AI Image Detection
    image_result = detect_image(image_path)

    text_result = detect_text(caption)

    if image_result.get("status") == "success":
        final_result = image_result["label"]
    else:
        final_result = "Image analysis failed"

    return render_template(
        "result.html",
        image_filename=filename,
        caption=caption,
        image_result=image_result,
        text_result=text_result,
        final_result=final_result
    )


if __name__ == "__main__":
    app.run(debug=True)