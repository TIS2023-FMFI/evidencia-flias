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


def longest_lines(lines):
    ordered = []
    for line in lines:
        length = distance(*line)
        ordered.append((length, line))
    ordered.sort(reverse=True, key=lambda x: x[0])
    return [x[1] for x in ordered[:2]]


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


def angle_between(x1, y1, x2, y2):
    return round(np.rad2deg(np.arctan2(y1 - y2, x1 - x2))) + 179


def save_img(img, verdict, file):
    if file is None:
        return
    cv2.putText(img, verdict, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9,(0,255,0),2)
    cv2.imwrite(file, img)


def detect_pressure(img_bytes, range_min, range_max, output=None):
    im_data = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(im_data, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    height, width = img.shape[:2]

    # Try to find the gauge
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.5, 50, param1=180, param2=220, minRadius=width // 6)

    if circles is None:
        save_img(img, "No circles", output)
        return None

    filtered_circles = []
    for circle in circles[0]:
        if circle[2] < width * 0.4:
            continue
        if distance(circle[0], circle[1], width/2, height/2) > 100:
            continue
        filtered_circles.append(circle)

    if not filtered_circles:
        save_img(img, "No circles after filter", output)
        return None

    for circle in filtered_circles:
        cv2.circle(img, (int(circle[0]), int(circle[1])), int(circle[2]), (0,0,255),2)

    cx, cy, radius = average_circle(filtered_circles)
    cv2.circle(img, (cx, cy), radius, (0, 255, 0), 3, cv2.LINE_AA)

    # Calculate darkness around the gauge
    darkness = [0] * 360
    for x in range(width):
        for y in range(height):
            dist = math.sqrt((cx - x)**2 + (cy - y)**2)
            if radius * 0.7 >= dist >= radius * 0.5:
                angle = angle_between(cx, cy, x, y)

                b, g, r = img[y, x]
                rg = int(r) - int(g)
                rb = int(r) - int(b)
                delta = 30
                level = (255 if rg > delta and rb > delta else 0)
                darkness[angle] += level

                img[y, x, 0] = level

    darkness_prefix = [0]
    for i in range(360*2):
        darkness_prefix.append(darkness_prefix[-1] + darkness[i % 360])

    # Find the gauge's cutout
    cutout_size = 89
    cutout_angle = 0
    cutout_max = None
    for start in range(360):
        dark = darkness_prefix[start + cutout_size] - darkness_prefix[start]
        if cutout_max is None or dark < cutout_max:
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

    canny = cv2.Canny(gray, 180, 300)
    lines = cv2.HoughLinesP(canny, 2.5, np.pi / 180, 80, minLineLength=150, maxLineGap=25)
    if lines is None:
        save_img(img, "No lines", output)
        return None

    filtered_lines = []
    for line in lines:
        line = line[0]
        dist = min(distance(cx, cy, *line[2:]), distance(cx, cy, *line[:2]))
        dist_center = np.cross(line[2:] - line[:2], np.array([cx, cy]) - line[:2]) / np.linalg.norm(line[2:] - line[:2])
        color = (255,255,0)

        if abs(dist_center) <= 50 and abs(dist) <= 150:
            filtered_lines.append(line)
            color = (0,255,255)
        cv2.line(img, line[:2], line[2:], color, 2)

    if not filtered_lines:
        save_img(img, "No lines after filter", output)
        return None

    filtered_lines = longest_lines(filtered_lines)
    for line in filtered_lines:
        cv2.line(img, line[:2], line[2:], (0,0,255), 1)

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

    pressure = int(diff * bar_per_deg)
    save_img(img, f"{pressure} bar", output)
    return pressure
