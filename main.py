#!/usr/bin/python3
import sys
import mediapipe as mp
import cv2
import json
from socket_server import CaptureServer, MESSAGE_QUEUE


def main():
    cam = cv2.VideoCapture(0)
    socket = CaptureServer()
    socket.start()
    pose_detector = mp.solutions.holistic.Holistic(min_detection_confidence=0.7, min_tracking_confidence=0.7, model_complexity=1,smooth_landmarks=True, refine_face_landmarks=True)
    try:
        while True:
            data = {
                'poseLandmarks': [],
                'worldPoseLandmarks': [],
                'rightHandLandmarks': [],
                'leftHandLandmarks': [],
                'faceLandmarks': []
            }
            # sucess是布尔型，读取帧正确返回True;img是每一帧的图像（BGR存储格式）
            success, image = cam.read()
            if not success:
                continue
            # 将一幅图像从一个色彩空间转换为另一个,返回转换后的色彩空间图像
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # 处理RGB图像并返回手的标志点和检测到的每个手对象
            result_pose = pose_detector.process(img_rgb)
            # results.multi_hand_landmarks返回None或手的标志点坐标
            if result_pose.pose_landmarks:
                for point in result_pose.pose_landmarks.landmark:
                    data['poseLandmarks'].append({'x': point.x, 'y': point.y, 'z': 0, 'visibility': point.visibility})
                for point in result_pose.pose_world_landmarks.landmark:
                    data['worldPoseLandmarks'].append({'x': point.x, 'y': point.y, 'z': point.z, 'visibility': point.visibility})

            if result_pose.left_hand_landmarks:
                for point in result_pose.left_hand_landmarks.landmark:
                    data['leftHandLandmarks'].append({'x': point.x, 'y': point.y, 'z': 0, 'visibility': point.visibility})

            if result_pose.right_hand_landmarks:
                for point in result_pose.right_hand_landmarks.landmark:
                    data['rightHandLandmarks'].append({'x': point.x, 'y': point.y, 'z': 0, 'visibility': point.visibility})

            if result_pose.face_landmarks:
                for point in result_pose.face_landmarks.landmark:
                    data['faceLandmarks'].append({'x': point.x, 'y': point.y, 'z': point.z, 'visibility': point.visibility})

            if not MESSAGE_QUEUE.full():
                MESSAGE_QUEUE.put(json.dumps(data))

    except KeyboardInterrupt:
        socket.terminate()
        sys.exit(0)


if __name__ == '__main__':
    main()
