#!/usr/bin/env python3

'''
Streamtest is a simple utility to demonstrate streaming the frames from a tCam-Mini to a canvas in real-time.

'''

from tcam import TCamInterface, enumerateTCamInterfaces
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt


class TCamList:
    def __init__(self):
        super().__init__()
        self.enumerated = False
        self.intfc = []

    def reset(self):
        if self.intfc.count:
            for intfc in self.intfc:
                intfc.shutdown()
        self.enumerated = False
        self.intfc = []


    def enumerate(self):
        if self.enumerated:
            self.reset()
        else:
            intfc = enumerateTCamInterfaces()
            if (intfc.count):
                self.intfc = intfc
                self.enumerated = True

    def shutdown(self):
        self.reset()


class StreamApp(QWidget):
    def __init__(self):
        super().__init__()
        self.current_image = None
        self.initUI()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def initUI(self):
        self.setWindowTitle('tCam Viewer')
        
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
        camList.enumerate()

    def connect_camera(self):
        camList.intfc[0].connect()
        image = camList.intfc[0].getImage()
        self.current_image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
        self.update_image()
        camList.intfc[0].startStream()
        self.timer.start(50)

    def disconnect_camera(self):
        self.timer.stop()
        camList.intfc[0].disconnect()

    def update_frame(self):
        image = camList.intfc[0].getFrame()
        self.current_image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
        self.update_image()

    def update_image(self):
        if self.current_image:
            scaled_image = self.current_image.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(QPixmap.fromImage(scaled_image))

    def resizeEvent(self, event):
        self.update_image()

    def quit_application(self):
        camList.shutdown()
        QApplication.quit()

if __name__ == '__main__':

    camList = TCamList()

    app = QApplication([])
    stream_app = StreamApp()
    stream_app.resize(300, 400)  # Set initial window size
    app.exec_()

    camList.shutdown()

