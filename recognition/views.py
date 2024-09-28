import cv2
import numpy as np
from time import sleep
from django.http import StreamingHttpResponse
from django.shortcuts import render
from ultralytics import YOLO

from recognition.models import PlateRecognition, MotorControlLog
from border.models import Vehicle, BorderCheck

from util import read_license_plate
import RPi.GPIO as GPIO
import threading
from collections import Counter


# Replace with the IP address of your phone stream
url = 'http://192.168.0.102:4747/video'


# Initialize GPIO for servo motor and IR sensor
SERVO_PIN = 18  # Define your servo motor pin
IR_SENSOR_PIN = 23  # Define your IR sensor pin
    
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(IR_SENSOR_PIN, GPIO.IN)  # Set up IR sensor as input

servo = GPIO.PWM(SERVO_PIN, 50)  # PWM at 50Hz
servo.start(0)

# Lock for thread-safe GPIO operations
gpio_lock = threading.Lock()

def set_angle(angle: int) -> None:
    """
    Set the angle of the servo motor.
    :param angle: Angle in degrees (0 to 180).
    """
    if 0 <= angle <= 180:
        duty = angle / 18 + 2
        with gpio_lock:
            servo.ChangeDutyCycle(duty)
        sleep(0.2)  # Reduced sleep time for faster operation
        with gpio_lock:
            servo.ChangeDutyCycle(0)
    else:
        print("Invalid angle. Angle must be between 0 and 180.")

def open_gate():
    """Function to actuate the servo motor and open the gate."""
    threading.Thread(target=_open_gate_thread).start()

def _open_gate_thread():
    set_angle(180)
    sleep(5)  # Reduced sleep time
    set_angle(80)
    
    
# Load YOLO model once at startup
license_plate_detector = YOLO('license_plate_detector.pt')  # Ensure the model is optimized

def is_ir_sensor_triggered():
    """
    Check if the IR sensor is triggered (obstacle detected).
    The function returns True when the IR sensor output is LOW, 
    indicating an obstacle is present.
    """
    return GPIO.input(IR_SENSOR_PIN) == GPIO.LOW


def generate_video(video_path):
    """Stream video from the file and perform detection."""
    frame_number = 0
    frame_skip = 2  # Process every 3rd frame for speed
    plate_list = []
    plate_limit = 0

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Check if video opened successfully
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("End of video file or error reading frame.")
                break

            if frame_number % (frame_skip + 1) == 0:
                if is_ir_sensor_triggered():
                    # Resize frame for faster processing
                    resized_frame = cv2.resize(frame, (640, 480))
                    
                    # Convert to RGB as YOLO expects RGB images
                    image = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

                    # DETECT LICENSE PLATES
                    results = license_plate_detector(image, verbose=False)
                    license_plates = results[0]

                    for license_plate in license_plates.boxes.data.tolist():
                        x1, y1, x2, y2, score, class_id = license_plate

                        # Ensure coordinates are within frame boundaries
                        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                        x1 = max(x1, 0)
                        y1 = max(y1, 0)
                        x2 = min(x2, resized_frame.shape[1])
                        y2 = min(y2, resized_frame.shape[0])

                        # Crop and preprocess the license plate region
                        license_plate_crop = resized_frame[y1:y2, x1:x2]
                        license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
                        _, license_plate_crop_thresh = cv2.threshold(
                            license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV
                        )

                        # Read license plate number
                        license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)

                        print(f'License plate: {license_plate_text} and score: {license_plate_text_score}')
                        
                        # Checking and processing license plate
                        if license_plate_text != None and license_plate_text_score != None:
                            if len(license_plate_text) == 7 and license_plate_text_score >= 0.3 and plate_limit <= 5:
                                plate_list.append(license_plate_text)
                                plate_limit += 1

                            if plate_limit > 5:
                                # Collecting characters from each position across all detected plates
                                characters_by_position = zip(*plate_list)

                                # Finding the most common character in each position
                                final_chars = [Counter(chars).most_common(1)[0][0] for chars in characters_by_position]

                                # Joining the most common characters to form the probable license plate
                                probable_plate = ''.join(final_chars)

                                print(f'probable plate: {probable_plate}')
                                
                                if probable_plate:
                                    # Check if the vehicle is registered\
                                    
                                    vehicle = Vehicle.objects.filter(license_plates__license_plate_number=probable_plate).first()
                                    
                                    if vehicle:
                                        vehicle = Vehicle.objects.get(license_plates__license_plate_number=probable_plate)

                                        # Check if the vehicle is approved for travel in BorderCheck
                                        border_check = BorderCheck.objects.filter(vehicle=vehicle).first()

                                        if border_check and border_check.is_approved:
                                            # Open the gate automatically if approved
                                            # Log motor control action
                                            MotorControlLog.objects.create(vehicle=vehicle, action="Gate Opened")
                                            open_gate()
                                            print('Gate opened: Vehicle approved for travel')
                                            # Log motor control action
                                            MotorControlLog.objects.create(vehicle=vehicle, action="Gate Closed")
                                        
                                        else:
                                            # Redirect to vehicle creation page if not approved
                                            print(f"Vehicle not approved for travel: Redirecting to vehicle creation page")

                                    else:
                                        # Vehicle not found in the database, redirect to vehicle creation page
                                        print(f"Vehicle not found: Redirecting to vehicle creation page")
                                    
                                    plate_limit = 0
                                    plate_list = []
                                    

                                                                    
                                    
                        # Optionally, draw bounding box and text on the frame
                        cv2.rectangle(resized_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(
                            resized_frame, license_plate_text, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2
                        )

                    # Encode the frame to JPEG
                    _, jpeg = cv2.imencode('.jpg', cv2.cvtColor(resized_frame, cv2.COLOR_RGB2BGR))
                    frame_bytes = jpeg.tobytes()

                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

            frame_number += 1

    finally:
        # Release the video capture object and clean up resources
        cap.release()
        cv2.destroyAllWindows()

def video_feed(request):
    """View to stream the video."""
    video_path = url  # Use your video file path here
    
    try:
        # Stream generator that yields the frames
        stream_generator = generate_video(video_path)

        # Directly return StreamingHttpResponse to stream the video
        return StreamingHttpResponse(stream_generator, content_type='multipart/x-mixed-replace; boundary=frame')
    
    except Exception as e:
        print(f"Error: {e}")
        # Handle errors, potentially redirect if the error indicates a need for redirect
        
        return redirect('border:vehicle-create')
                
def home(request):
    """Home view to show the video feed."""
    return render(request, 'recognition/home.html')
