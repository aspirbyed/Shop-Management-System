import cv2
from pyzbar.pyzbar import decode

def scan_barcode():
    # Open the default camera (index 0)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    print("Camera opened. Scanning for barcodes... (Press 'q' to quit, 'r' to reset)")

    # Variable to store the last scanned barcode
    last_barcode = None

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Convert the frame to grayscale for barcode detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Decode barcodes in the frame
        barcodes = decode(gray)
        for barcode in barcodes:
            # Extract barcode data
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type

            # Only print if this is a new barcode
            if barcode_data != last_barcode:
                print(f"Barcode Detected - Type: {barcode_type}, Data: {barcode_data}")
                last_barcode = barcode_data

            # Draw a rectangle around the barcode
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Display the barcode data on the frame
            cv2.putText(frame, f"{barcode_type}: {barcode_data}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Display the frame
        cv2.imshow('Barcode Scanner', frame)

        # Check for key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Quit the program
            break
        elif key == ord('r'):  # Reset the last scanned barcode
            last_barcode = None
            print("Reset: Ready to scan a new barcode.")

    # Release the camera and close windows
    cap.release()
    cv2.destroyAllWindows()
    print("Camera closed.")

# if __name__ == '__main__':
#     try:
#         scan_barcode()
#     except ImportError as e:
#         print(f"ImportError: {str(e)}")
#         print("Ensure the zbar library is installed. On macOS, run: 'brew install zbar'")
#     except Exception as e:
#         print(f"An unexpected error occurred: {str(e)}")