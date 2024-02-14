import numpy as np
import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


def dist_2_pts(x1, y1, x2, y2):
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def rotate_image(image, angle):
    center = (image.shape[1] // 2, image.shape[0] // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(image, rotation_matrix, (image.shape[1], image.shape[0]))
    return rotated_image


def count_red(angle_degrees, offset, roi):
    temp = rotate_image(roi, angle_degrees)
    h, w = temp.shape[:2]
    top_left = (0, 0)
    min_pressure = (w // 2 + offset, 2 * h)
    max_pressure = (2 * w, h // 2 + offset)
    color = (0, 255, 0)
    thickness = -1
    cv2.rectangle(temp, top_left, min_pressure, color, thickness)
    cv2.rectangle(temp, top_left, max_pressure, color, thickness)
    hsv = cv2.cvtColor(temp, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    mask = cv2.inRange(hsv, lower_red, upper_red)
    red_pixel_count = np.sum(mask == 255)
    return red_pixel_count, angle_degrees, offset


def adjust_line_length(point1, point2, length):
    direction = np.array([point2[0] - point1[0], point2[1] - point1[1]])
    direction_normalized = direction / np.linalg.norm(direction)
    new_endpoint = (
        int(point1[0] + length * direction_normalized[0]), int(point1[1] + length * direction_normalized[1]))
    return new_endpoint


def angle_between_points(a, b, c):
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    return np.degrees(angle)


def rotate_point(point, angle, center):
    angle_rad = np.radians(angle)
    translated_point = np.subtract(point, center)
    cos_theta = np.cos(angle_rad)
    sin_theta = np.sin(angle_rad)
    rotation_matrix = np.array([[cos_theta, -sin_theta], [sin_theta, cos_theta]])
    rotated_point = np.dot(rotation_matrix, translated_point)
    rotated_point = np.add(rotated_point, center)
    return rotated_point


def get_number(point, image):
    adjust_x, adjust_y = 30, 35
    x1, y1 = point
    x2, y2 = x1 + adjust_x, y1 + adjust_y

    temp = image[int(y1):int(y2), int(x1):int(x2)].copy()

    x1, y1 = 0, 0
    x2, y2 = adjust_x, adjust_y

    # cv2.imshow('Analog Gauge Reader temp', temp)
    # cv2.waitKey(0)
    # print(temp.shape[:2])
    new_y1 = 0
    for y in range(0, y2):
        if not is_black_pixel_in_line(temp, 0, y, x2 - 1, y):
            new_y1 = y + 1
            break

    new_y2 = 0
    for y in range(y2 - 1, 0, -1):
        if not is_black_pixel_in_line(temp, 0, y, x2 - 1, y):
            new_y2 = y - 1
            break

    new_temp = temp[new_y1:new_y2, 0:int(x2) - int(x1)].copy()
    y2, x2 = new_temp.shape[:2]

    # print(new_temp.shape[:2])

    # cv2.imshow('Analog Gauge Reader new_temp', new_temp)
    # cv2.waitKey(0)

    new_x1 = 0
    for x in range(0, x2):
        if is_black_pixel_in_column(new_temp, x, 0, x, y2 - 1):
            new_x1 = x - 1
            break

    new_x2 = 0
    for x in range(x2 - 1, 0, -1):
        if is_black_pixel_in_column(new_temp, x, 0, x, y2 - 1):
            new_x2 = x + 1
            break

    if (new_x2 - new_x1) < 15:
        new_x2 = new_x1 + 20
    newer_temp = new_temp[0:int(y2), new_x1:new_x2].copy()
    # print(newer_temp.shape[:2])
    # cv2.imshow("Turned", newer_temp)
    # cv2.waitKey(0)
    # Perform OCR (Optical Character Recognition) using PyTesseract
    text = pytesseract.image_to_string(np.array(newer_temp), config='--psm 13')

    # Print the detected text
    # print("Detected numbers in the region of interest:")

    result = ""

    for i in text:
        if '0' <= i <= '9':
            result += i

    if result == "" or int(result) < 100:
        print("Failed to detect max pressure, using preset value of " + str(default_pressure))
        return 315

    # print(result)
    print(result, "max pressure detected")
    return int(result)


def is_black_pixel_in_line(image, x1, y1, x2, y2):
    length = max(abs(x2 - x1), abs(y2 - y1)) + 1
    for x in range(length):
        if np.mean(image[y1, x]) < 100:
            return True
    return False


def is_black_pixel_in_column(image, x1, y1, x2, y2):
    length = max(abs(x2 - x1), abs(y2 - y1)) + 1
    for y in range(length):
        if np.mean(image[y, x1]) < 100:
            return True
    return False


def count_black(angle_degrees, width, roi):
    temp = rotate_image(roi, angle_degrees)
    h, w = temp.shape[:2]
    x1, y1 = w // 2 - width, h // 2
    x2, y2 = w // 2 + width, 3 * h // 4
    new_temp = temp[y1:y2, x1:x2]
    gray_roi = cv2.cvtColor(new_temp, cv2.COLOR_BGR2GRAY)
    num_pixels_close_to_black = np.sum(gray_roi < 100)
    return num_pixels_close_to_black, angle_degrees


default_pressure = 400  # If detection fails

image_file = 'centered8.jpg'  # input image
img = cv2.imread(image_file)
y, x = img.shape[:2]
y, x = y // 2, x // 2
r = x // 2
clean_roi = img.copy()

cv2.circle(img, (x, y), 2, (0, 255, 0), 10, cv2.LINE_AA)
cv2.circle(img, (x, y), r, (0, 0, 0), -1)

roi = img.copy()

max_width = 400
max_height = 400

if roi.shape[1] > max_width or roi.shape[0] > max_height:
    scale = min(max_width / roi.shape[1], max_height / roi.shape[0])
    roi = cv2.resize(roi, None, fx=scale, fy=scale)
    clean_roi = cv2.resize(clean_roi, None, fx=scale, fy=scale)

y, x = roi.shape[:2]
y, x = y // 2, x // 2
r = x // 2
roi = roi[y - x:(2 * y - (y - x)), 0:2 * x]
clean_roi = clean_roi[y - x:(2 * y - (y - x)), 0:2 * x]

if roi is not None:
    saved_result = None
    pixels = None
    narrow_by = 0
    adjust = 0
    last_two = [0, 0]
    while True:
        if (last_two[0] == 0) and (last_two[1] != 0):
            break
        found = 0
        for i in range(360):
            pixels, result, adjust = count_red(i, narrow_by, roi)
            if pixels == 0:
                found += 1
                saved_result = result
        last_two[1] = last_two[0]
        last_two[0] = found
        if found == 1:
            break
        elif found > 1:
            narrow_by -= 1
        elif found == 0:
            narrow_by += 1

    most_pixels = 0
    best_result = 0
    for i in range(360):
        pixels, result = count_black(i, 4, clean_roi)
        if pixels > most_pixels:
            most_pixels = pixels
            best_result = result

    with_extremes = rotate_image(clean_roi, saved_result)
    h, w = with_extremes.shape[:2]
    b = (w // 2 + adjust, 2 * h)
    b = rotate_point(b, saved_result, (w // 2, h // 2))
    c = (2 * w, h // 2 + adjust)
    c = rotate_point(c, saved_result, (w // 2, h // 2))
    bx, by = adjust_line_length((w // 2, h // 2), b, r)
    cx, cy = adjust_line_length((w // 2, h // 2), c, r)

    extremes_angle = angle_between_points(np.array([bx, by]), (w // 2, h // 2), np.array([cx, cy]))

    if extremes_angle < 180:
        extremes_angle = 360 - extremes_angle

    if True:
        if True:
            arrow_angle = best_result
            ax, ay = adjust_line_length([w // 2, h // 2], [w // 2, h], r)
            arrow = rotate_point([ax, ay], arrow_angle, [w // 2, h // 2])
            arrow_x = int(arrow[0])
            arrow_y = int(arrow[1])

            pressure_angle = angle_between_points(np.array([arrow_x, arrow_y]), [w // 2, h // 2], np.array([bx, by]))

            number_position = adjust_line_length((w // 2, h // 2), (cx, cy), w // 4)
            rotated_position = rotate_point(number_position, (360 - extremes_angle) // 2 - saved_result,
                                            (w // 2, h // 2))
            read_image = rotate_image(clean_roi, saved_result - (360 - extremes_angle) // 2)

            max_pressure = default_pressure
            try:
                max_pressure = get_number(rotated_position, read_image)
            except IndexError:
                print("Failed to detect max pressure, using preset value of " + str(default_pressure))

            ratio = max_pressure / extremes_angle
            detected_pressure = int(ratio * pressure_angle)

            print(detected_pressure, "bar")
