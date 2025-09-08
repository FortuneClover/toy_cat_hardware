import cv2
import numpy as np

cap = cv2.VideoCapture('/home/pc/toy_cat/venv/Video/recordings/2025-06-15/17-34-00_recording.mp4')
fgbg = cv2.createBackgroundSubtractorMOG2()

prev_centers = []
total_motion = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (400, 400))
    fgmask = fgbg.apply(frame)

    # 마스크 전처리
    _, thresh = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

    # 윤곽선 찾기
    contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    fgmask_colored = cv2.cvtColor(clean, cv2.COLOR_GRAY2BGR)

    current_centers = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 500:
            continue

        # 윤곽선 데이터 구조 (x, y)형식
        # print(cnt)
        
        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        current_centers.append((cx, cy))

        cv2.circle(fgmask_colored, (cx, cy), 5, (0, 0, 255), -1)

    # 활동량 계산
    frame_motion = 0
    for (cx, cy) in current_centers:
        for (pcx, pcy) in prev_centers:
            distance = np.sqrt((cx - pcx)**2 + (cy - pcy)**2)
            frame_motion += distance

    total_motion += frame_motion
    prev_centers = current_centers

    # 화면에 출력
    cv2.putText(fgmask_colored, f"Motion: {frame_motion:.2f}", (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(fgmask_colored, f"Total: {total_motion:.2f}", (10, 45),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow('MOG2_with_points', fgmask_colored)
    cv2.imshow('original', frame)

    if cv2.waitKey(30) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

print("frame_motion : ", frame_motion)
print("Total : ", total_motion)