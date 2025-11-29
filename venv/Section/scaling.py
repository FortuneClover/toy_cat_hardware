import cv2
import numpy as np
import random
from shapely.geometry import Polygon, Point

class Section:
    def __init__(self, points):
        self.points = np.array(points, dtype=np.float32)
        self.height = 640
        self.width = 480
        self.poly = None
        self.center = None
        self.mask = None

    def find_section(self):
        # print("self.points : ", self.points)
        
        """입력받은 다각형을 시각화하고 내부 랜덤 좌표를 생성"""
        self.mask = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        # print("mask : ", mask)
        
        # 중심점 계산
        self.center = np.mean(self.points, axis=0)
        
        # # 다각형 스케일링
        scaled_poly = self.scale_around_point(0.8, self.center)

        # 다각형 객체 생성
        self.poly = Polygon(scaled_poly)

    # @staticmethod
    def scale_around_point(self, scale_factors, origin):
        """중심점 기준 스케일링"""
        points = np.asarray(self.points)
        origin = np.asarray(origin)

        shifted_points = points - origin
        if np.isscalar(scale_factors):
            scaled_points = shifted_points * scale_factors
        else:
            scaled_points = shifted_points * np.array(scale_factors)

        return scaled_points + origin

    # @staticmethod
    def generate_point(self):
        """다각형 내부 랜덤 점 생성"""
        min_x, min_y, max_x, max_y = self.poly.bounds
        while True:
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
            point = Point(x, y)
            if self.poly.contains(point):
                return x, y

if __name__ == '__main__':
    points = [[0.375, 28.75], [91.375, 45.75], [104.375, 1.75], [158.375, 4.75], [123.375, 161.75], [10.375, 164.75], [1.375, 33.75]]
    section = Section(points)
    section.find_section()
    for i in range(10):
        print(section.generate_point())