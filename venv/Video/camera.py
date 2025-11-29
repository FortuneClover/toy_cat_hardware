# Camera.py
import sys
sys.path.append('/usr/lib/python3/dist-packages')

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FileOutput
from datetime import datetime
import cv2
import numpy as np
import os
import time
import subprocess
import threading

# 카메라 보정 파라미터
fx, fy, cx, cy = 2852, 2855, 1640, 1232
k1, k2, k3, k4 = -0.317640, -0.099809, -0.006748, 0.010827
dist = np.array([k1, k2, k3, k4], dtype=np.float64)
mtx = np.array([[fx, 0, cx],
                [0, fy, cy],
                [0, 0, 1]], dtype=np.float64)

class Camera:
    def __init__(self, width=640, height=480, framerate=30):
        self.width = width
        self.height = height
        self.framerate = framerate
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_video_configuration(main={"size": (width, height)}))
        self.picam2.start()
        self.picam2.set_controls({"FrameRate": framerate})
        # 🔴 [상태 추가] 녹화 상태 관리 변수
        self.recorder = None 
        self.h264_filepath = None
        self.mp4_filepath = None
        self.encoder = None
        self.output = None

    def get_frame(self, mode="default"):
        """
        실시간 스트리밍을 위해 현재 스트림에서 프레임을 캡처합니다.
        (녹화가 진행 중이더라도 동일 스트림을 사용)
        """
        # 🔴 [핵심] 녹화와 관계없이 단순히 프레임을 캡처하고 반환합니다.
        # 이 함수를 호출하는 /video_feed 엔드포인트는 녹화와 병렬로 실행됩니다
        frame = self.picam2.capture_array()
        if frame.shape[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
        undistorted_frame = cv2.undistort(frame, mtx, dist)
        if mode == "byte":
            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()
        return undistorted_frame

    # ----------------------------------------------------
    # 🚀 1. 녹화 시작 메서드 (Recording Start)
    # ----------------------------------------------------
    def start_recording(self):
        """
        비디오 녹화를 시작합니다. 파일 경로는 자동으로 생성됩니다.
        """

        if self.recorder is not None:
            print("경고: 이미 녹화가 진행 중입니다.")
            return False

        try:
            now = datetime.now()
            date_str = now.strftime('%Y-%m-%d')
            time_str = now.strftime('%H-%M-%S')
            filename = f"{date_str}_{time_str}_recording"

            os.makedirs('recordings', exist_ok=True)
            print("1단계")
            # 1. 파일 경로 설정
            self.h264_filepath = os.path.join('recordings', f"{filename}.h264")
            self.mp4_filepath = os.path.join('recordings', f"{filename}.mp4")
            print("2단계")
            # 2. 레코더 객체 생성 및 설정
            bitrate = int(self.width * self.height * 0.1)
            print("3단계")
            # encoder = H264Encoder(bitrate)
            self.encoder = H264Encoder()
            # output = FileOutput(self.h264_filepath)
            self.output = FileOutput(self.h264_filepath)
            print("4단계")
            # 3. picam2.start_recording()을 사용하여 녹화 시작
            self.picam2.start_recording(self.encoder, self.output)
            print("5단계")
            # 녹화가 시작되었음을 표시하기 위해 self.recorder에 임시 값 할당
            self.recorder = True 
            print("6단계")
            print(f"🎬 녹화 시작: {self.h264_filepath}")
            return True

        except Exception as e:
            print(f"❌ 녹화 시작 오류: {e}")
            # 오류 발생 시 자원 정리 및 상태 초기화
            if self.recorder:
                try: self.picam2.stop_recording()
                except: pass 
            self.recorder = None 
            return False

    def stop_recording_and_convert(self):
        """
        현재 진행 중인 녹화를 중지하고, H.264 파일을 MP4로 변환 후 원본을 삭제합니다.
        """
        if self.recorder is None:
            print("경고: 현재 진행 중인 녹화가 없습니다.")
            return False

        try:
            # 1. 녹화 중지
            self.picam2.stop_recording() 
            print(f"✅ 녹화 중지 완료: {self.h264_filepath}")
            print("1단계")
            
            # 2. FFmpeg을 이용한 H.264 -> MP4 변환
            print(f"[MP4 변환 시작] 대상: {self.mp4_filepath}")
            
            subprocess.run([
                "ffmpeg", "-y",
                "-framerate", str(self.framerate),
                "-i", self.h264_filepath,
                "-c", "copy",
                self.mp4_filepath
            ], check=True, capture_output=True) 

            print(f"[MP4 변환 완료] {self.mp4_filepath}")
            print("2단계")

            # 3. 원본 H.264 삭제
            if os.path.exists(self.h264_filepath):
                os.remove(self.h264_filepath)
                print(f"[H.264 삭제 완료] {self.h264_filepath}")
                print("3단계")
            
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ FFmpeg 변환 오류! (FFmpeg 명령 실행 실패) stderr: {e.stderr.decode()}")
            return False
        except Exception as e:
            print(f"❌ 녹화 중지/변환 중 예상치 못한 오류 발생: {e}")
            return False
        finally:
            # 4. 레코더 상태 초기화 (오류 발생 여부와 관계없이 실행)
            self.recorder = None
            
    # def save_video(self, duration=60):
    #     now = datetime.now()
    #     date_str = now.strftime('%Y-%m-%d')
    #     time_str = now.strftime('%H-%M-%S')
    #     os.makedirs(f'recordings/{date_str}', exist_ok=True)

    #     h264_filepath = f'recordings/{date_str}/{time_str}_recording.h264'
    #     mp4_filepath = f'recordings/{date_str}/{time_str}_recording.mp4'

    #     # H.264 인코더 + FileOutput
    #     encoder = H264Encoder()
    #     output = FileOutput(h264_filepath)

    #     print(f"[녹화 시작] {h264_filepath}")
    #     self.picam2.start_recording(encoder, output)
    #     time.sleep(duration)
    #     self.picam2.stop_recording()
    #     print(f"[녹화 완료] {h264_filepath}")

    #     # ffmpeg를 이용한 H.264 -> MP4 변환
    #     print(f"[MP4 변환 시작] {mp4_filepath}")
    #     subprocess.run([
    #         "ffmpeg", "-y",
    #         "-framerate", str(self.framerate),
    #         "-i", h264_filepath,
    #         "-c", "copy",
    #         mp4_filepath
    #     ], check=True)
    #     print(f"[MP4 변환 완료] {mp4_filepath}")

    #     # 원본 H.264 삭제
    #     if os.path.exists(h264_filepath):
    #         os.remove(h264_filepath)
    #         print(f"[삭제 완료] {h264_filepath}")
