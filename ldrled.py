import cv2
import serial
import numpy as np
import threading
import time
from collections import deque

# Initialize Serial Communication with Arduino
ser = serial.Serial('COM3', 9600, timeout=0.1)
time.sleep(2)

# Initialize webcam
cap = cv2.VideoCapture(0)  
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  
cap.set(cv2.CAP_PROP_EXPOSURE, -6)  
cap.set(cv2.CAP_PROP_GAIN, 0)  

# Buffer for LDR values (moving average filter)
ldr_buffer = deque(maxlen=10)  
ldr_value = None
ldr_lock = threading.Lock()

# Track LED state to avoid sending redundant commands
led_on = False

# FPS Calculation
prev_time = time.time()

def read_serial():
    """Continuously read LDR values from Arduino in a separate thread."""
    global ldr_value
    while True:
        try:
            raw_ldr = ser.readline().decode().strip()
            if raw_ldr.isdigit():  
                with ldr_lock:
                    ldr_buffer.append(int(raw_ldr))
                    ldr_value = sum(ldr_buffer) / len(ldr_buffer)
        except Exception as e:
            continue

# Start serial reading in a separate thread
threading.Thread(target=read_serial, daemon=True).start()

def adjust_camera_settings(ldr_value):
    """Adjust camera ISO, exposure, and gain based on LDR value."""
    
    if ldr_value > 975:  # Extreme sunlight
        cap.set(cv2.CAP_PROP_GAIN, 1)  
        cap.set(cv2.CAP_PROP_EXPOSURE, -7)
    elif 950 < ldr_value <= 975:  # Very bright sunlight
        cap.set(cv2.CAP_PROP_GAIN, 1.5)
        cap.set(cv2.CAP_PROP_EXPOSURE, -6.5)
    elif 920 < ldr_value <= 950:  # Bright daylight
        cap.set(cv2.CAP_PROP_GAIN, 2)
        cap.set(cv2.CAP_PROP_EXPOSURE, -6)
    elif 880 < ldr_value <= 920:  # Indoor shade start
        cap.set(cv2.CAP_PROP_GAIN, 2.5)
        cap.set(cv2.CAP_PROP_EXPOSURE, -5.5)
    elif 810 < ldr_value <= 880:  # Bright indoor near windows
        cap.set(cv2.CAP_PROP_GAIN, 3)
        cap.set(cv2.CAP_PROP_EXPOSURE, -5)
    elif 750 < ldr_value <= 810:  # Well-lit indoor
        cap.set(cv2.CAP_PROP_GAIN, 3.5)
        cap.set(cv2.CAP_PROP_EXPOSURE, -4.5)
    elif 680 < ldr_value <= 750:  # Normal indoor lighting
        cap.set(cv2.CAP_PROP_GAIN, 3.75)
        cap.set(cv2.CAP_PROP_EXPOSURE, -4.25)
    elif 600 < ldr_value <= 680:  # Slightly dim indoor
        cap.set(cv2.CAP_PROP_GAIN, 4)
        cap.set(cv2.CAP_PROP_EXPOSURE, -4)
    elif 500 < ldr_value <= 600:  # Dim indoor
        cap.set(cv2.CAP_PROP_GAIN, 4.5)
        cap.set(cv2.CAP_PROP_EXPOSURE, -3.5)
    elif 400 < ldr_value <= 500:  # Near darkness
        cap.set(cv2.CAP_PROP_GAIN, 4.5)
        cap.set(cv2.CAP_PROP_EXPOSURE, -3)
    else:  # Complete darkness
        cap.set(cv2.CAP_PROP_GAIN, 5.25)
        cap.set(cv2.CAP_PROP_EXPOSURE, -2.75)

def detect_green_led_and_object(frame):
    """Detect both green LED and green objects in the frame."""
    blurred = cv2.GaussianBlur(frame, (9, 9), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # Dynamic thresholding for LED detection
    lower_led = np.array([40, 120, 200])
    upper_led = np.array([90, 255, 255])

    # Green object range (broader)
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])

    # Create masks
    mask_led = cv2.inRange(hsv, lower_led, upper_led)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    # Morphological operations for noise reduction
    kernel = np.ones((5, 5), np.uint8)
    mask_led = cv2.morphologyEx(mask_led, cv2.MORPH_OPEN, kernel, iterations=2)
    mask_led = cv2.morphologyEx(mask_led, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel, iterations=2)
    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Find bounding boxes
    led_box, led_status = find_bounding_box(mask_led, "LED")
    green_box, green_status = find_bounding_box(mask_green, "Green Object")

    return led_box, led_status, green_box, green_status

def find_bounding_box(mask, label):
    """Find bounding box around detected regions."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 100:  
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            if 0.5 < aspect_ratio < 2:  
                return (x, y, w, h), f"{label} ON"
    return None, f"{label} OFF"

print("Program started. Press 'q' to quit.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Adjust camera settings based on LDR value
        with ldr_lock:
            if ldr_value is not None:
                adjust_camera_settings(ldr_value)

        # Detect green LED and green object
        led_box, led_status, green_box, green_status = detect_green_led_and_object(frame)

        # FPS Calculation
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time

        # Logic for drawing bounding boxes and controlling Arduino LED
        bounding_box_visible = False
        
        # Check if LED bounding box exists and draw it
        if led_box is not None:
            x, y, w, h = led_box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2) 
            bounding_box_visible = True
        
        # Check if green object bounding box exists and draw it
        if green_box is not None:
            x, y, w, h = green_box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  
            bounding_box_visible = True
            
        if bounding_box_visible:
            if not led_on:
                ser.write(b'1')
                print("Bounding box detected! Sending '1' to Arduino to turn LED ON")
                led_on = True
        else:
            if led_on:
                ser.write(b'0')
                print("No bounding box detected. Sending '0' to Arduino to turn LED OFF")
                led_on = False

        # Display status, FPS, and LDR value
        with ldr_lock:
            ldr_display = f"LDR: {ldr_value:.2f}" if ldr_value is not None else "LDR: N/A"
        
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(frame, ldr_display, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Display Arduino LED status
        arduino_led_status = "Arduino LED: ON" if led_on else "Arduino LED: OFF"
        cv2.putText(frame, arduino_led_status, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        cv2.imshow("Green LED and Object Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            # Turn off LED before quitting
            ser.write(b'0')
            print("Quitting. Turning OFF Arduino LED.")
            break

except KeyboardInterrupt:
    print("Program interrupted by user")
except Exception as e:
    print(f"Error occurred: {e}")
finally:
    # Clean up resources
    cap.release()
    cv2.destroyAllWindows()
    # Ensure LED is turned off when exiting
    ser.write(b'0')
    ser.close()
    print("Program ended. All resources released.")