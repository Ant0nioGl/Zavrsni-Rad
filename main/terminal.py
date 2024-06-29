from ultralytics import YOLO
from ultralytics.solutions import object_counter
from ultralytics.solutions import speed_estimation
import cv2


def track(model, source):
    model.predict(source=source,
                  conf=0.5,
                  save=True,
                  classes=[2, 3, 5, 7])

# https://docs.ultralytics.com/guides/speed-estimation/#arguments-modeltrack
def measure_speed(model, source):
    names = model.model.names

    cap = cv2.VideoCapture(source)
    assert cap.isOpened(), "Error reading video file"
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

    # Video writer
    video_writer = cv2.VideoWriter("speed_estimation.avi",
                                   cv2.VideoWriter_fourcc(*'mp4v'),
                                   fps,
                                   (w, h))

    line_pts = [(0, h/2 + h/8), (w, h/2 + h/8)]

    # Init speed-estimation obj
    speed_obj = speed_estimation.SpeedEstimator()
    speed_obj.set_args(reg_pts=line_pts,
                       names=names,
                       view_img=True)

    while cap.isOpened():

        success, im0 = cap.read()
        if not success:
            print("Video frame is empty or video processing has been successfully completed.")
            break

        tracks = model.track(im0, persist=True, show=False, classes=[2, 3, 5, 7])

        im0 = speed_obj.estimate_speed(im0, tracks)
        video_writer.write(im0)

    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()

# https://docs.ultralytics.com/guides/object-counting/#what-is-object-counting
def count_vehicles(model, source):
    cap = cv2.VideoCapture(source)
    assert cap.isOpened(), "Error reading video file"
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

    # Define line points
    line_points = [(0, h/2 + h/8), (w, h/2 + h/8)]

    # Video writer
    video_writer = cv2.VideoWriter("object_counting_output.avi",
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


def main():
    model = YOLO('yolov8n.pt')
    # model = YOLO("../main/best.pt")

    mode = input("Enter the mode of video you want to display (track, speed, count): ")
    source = "../data/motor.jpg"

    if mode == "track":
        track(model, source)
    elif mode == "speed":
        measure_speed(model, source)
    elif mode == "count":
        count_vehicles(model, source)
    else:
        print("Invalid mode")


main()
