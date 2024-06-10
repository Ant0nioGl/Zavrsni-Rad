import cv2
from ultralytics import YOLO
from ultralytics.solutions import object_counter
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

def count_vehicles(file):
    model = YOLO('yolov8n.pt')
    cap = cv2.VideoCapture(file)
    assert cap.isOpened(), "Error reading video file"
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

    # Define line points
    line_points = [(0, h/2 + h/8), (w, h/2 + h/8)]

    # Video writer
    video_writer = cv2.VideoWriter("result.avi",
                                   cv2.VideoWriter_fourcc(*'mp4v'),
                                   fps,
                                   (w, h))

    # Init Object Counter
    counter = object_counter.ObjectCounter()
    counter.set_args(view_img=True,
                     reg_pts=line_points,
                     classes_names=model.names,
                     draw_tracks=True,
                     line_thickness=2)

    while cap.isOpened():
        success, im0 = cap.read()
        if not success:
            print("Video frame is empty or video processing has been successfully completed.")
            break
        tracks = model.track(im0, persist=True, show=False, classes=[2, 3, 5, 7])

        im0 = counter.start_counting(im0, tracks)
        video_writer.write(im0)

    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()

    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.avi')
    os.rename("result.avi", output_path)
    return 'result.avi'

@app.route("/")
def index():
    # Reset uploads folder
    shutil.rmtree('uploads', ignore_errors=True)
    os.makedirs(app.config['UPLOAD_FOLDER'])
    # Reset runs folder
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

@app.route('/upload-count', methods=['POST'])
def upload_file_count():
    if 'file' not in request.files:
        return 'Missing file.'
    file = request.files['file']
    if file.filename == '':
        return 'Please select a file.'
    elif file and check_if_allowed(file.filename):
        file_content = file.read()
        extension = file.filename.rsplit('.', 1)[1].lower()
        if extension in {'mp4', 'mov', 'avi', 'webm'}:
            temp_video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp.mp4')
            with open(temp_video_path, 'wb') as temp_file:
                temp_file.write(file_content)
            prediction = count_vehicles(temp_video_path)
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
