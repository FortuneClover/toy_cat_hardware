# import sys
# sys.path.append('/usr/lib/python3/dist-packages')

# from picamera2 import Picamera2
# import time

# picam2 = Picamera2()
# config = picam2.create_video_configuration(
#     main={"size": (640, 480)}, controls={"FrameRate": 59.18})
# picam2.configure(config)
# picam2.start()

# start = time.time()
# frame_count = 0

# while time.time() - start < 3:
#     frame = picam2.capture_array()
#     frame_count += 1

# fps_actual = frame_count / (time.time() - start)
# print(f"실제 FPS: {fps_actual:.2f}")

# picam2.stop()

import sys
sys.path.append('/usr/lib/python3/dist-packages')

# import os
# from picamera2 import Picamera2
# from picamera2.encoders import H264Encoder
# import time
# from datetime import datetime


# def save_video_picamera2():
#     # 현재 시각 기준으로 폴더 및 파일명 생성
#     now = datetime.now()
#     date_str = now.strftime('%Y-%m-%d')
#     time_str = now.strftime('%H-%M-%S')
#     os.makedirs(f'recordings/{date_str}', exist_ok=True)
#     filepath = f'recordings/{date_str}/{time_str}_recording.mp4'

#     # 카메라 설정
#     picam2 = Picamera2()
#     # video_config = picam2.create_video_configuration(main={"size": (640, 480)})
#     # picam2.configure(video_config)

#     # 인코더 설정 (H.264 → MP4로 저장 가능)
#     encoder = H264Encoder(bitrate=10000000)  # 10 Mbps 비트레이트

#     print(f"[저장 시작] {filepath}")
#     picam2.start_recording(encoder, filepath)

#     # 60초 동안 녹화
#     time.sleep(60)

#     picam2.stop_recording()
#     picam2.close()
#     print(f"[저장 완료] {filepath}")


# if __name__ == "__main__":
#     save_video_picamera2()

import os
import time
from datetime import datetime
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
import subprocess

# 녹화 파일 저장 경로 설정
now = datetime.now()
date_str = now.strftime('%Y-%m-%d')
time_str = now.strftime('%H-%M-%S')
os.makedirs(f'recordings/{date_str}', exist_ok=True)

h264_filepath = f'recordings/{date_str}/{time_str}_recording.h264'
mp4_filepath = f'recordings/{date_str}/{time_str}_recording.mp4'

# Picamera2 초기화
picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(video_config)

# H.264 인코더 및 FileOutput 설정
encoder = H264Encoder()
output = FileOutput(h264_filepath)

# 녹화 시작
print(f"[녹화 시작] {h264_filepath}")
picam2.start_recording(encoder, output)

# 60초 녹화
time.sleep(60)

# 녹화 종료
picam2.stop_recording()
print(f"[녹화 완료] {h264_filepath}")

# ffmpeg를 이용해 H.264 -> MP4 변환
print(f"[MP4 변환 시작] {mp4_filepath}")
subprocess.run([
    "ffmpeg", "-y",
    "-framerate", "30",
    "-i", h264_filepath,
    "-c", "copy",
    mp4_filepath
])
print(f"[MP4 변환 완료] {mp4_filepath}")

# 원본 H.264 파일 삭제
if os.path.exists(h264_filepath):
    os.remove(h264_filepath)
    print(f"[삭제 완료] {h264_filepath}")