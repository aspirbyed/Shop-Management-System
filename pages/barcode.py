import sys
import os
os.environ['DYLD_LIBRARY_PATH'] = os.path.dirname(__file__)
import cv2
from pyzbar.pyzbar import decode
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QApplication
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap

# import time

# from AppKit import NSApplication
# from PyObjCTools import AppHelper
# import AVFoundation

class BarcodeScannerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent

        self.setWindowTitle("Scan Barcode")
        self.setGeometry(300, 300, 640, 480)

        # Hardcoded dictionary mapping barcode numbers to product names
        self.barcode_to_product = {
            "9780241389324": "iPhone 15 Pro",
            "8905631871208": "Samsung Galaxy S24 Ultra"
        }

        # self.request_camera_access()

        # Initialize camera
        self.cap = cv2.VideoCapture(0)  # Open the default camera (index 0)
        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            self.reject()
            return

        # Set camera resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Layout
        layout = QVBoxLayout()

        # Video feed display
        self.video_label = QLabel(self)
        self.video_label.setFixedSize(600, 400)
        layout.addWidget(self.video_label)

        # Result display
        self.result_label = QLabel("Scanned Barcode: None")
        layout.addWidget(self.result_label)

        # Product info display
        self.product_label = QLabel("Product: None")
        layout.addWidget(self.product_label)

        # Buttons
        button_layout = QHBoxLayout()
        self.stop_button = QPushButton("Stop Scanning", self)
        self.stop_button.clicked.connect(self.stop_scanning)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Timer for updating the video feed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30ms (~33 FPS)

        self.scanned_barcode = None
        self.last_barcode = None  # To avoid repeated printing
    
    # def request_camera_access(self):
    #     status = AVFoundation.AVCaptureDevice.authorizationStatusForMediaType_(AVFoundation.AVMediaTypeVideo)
        
    #     if status == AVFoundation.AVAuthorizationStatusNotDetermined:
    #         print("Requesting camera access...")
    #         AVFoundation.AVCaptureDevice.requestAccessForMediaType_completionHandler_(
    #             AVFoundation.AVMediaTypeVideo,
    #             lambda granted: print("Granted" if granted else "Denied")
    #         )
    #         time.sleep(2)  # Give some time for permission prompt
        
    #     elif status == AVFoundation.AVAuthorizationStatusAuthorized:
    #         print("Camera access already granted.")
        
    #     else:
    #         print("Camera access denied. Please enable it in System Preferences > Security & Privacy > Camera.")

    def update_frame(self):
        """Capture a frame from the camera, process it for barcodes, and display it."""
        if not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            print("Error: Could not read frame.")
            return

        # Convert the frame to grayscale for barcode detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Decode barcodes in the frame
        barcodes = decode(gray)
        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            self.scanned_barcode = barcode_data

            # Only update if this is a new barcode
            if barcode_data != self.last_barcode:
                self.result_label.setText(f"Scanned Barcode: {barcode_data}")
                self.last_barcode = barcode_data

                # Map the barcode to a product name
                product_name = self.barcode_to_product.get(barcode_data, "Not found")
                self.product_label.setText(f"Product: {product_name}")

            # Draw a rectangle around the barcode
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Display the barcode data on the frame
            cv2.putText(frame, f"{barcode_data}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Convert the frame to QImage for display in PyQt
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.video_label.setPixmap(pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio))

    def stop_scanning(self):
        """Stop the camera, timer, and close the dialog."""
        if self.timer.isActive():
            self.timer.stop()
        if self.cap.isOpened():
            self.cap.release()
        self.accept()

    def get_scanned_barcode(self):
        """Return the scanned barcode data."""
        return self.scanned_barcode

    def get_product_name(self):
        """Return the product name corresponding to the scanned barcode."""
        if self.scanned_barcode is None:
            return None
        return self.barcode_to_product.get(self.scanned_barcode, "Not found")

    def closeEvent(self, event):
        """Ensure the camera and timer are stopped when the dialog is closed."""
        if self.timer.isActive():
            self.timer.stop()
        if self.cap.isOpened():
            self.cap.release()
        event.accept()

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     dialog = BarcodeScannerDialog()
#     if dialog.exec_():
#         product_name = dialog.get_product_name()
#         print(f"Scanned Product: {product_name}")
#     sys.exit(app.exec_())
