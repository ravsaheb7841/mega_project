import os
from flask import Flask, render_template, request
from keras.models import load_model
from keras.preprocessing import image
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Load model
model = load_model("models/brain_tumor_model.h5")

# Ensure uploads folder exists
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    confidence = None
    file_path = None

    if request.method == "POST":
        file = request.files["file"]
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Preprocess image
            img = image.load_img(filepath, target_size=(128, 128))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0) / 255.0

            # Predict
            predictions = model.predict(img_array)
            tumor_types = ["glioma", "meningioma", "no tumor", "pituitary"]
            predicted_class = np.argmax(predictions)
            result = f"Tumor Type: {tumor_types[predicted_class]}"
            confidence = round(100 * np.max(predictions), 2)

            # relative path for HTML
            file_path = f"uploads/{filename}"

    return render_template("index.html", result=result, confidence=confidence, file_path=file_path)

if __name__ == "__main__":
    app.run(debug=True)
