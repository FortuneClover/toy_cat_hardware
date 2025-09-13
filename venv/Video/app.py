# app.py
from flask import Flask, render_template, Response, send_from_directory, jsonify, request
from camera import Camera

import threading
from datetime import datetime, timedelta
import os
import re
import cv2
import time

import sys
import os

# 현재 파일 기준 상위 폴더 경로 얻기
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 상위 폴더를 모듈 경로에 추가
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from Subtraction import get_total_motion

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

# 백그라운드 실행으로 비디오 저장할 쓰레드 함수
def save_video():
    current_date = None
    video_writer = None
    fps = 30 #초당 15프레임 

    #하루마다 새파일로 비디오 녹화
    try:
        while True:
            frame = camera.get_frame()
            # if frame is None:
            #     print("❌ 프레임이 None입니다.")
            # else:
            #     print("✅ 프레임 캡처 성공:", frame.shape)

            # 4채널 → 3채널 BGR로 변환
            # if frame.shape[2] == 4:
            #     frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)

            now = datetime.now()
            date_str = now.strftime('%Y-%m-%d')
            minute_str = now.strftime('%Y-%m-%d %H:%M') # 테스트 용으로 1분마다 녹화파일 저장 코드 
            time_str = now.strftime('%H-%M-%S')
            #하루마다 새파일 만들고 녹화하는 코드 
            #if current_date != date_str:
            if current_date != minute_str: # 테스트 용으로 1분마다 녹화파일 저장 코드
                if video_writer:
                    video_writer.release()

                os.makedirs(f'recordings/{date_str}', exist_ok=True)
                filepath = f'recordings/{date_str}/{time_str}_recording.mp4'
                h, w, _ = frame.shape
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writer = cv2.VideoWriter(filepath, fourcc, fps, (w, h))
                #current_date = date_str
                current_date = minute_str # 테스트 용으로 1분마다 녹화파일 저장 코드
                print(f"[저장 시작] {filepath}")
            # 비디오 녹화 코드
            video_writer.write(frame)
            # print("✔️ 프레임 작성됨")

            time.sleep(1 / fps)

    except KeyboardInterrupt:
            print("녹화 중단됨 (Ctrl+C)")
            video_writer.release()

# 비디오 저장 쓰레드 시작
threading.Thread(target=save_video, daemon=True).start()

#실시간 영상 스트리밍
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


# ✅ 날짜 리스트 반환 (Spring이 요청하는 /videos 경로 대응)
@app.route('/videos', methods=['GET'])
def list_dates():
    if not os.path.exists(VIDEO_PATH):
        return jsonify([])

    folders = [f for f in os.listdir(VIDEO_PATH) if os.path.isdir(os.path.join(VIDEO_PATH, f))]
    folders.sort(reverse=True)  # 최신 날짜 먼저
    return jsonify(folders)


# ✅ 특정 날짜의 영상 리스트 반환
@app.route('/videos/<date>', methods=['GET'])
def list_videos(date):
    folder_path = os.path.join(VIDEO_PATH, date)
    if not os.path.exists(folder_path):
        return jsonify([])

    files = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
    return jsonify(files)


# ✅ 특정 영상 스트리밍
@app.route('/video/recordings/<date>/<filename>', methods=['GET'])
def serve_video(date, filename):
    print("=== Flask 비디오 요청 시작 ===")
    print(f"📅 Date: {date}")
    print(f"📁 Filename: {filename}")
    
    folder_path = os.path.join(VIDEO_PATH, date)
    file_path = os.path.join(folder_path, filename)
    
    print(f"📄 File path: {file_path}")
    print(f"✅ File exists: {os.path.isfile(file_path)}")

    if not os.path.isfile(file_path):
        print(f"❌ 파일을 찾을 수 없음: {file_path}")
        return abort(404)

    try:
        file_size = os.path.getsize(file_path)
        print(f"📊 File size: {file_size} bytes")
    except OSError as e:
        print(f"❌ 파일 크기 확인 실패: {e}")
        return abort(500)

    range_header = request.headers.get("Range", None)
    print(f"🔄 Range header: {range_header}")

    if range_header:
        try:
            match = re.match(r"bytes=(\d+)-(\d*)", range_header)
            if not match:
                print("❌ Range 헤더 형식이 잘못됨")
                return Response(status=416)

            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else file_size - 1
            
            # 범위 검증
            if start >= file_size or end >= file_size or start > end:
                print(f"❌ 잘못된 범위: {start}-{end}, 파일 크기: {file_size}")
                return Response(status=416)
                
            length = end - start + 1
            print(f"📍 Range: {start}-{end}, Length: {length}")

            def generate():
                try:
                    with open(file_path, "rb") as f:
                        f.seek(start)
                        remaining = length
                        sent = 0
                        
                        while remaining > 0:
                            # 읽을 크기 결정 (남은 양과 CHUNK_SIZE 중 작은 값)
                            chunk_size = min(CHUNK_SIZE, remaining)
                            chunk = f.read(chunk_size)
                            
                            if not chunk:
                                print(f"⚠️ 파일 끝 도달: sent={sent}, remaining={remaining}")
                                break
                                
                            yield chunk
                            sent += len(chunk)
                            remaining -= len(chunk)
                            
                            # 진행상황 로그 (1MB마다)
                            if sent % (1024 * 1024) == 0:
                                print(f"📤 전송 중: {sent // 1024 // 1024}MB / {length // 1024 // 1024}MB")
                        
                        print(f"📤 전송 완료: {sent} bytes")
                        
                except Exception as e:
                    print(f"❌ 파일 읽기 중 오류: {e}")
                    raise

            headers = {
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(length),
                "Content-Type": "video/mp4",
            }
            
            print("📋 응답 헤더들:")
            for key, value in headers.items():
                print(f"  {key}: {value}")

            return Response(generate(), status=206, headers=headers)

        except Exception as e:
            print(f"❌ Range 요청 처리 중 오류: {e}")
            return abort(500)

    else:
        # 전체 파일 전송
        print("📤 전체 파일 전송")
        
        def generate_full():
            try:
                with open(file_path, 'rb') as f:
                    sent = 0
                    while True:
                        chunk = f.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        yield chunk
                        sent += len(chunk)
                        
                        # 진행상황 로그
                        if sent % (1024 * 1024) == 0:
                            print(f"📤 전송 중: {sent // 1024 // 1024}MB")
                    
                    print(f"📤 전체 파일 전송 완료: {sent} bytes")
                    
            except Exception as e:
                print(f"❌ 전체 파일 읽기 중 오류: {e}")
                raise
        
        headers = {
            "Content-Length": str(file_size),
            "Content-Type": "video/mp4",
            "Accept-Ranges": "bytes"
        }
        
        return Response(generate_full(), status=200, headers=headers)

# ✅ 요청한 전체 움직임 값 반환



@app.route("/gettotal", methods=["GET"])
def provide_total():
    saved_videos_path = VIDEO_PATH + str(datetime.now().date() - timedelta(days=-1))
    try:
        value = int(get_total_motion(saved_videos_path))
        return jsonify({"amount": value}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
         
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
