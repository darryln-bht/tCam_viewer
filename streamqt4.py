#!/usr/bin/env python3

'''
Streamtest is a simple utility to demonstrate streaming the frames from a tCam-Mini to a canvas in real-time.

'''

import base64
import argparse
import numpy as np
from tcam import TCam
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
from array import array

def convert(img):
    dimg = base64.b64decode(img["radiometric"])
    ra = array('H', dimg)

    imgmin = 65535
    imgmax = 0
    for i in ra:
        if i < imgmin:
            imgmin = i
        if i > imgmax:
            imgmax = i
    delta = imgmax - imgmin
    a = np.zeros((120, 160, 3), np.uint8)
    for r in range(0, 120):
        for c in range(0, 160):
            val = int((ra[(r * 160) + c] - imgmin) * 255 / delta)
            if val > 255:
                a[r, c] = [255, 255, 255]
            else:
                a[r, c] = [val, val, val]
    return a

class StreamApp(QWidget):
    def __init__(self, tcam, ip):
        super().__init__()
        self.tcam = tcam
        self.ip = ip
        self.current_image = None

        self.initUI()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def initUI(self):
        self.setWindowTitle('tCam-Mini Video in a Frame')
        
        # Layouts
        self.main_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        
        # Label to display image
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.label)
        
        # Connect button
        self.connect_btn = QPushButton('Connect', self)
        self.connect_btn.clicked.connect(self.connect_camera)
        self.button_layout.addWidget(self.connect_btn)
        
        # Disconnect button
        self.disconnect_btn = QPushButton('Disconnect', self)
        self.disconnect_btn.clicked.connect(self.disconnect_camera)
        self.button_layout.addWidget(self.disconnect_btn)
        
        # Quit button
        self.quit_btn = QPushButton('Quit', self)
        self.quit_btn.clicked.connect(self.quit_application)
        self.button_layout.addWidget(self.quit_btn)
        
        self.main_layout.addLayout(self.button_layout)
        self.setLayout(self.main_layout)
        self.resize(300, 400)
        self.show()

    def connect_camera(self):
        self.tcam.connect(self.ip)
        image = convert(self.tcam.get_image())
        self.current_image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
        self.update_image()
        self.tcam.start_stream()
        self.timer.start(50)

    def disconnect_camera(self):
        self.timer.stop()
        self.tcam.disconnect()

    def update_frame(self):
        if not self.tcam.frameQueue.empty():
            image = convert(self.tcam.get_frame())
            self.current_image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
            self.update_image()

    def update_image(self):
        if self.current_image:
            scaled_image = self.current_image.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(QPixmap.fromImage(scaled_image))

    def resizeEvent(self, event):
        self.update_image()

    def quit_application(self):
        self.disconnect_camera()
        self.tcam.shutdown()
        QApplication.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.prog = "streamtest"
    parser.description = f"{parser.prog} - an example program to stream images from tCam-mini and display as video\n"
    parser.usage = "streamtest.py --ip=<ip address of camera>"
    parser.add_argument("-i", "--ip", help="IP address of the camera")

    args = parser.parse_args()

    if not args.ip:
        args.ip = "192.168.4.1"
        print(f"Using default of {args.ip}")

    tcam = TCam()

    app = QApplication([])
    stream_app = StreamApp(tcam, args.ip)
    stream_app.resize(300, 400)  # Set initial window size
    app.exec_()

    tcam.shutdown()

