import math

import cv2
import numpy as np


def average_circle(circles):
    x = []
    y = []
    r = []
    for circle in circles:
        x.append(circle[0])
        y.append(circle[1])
        r.append(circle[2])

    x = int(sum(x) / len(x))
    y = int(sum(y) / len(y))
    r = int(sum(r) / len(r))
    return x, y, r


def average_line(lines):
    x1 = x2 = y1 = y2 = 0
    l = 0
    for line in lines:
        length = distance(*line)
        x1 += line[0] * length
        y1 += line[1] * length
        x2 += line[2] * length
        y2 += line[3] * length
        l += length
    # l = len(lines)
    return int(x1 / l), int(y1 / l), int(x2 / l), int(y2/l)


def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def save_img(img, verdict, file):
    if file is None:
        return
    cv2.putText(img, verdict, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9,(0,255,0),2)
    cv2.imwrite(file, img)


def detect_pressure(img_bytes, range_min, range_max, output=None):
    im_data = np.fromstring(img_bytes, np.uint8)
    img = cv2.imdecode(im_data, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thr = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    _, thr2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    height, width = img.shape[:2]

    # Try to find the gauge
    canny = cv2.Canny(gray, 100, 200)
    circles = cv2.HoughCircles(canny, cv2.HOUGH_GRADIENT, 1, 20, minRadius=width // 10)

    if circles is None:
        save_img(img, "No circles", output)
        return None

    filtered_circles = []
    for circle in circles[0]:
        # if 10 <= circle[2] <= 100:
        #     continue
        if width * 0.7 <= circle[2] <= width * 0.4:
            continue
        if distance(circle[0], circle[1], width/2, height/2) > 200:
            continue
        filtered_circles.append(circle)

    if not filtered_circles:
        save_img(img, "No circles after filter", output)
        return None

    # for circle in filtered_circles:
    #     cv2.circle(img, (int(circle[0]), int(circle[1])), int(circle[2]), (0,0,255),2)

    cx, cy, radius = average_circle(filtered_circles)
    cv2.circle(img, (cx, cy), radius, (0, 255, 0), 3, cv2.LINE_AA)

    # Calculate darkness around the gauge
    darkness = [0] * 360
    for x in range(width):
        for y in range(height):
            dist = math.sqrt((cx - x)**2 + (cy - y)**2)
            if abs(dist - radius) <= radius * 0.2:
                angle = int(np.rad2deg(np.arctan2(cy - y, cx - x))) + 179
                darkness[angle] += thr[y, x]

    darkness_prefix = [0]
    for i in range(360*2):
        darkness_prefix.append(darkness_prefix[-1] + darkness[i % 360])

    # Find the gauge's cutout
    cutout_size = 88
    cutout_angle = 0
    cutout_max = 0
    for start in range(360):
        dark = darkness_prefix[start + cutout_size] - darkness_prefix[start]
        if dark > cutout_max:
            cutout_angle = start
            cutout_max = dark

    max_angle = cutout_angle
    a = np.deg2rad(cutout_angle)
    max_point = (cx + int(math.cos(a) * radius), cy + int(math.sin(a)*radius))
    min_angle = cutout_angle + cutout_size
    a = np.deg2rad(cutout_angle + cutout_size)
    min_point = (cx + int(math.cos(a) * radius), cy + int(math.sin(a)*radius))

    cv2.line(img, (cx, cy), max_point, (255,0,0), 2)
    cv2.line(img, (cx, cy), min_point, (255,0,0), 2)

    lines = cv2.HoughLinesP(thr2, 3, np.pi / 180, 100, minLineLength=250, maxLineGap=8)
    if lines is None:
        save_img(img, "No lines", output)
        return None

    filtered_lines = []
    for line in lines:
        line = line[0]
        dist = np.cross(line[2:] - line[:2], np.array([cx, cy]) - line[:2]) / np.linalg.norm(line[2:] - line[:2])
        if abs(dist) < 50:
            filtered_lines.append(line)

    if not filtered_lines:
        save_img(img, "No lines after filter", output)
        return None

    line = average_line(filtered_lines)
    top_x, top_y = line[:2]
    if distance(cx, cy, *line[:2]) < distance(cx, cy, *line[2:]):
        top_x, top_y = line[2:]

    cv2.line(img, (cx, cy), (top_x, top_y), (0,0,255), 4)
    angle = int(np.rad2deg(np.arctan2(cy - top_y, cx - top_x))) + 179

    diff = (angle - min_angle) % 360
    max_angle = (max_angle - min_angle) % 360

    range_total = range_max - range_min
    bar_per_deg = range_total / max_angle
    if diff > range_total:
        save_img(img, "Value out of range", output)
        return None

    pressure = diff * bar_per_deg
    save_img(img, f"{pressure} bar", output)
    return pressure
