# app.py
from flask import Flask, render_template, Response, send_from_directory, jsonify, request
from camera import Camera

import subprocess

import threading
from datetime import datetime, timedelta
import os
import re
import cv2
import time
import requests

import sys
import os

# 현재 파일 기준 상위 폴더 경로 얻기
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 상위 폴더를 모듈 경로에 추가
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from Subtraction import get_total_motion
from Laser import laser_on, laser_off

"""
CORS 보안 문제 발생한다면 
1 pip install flask-cors 
2 from flask_cors import CORS

3 app = Flask(__name__) 
  CORS(app) 이렇게 코드 추가 이하 코드는 동일 
"""
app = Flask(__name__)
VIDEO_PATH = '/home/pc/toy_cat/venv/Video/recordings'
camera = Camera()
CHUNK_SIZE = 8192

# # 백그라운드 실행으로 비디오 저장할 쓰레드 함수
# def save_video():
#     current_date = None
#     video_writer = None
#     fps = 90 #초당 15프레임 

#     #하루마다 새파일로 비디오 녹화
#     try:
#         while True:
#             frame = camera.get_frame()
#             # if frame is None:
#             #     print("❌ 프레임이 None입니다.")
#             # else:
#             #     print("✅ 프레임 캡처 성공:", frame.shape)

#             # # 4채널 → 3채널 BGR로 변환
#             # if frame.shape[2] == 4:
#             #     frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)

#             now = datetime.now()
#             date_str = now.strftime('%Y-%m-%d')
#             minute_str = now.strftime('%Y-%m-%d %H:%M') # 테스트 용으로 1분마다 녹화파일 저장 코드 
#             time_str = now.strftime('%H-%M-%S')
#             #하루마다 새파일 만들고 녹화하는 코드 
#             #if current_date != date_str:
#             if current_date != minute_str: # 테스트 용으로 1분마다 녹화파일 저장 코드
#                 if video_writer:
#                     video_writer.release()

#                 os.makedirs(f'recordings/{date_str}', exist_ok=True)
#                 filepath = f'recordings/{date_str}/{time_str}_recording.mp4'
#                 h, w, _ = frame.shape
#                 fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#                 video_writer = cv2.VideoWriter(filepath, fourcc, fps, (w, h))
#                 #current_date = date_str
#                 current_date = minute_str # 테스트 용으로 1분마다 녹화파일 저장 코드
#                 print(f"[저장 시작] {filepath}")
#             # 비디오 녹화 코드
#             video_writer.write(frame)
#             # print("✔️ 프레임 작성됨")

#             time.sleep(1 / fps)

#     except KeyboardInterrupt:
#             print("녹화 중단됨 (Ctrl+C)")
#             video_writer.release()

# def save_video():
#     current_file = None
#     ffmpeg_proc = None
#     fps = 90  # 카메라에서 capture 속도와 동일하게 설정

#     try:
#         while True:
#             frame = camera.get_frame()  # BGR ndarray 반환
#             if frame is None:
#                 continue  # 프레임이 None이면 건너뛰기

#             # 4채널 → 3채널 처리
#             if frame.shape[2] == 4:
#                 frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

#             now = datetime.now()
#             minute_str = now.strftime('%Y-%m-%d_%H-%M')  # 1분 단위 파일
#             date_str = now.strftime('%Y-%m-%d')

#             # 새 파일 생성 조건 ss
#             if current_file != minute_str:
#                 # 기존 FFmpeg 프로세스 종료
#                 if ffmpeg_proc is not None:
#                     ffmpeg_proc.stdin.close()
#                     ffmpeg_proc.wait()

#                 # 디렉토리 생성
#                 os.makedirs(f'recordings/{date_str}', exist_ok=True)
#                 filepath = f'recordings/{date_str}/{minute_str}_recording.mp4'

#                 h, w, _ = frame.shape
#                 ffmpeg_cmd = [
#                     'ffmpeg',
#                     '-y',  # 기존 파일 덮어쓰기
#                     '-f', 'rawvideo',
#                     '-vcodec', 'rawvideo',
#                     '-pix_fmt', 'bgr24',
#                     '-s', f'{w}x{h}',
#                     '-r', str(fps),
#                     '-i', '-',  # stdin
#                     '-an',  # 오디오 없음
#                     '-c:v', 'libx264',
#                     '-pix_fmt', 'yuv420p',
#                     filepath
#                 ]

#                 ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
#                 current_file = minute_str
#                 print(f"[저장 시작] {filepath}")

#             # 프레임 쓰기
#             ffmpeg_proc.stdin.write(frame.tobytes())

#     except KeyboardInterrupt:
#         print("녹화 중단됨 (Ctrl+C)")
#         if ffmpeg_proc:
#             ffmpeg_proc.stdin.close()
#             ffmpeg_proc.wait()
#     except KeyboardInterrupt:
#         print("녹화 중단됨 (Ctrl+C)")
#         if video_writer:
#             video_writer.release()


# # 비디오 저장 쓰레드 시작
# threading.Thread(target=save_video, daemon=True).start()

# 실시간 영상 스트리밍
def gen(camera):
    while True:
        frame = camera.get_frame("byte")
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# 스프링과 소통해서 비디오 보여줄 수 있는 코드 
CHUNK_SIZE = 1024 * 1024  # 1MB

# ✅ 요청한 전체 움직임 값 반환


# 테스트를 위해 임시로 만든 gettotal 20을 고정으로 반환 
@app.route("/gettotal", methods=["GET"])
def provide_total():
    try:
        return jsonify({"amount": 20}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @app.route("/gettotal", methods=["GET"])
# def provide_total():
#     saved_videos_path = VIDEO_PATH + str(datetime.now().date() - timedelta(days=-1))
#     try:
#         value = int(get_total_motion(saved_videos_path))
#         return jsonify({"amount": value}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

"""
레이저 on off시 작동기능 관련 코드 --------------------------------------------------------
# 레이저 on : 1 레이저 on 2 녹화 시작
# 레이저 off : 1 레이저 off 2 영상저장 완료 3 저장된 영상 백앤드로 보내기 4 저장된 영상에서 운동량값 추출 5 영상삭제 6 운동량값 db로 전송
"""
# 전역 상태 변수
is_recording = False
exercise_amount = 0
base_dir = "/home/pc/toy_cat/venv/Video/recordings"
recording_file = None

# --- 하드웨어 관련 함수 (예시) ---

def start_recording():
    global recording_file, is_recording
    if is_recording == False:
        is_recording = True
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        #테스트용 임시코드
        recording_file = "test_video.mp4"
        # recording_file = f"recording_{timestamp}.mp4" 
        print(f"녹화 시작: {recording_file}")
    else:
        print("이미 레이저 및 녹화 작동 중")
    # 실제 녹화 코드 추후 작성해야 함

def stop_recording():
    global is_recording
    if is_recording == True:
        is_recording = False
        print(f"녹화 종료: {recording_file}")
    else:
        print("레이저 및 녹화 작동 중이 아닙니다")
    # 실제 녹화 끊는 코드 추후 작성해야 함

def get_total_motion(filepath):
    print("운동량: 1000")
    return 1000  
    # 테스트용 하드 코딩코드 추후 수정 필요

#녹화된 영상 백앤드 서버로 전송하는 코드
# 백엔드 업로드 URL (Spring)
BACKEND_UPLOAD_URL = "http://10.99.89.251:8000/api/recording/uploadRecording"
def send_recording_to_backend(filepath, backend_url=BACKEND_UPLOAD_URL, timeout=120):
    """
    녹화된 파일을 백엔드에 multipart/form-data로 업로드한다.
    - filepath: 라즈베리파이 상의 전체 파일 경로
    - backend_url: 스프링 업로드 엔드포인트
    - timeout: requests timeout (초)
    반환: 서버의 JSON 응답(dict) 또는 예외 발생
    """
    #파일 없으면 에러발생
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    # 파일명 파일페스로 부터 추출
    filename = os.path.basename(filepath)

    # 스트리밍 업로드: 파일을 열어 requests에 전달
    with open(filepath, "rb") as f:
        files = {"file": (filename, f, "video/mp4")}
        # 추가 데이터(예: date)를 보내고 싶으면 data= {...}
        try:
            resp = requests.post(backend_url, files=files, timeout=timeout)
            resp.raise_for_status()
            # JSON 리턴을 기대
            return resp.json()
        except requests.RequestException as e:
            # 업로드 실패 시 로깅 / 예외 재발생
            print(f"[send_recording_to_backend] upload failed: {e}")
            raise

# --- 레이저 on off 실제 작동 제어 ---
@app.route('/start', methods=['POST'])
def start():
    global recording_file, is_recording
    if is_recording == False:
        laser_on()
        start_recording()
        return jsonify({"message": "레이저 및 녹화 시작"})
    else:
        print("이미 레이저 및 녹화 작동 중")
        return jsonify({"message": "이미 레이저 및 녹화 작동 중"})

@app.route('/end', methods=['POST'])
def end():
    global recording_file, is_recording, base_dir
    if is_recording:
        try:
            laser_off()
            stop_recording()   # 내부적으로 녹화 스레드/비디오 writer를 안전히 닫음

            filepath = os.path.join(base_dir, recording_file)
            # 1) 백엔드로 파일 업로드
            try:
                upload_resp = send_recording_to_backend(filepath)
                print("[/end] upload response:", upload_resp)
            except Exception as e:
                print("[/end] upload to backend failed:", e)
                # 업로드 실패해도 로컬에서 분석은 계속할 수 있음

            # 2) 로컬에서 운동량 계산
            amount = get_total_motion(filepath)

            # 3) 로컬 파일 삭제 임시로 주석처리 나중엔 주석 풀기
            # os.remove(filepath)
            # print(f"INFO: Local file deleted: {filepath}")

            # 클라이언트(스프링)에 JSON으로 정수 반환
            return str(amount), 200, {'Content-Type': 'text/plain'}

        except Exception as e:
            print(f"ERROR in /end: {e}")
            # 처리 중 예상치 못한 오류 발생 시 500 에러와 함께 메시지 반환
            return jsonify({"error": f"Internal Pi Error: {e}"}), 500

        finally:
            is_recording = False
            recording_file = None
    else:
        print("레이저 및 녹화 작동 중이 아닙니다")
        return jsonify({"error": "not_recording"}), 400
"""
--------------------------------------------------------------------------------------------        
"""
"""
놀이 범위 세팅 코드 --------------------------------------------------------------------------
"""
@app.route('/set_area', methods=['POST'])
def set_play_area():
    try:
        # 1. Vue에서 Spring을 거쳐 넘어온 JSON 데이터 받기
        data = request.get_json()
        points = data.get('area_points')

        if not points:
            return jsonify({"success": False, "message": "좌표 데이터(area_points)가 없습니다."}), 400

        print(f"✅ 새로운 놀이 범위 좌표 수신: {points}")
        
        # 2. 여기서 받은 좌표 데이터를 사용하여 실제 하드웨어 제어 로직 구현
        # 예: 로봇에게 해당 좌표를 전송하거나, 이미지 처리 모듈에 영역 정보 전달

        return jsonify({"success": True, "message": "놀이 범위 설정 완료"}), 200

    except Exception as e:
        print(f"❌ Flask 처리 오류: {e}")
        return jsonify({"success": False, "message": f"서버 처리 오류: {e}"}), 500
"""
--------------------------------------------------------------------------------------------        
"""
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
