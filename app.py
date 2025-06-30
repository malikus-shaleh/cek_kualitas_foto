from flask import Flask, request, render_template, redirect, url_for
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Fungsi mendeteksi ketajaman (blur) menggunakan Variance of Laplacian
def detect_blur(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if laplacian_var < 100:
        return "Kabur", laplacian_var
    else:
        return "Tajam", laplacian_var

# Fungsi mendeteksi noise berdasarkan perbedaan dengan median blur
def detect_noise(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    median = cv2.medianBlur(gray, 3)
    noise = cv2.absdiff(gray, median)
    noise_level = np.mean(noise)
    if noise_level < 5:
        return "Rendah", noise_level
    elif noise_level < 15:
        return "Sedang", noise_level
    else:
        return "Tinggi", noise_level

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':    
        if 'image' not in request.files:
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image = cv2.imread(filepath)

            sharpness, sharpness_score = detect_blur(image)
            noise, noise_score = detect_noise(image)

            # Menentukan kesimpulan dan link rekomendasi
            if sharpness == "Kabur" and noise == "Tinggi":
                conclusion = "Gambar Anda buram dan banyak noise."
                link_rekomendasi = "https://picwish.com/id/unblur-image-portrait"
            elif sharpness == "Kabur":
                conclusion = "Gambar Anda buram."
                link_rekomendasi = "https://picwish.com/id/unblur-image-portrait"
            elif noise == "Tinggi":
                conclusion = "Gambar Anda jernih namun memiliki noise tinggi."
                link_rekomendasi = "https://cutout.pro/photo-enhancer"
            else:
                conclusion = "Gambar Anda jernih dan berkualitas baik."
                link_rekomendasi = "https://www.iloveimg.com/id/kompres-gambar"

            return render_template('result.html',
                                   filename=filename,
                                   sharpness=sharpness,
                                   sharpness_score=round(sharpness_score, 2),
                                   noise=noise,
                                   noise_score=round(noise_score, 2),
                                   conclusion=conclusion,
                                   link_rekomendasi=link_rekomendasi)
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return redirect(url_for('static', filename='uploads/' + filename))

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, host='0.0.0.0')
