from ultralytics import YOLO
from flask import Flask, render_template, url_for, request, redirect, send_from_directory
import os
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'mov', 'avi', 'webm', 'png', 'jpg', 'jpeg'}


def check_if_allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def predict_image(file):
    model = YOLO('yolov8n.pt')
    # Save the file temporarily
    temp_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'temp.jpg')
    with open(temp_filename, 'wb') as temp_file:
        temp_file.write(file)
    # Predict from the saved file
    results = model.predict(source=temp_filename, conf=0.5, save=True, classes=[2, 3, 5, 7])
    # Delete the temporary file after prediction
    os.remove(temp_filename)
    output_file = os.path.join(app.config['UPLOAD_FOLDER'], 'result.jpg')
    results[0].save(output_file)
    return 'result.jpg'


def predict_video(file):
    model = YOLO('yolov8n.pt')

    # Save the file temporarily
    temp_video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp.mp4')
    with open(temp_video_path, 'wb') as temp_file:
        temp_file.write(file)

    # Predict from the saved video file
    results = model.predict(source=temp_video_path, conf=0.5, save=True, classes=[2, 3, 5, 7])

    # Delete the temporary file after prediction
    os.remove(temp_video_path)

    # Move the predicted video to the UPLOAD_FOLDER
    predicted_video_path = os.path.join('runs', 'detect', 'predict', 'temp.avi')
    final_output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.avi')
    os.rename(predicted_video_path, final_output_path)

    return 'result.avi'


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route("/")
def index():
    shutil.rmtree('runs', ignore_errors=True)
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'Missing file.'
    file = request.files['file']
    if file.filename == '':
        return 'Please select a file.'
    elif file and check_if_allowed(file.filename):
        file_content = file.read()
        extension = file.filename.rsplit('.', 1)[1].lower()
        if extension in {'png', 'jpg', 'jpeg'}:
            prediction = predict_image(file_content)
        elif extension in {'mp4', 'mov', 'avi', 'webm'}:
            prediction = predict_video(file_content)
        else:
            return "Unsupported file type."
        return redirect(url_for('display_file', filename=prediction))
    else:
        return "Please try again."


@app.route('/display_file/<filename>')
def display_file(filename):
    file_url = url_for('uploaded_file', filename=filename)
    return render_template('display.html', file_url=file_url)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/download-video')
def download_video():
    # Make sure 'result.mp4' is placed in the 'static' directory
    return send_from_directory('uploads', 'result.avi', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
