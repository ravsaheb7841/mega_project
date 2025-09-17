from flask import Flask, render_template, request
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

try:
    model = load_model("model/skin_cnn_model.keras")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

classes = ['Acne', 'Eczema', 'Psoriasis', 'Rosacea', 'Vitiligo']

@app.route("/", methods=["GET", "POST"])
def index():
    pred_class = None
    error_message = None  # to display error if needed

    if request.method == "POST":
        try:
            if "file" not in request.files:
                error_message = "No file part in the request."
                raise ValueError(error_message)

            file = request.files["file"]
            if file.filename == "":
                error_message = "No file selected."
                raise ValueError(error_message)

            filename = secure_filename(file.filename)
            upload_folder = os.path.join("static", "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            # Image preprocess and prediction
            img = image.load_img(filepath, target_size=(128, 128))
            img_array = image.img_to_array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            if model is None:
                error_message = "Model is not loaded."
                raise ValueError(error_message)

            prediction = model.predict(img_array)
            pred_class = classes[np.argmax(prediction)]

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            pred_class = None

    return render_template("index.html", pred_class=pred_class, error_message=error_message)

if __name__ == "__main__":
    app.run(debug=True)
