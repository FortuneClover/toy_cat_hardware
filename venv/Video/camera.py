# camera.py 실시간 영상 JPEG 프레임으로 변환코드
import sys
sys.path.append('/usr/lib/python3/dist-packages')

import cv2
from picamera2 import Picamera2
from libcamera import controls
import numpy as np

fx = 2592
fy = 1944
cx = 1296
cy = 972
k1 = -0.317640
k2 = -0.099809
k3 = -0.006748
k4 = 0.010827

dist = np.array([k1, k2, k3, k4], dtype=np.float64)

mtx = np.array([[fx, 0, cx],
                [0, fy, cy],
                [0, 0, 1]], dtype=np.float64)

class Camera:
    def __init__(self):
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_video_configuration(main={"size": (2592, 1944)}))
        self.picam2.start()

    def get_frame(self):
        frame = self.picam2.capture_array()
        if frame.shape[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
        undistorted_frame = cv2.undistort(frame, mtx, dist)
        ret, jpeg = cv2.imencode('.jpg', frame)

        return jpeg.tobytes()