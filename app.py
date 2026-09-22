from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os

from modules.text_analysis import analyze_text


app = Flask(__name__)


UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create upload folder if it does not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/check", methods=["POST"])
def check_content():

    # Get uploaded image and text
    image = request.files.get("image")
    caption = request.form.get("caption", "").strip()

    # Analyze text if provided
    text_result = (
        analyze_text(caption)
        if caption
        else None
    )

    # Image is optional
    image_path = None

    if image and image.filename != "":

        # Validate image
        if not allowed_file(image.filename):
            return render_template(
                "index.html",
                error="Only PNG, JPG, JPEG and WEBP images are allowed."
            )

        # Secure filename
        filename = secure_filename(image.filename)

        # Create image path
        image_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        # Save image
        image.save(image_path)

    # Image analysis will be connected later
    image_result = "Analysis Pending"

    # Create final text result
    if text_result:

        ai_percentage = (
            text_result["ai_detection"]["ai_percentage"]
        )

        human_percentage = (
            text_result["ai_detection"]["human_percentage"]
        )

        classification = (
            text_result["ai_detection"]["classification"]
        )

        # Web source found
        if text_result["web_source"]:

            similarity = round(
                float(text_result["web_source"]["similarity"]),
                2
            )

            source_status = (
                text_result["web_source"]["status"]
            )

            final_result = (
                f"AI Generated: {ai_percentage}%. "
                f"Human Written: {human_percentage}%. "
                f"Classification: {classification}. "
                f"Web Similarity: {similarity:.2f}%. "
                f"Status: {source_status}."
            )

        # No web source found
        else:

            final_result = (
                f"AI Generated: {ai_percentage}%. "
                f"Human Written: {human_percentage}%. "
                f"Classification: {classification}. "
                f"No matching web source found."
            )

    else:

        final_result = "No text provided."

    # Send result to result page
    return render_template(
        "result.html",
        image_path=image_path,
        caption=caption,
        image_result=image_result,
        text_result=text_result,
        final_result=final_result
    )


if __name__ == "__main__":
    app.run(debug=True)