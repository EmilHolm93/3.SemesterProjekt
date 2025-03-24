from picamera2 import Picamera2
import cv2
from pyzbar.pyzbar import decode
import time

valid_amount = [1, 2, 5, 10, 25]

# Initialize the camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)

# Start the camera
picam2.start()
time.sleep(0.1)

print("Starting QR Code Reader. Press Ctrl+C to quit.")

to_send = None

try:
    while True:
        # Capture an image frame
        frame = picam2.capture_array()

        # Decode QR codes using pyzbar
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            try:
                to_send = int(obj.data.decode('utf-8'))
                
                if any(x == to_send for x in valid_amount):
                    print(f"Valid QR Code detected: {to_send}")
                else:
                    print(f"Invalid QR Code detected: {to_send}")
            
            except ValueError:
                print(f"what is wrong with you??? {obj.data.decode('utf-8')} is invalid")

        # Display the resulting frame
        cv2.imshow("QR Code Reader", frame)

        # Break the loop with 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except KeyboardInterrupt:
    print("Exiting.")

# Release resources
cv2.destroyAllWindows()
picam2.stop()
