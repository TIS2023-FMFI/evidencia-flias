# Python program to read analog gauge from a single image

import numpy as np
import cv2

print("This program will recognize gauge meter value from an image.")
print("Initial parameter of gauge:")

min_angle = 60
max_angle = 315
#min_value = 0
#max_value = 315
#units = "Bar"

'''
min_angle = input('Min angle (lowest possible angle of dial) - in degrees: ')  # the lowest possible angle
max_angle = input('Max angle (highest possible angle) - in degrees: ')  # highest possible angle
'''
min_value = input('Min value: ')  # usually zero
max_value = input('Max value: ')  # maximum reading of the gauge
units = input('Enter units: ')

# Read an image from a file
image_file = 'C:\\Users\\Admin\\Desktop\\mamometer\\0.jpg'


def avg_circles(circles, b):
    avg_x = 0
    avg_y = 0
    avg_r = 0
    for i in range(b):
        # optional - average for multiple circles (can happen when a gauge is at a slight angle)
        avg_x = avg_x + circles[0][i][0]
        avg_y = avg_y + circles[0][i][1]
        avg_r = avg_r + circles[0][i][2]
    avg_x = int(avg_x / (b))
    avg_y = int(avg_y / (b))
    avg_r = int(avg_r / (b))
    return avg_x, avg_y, avg_r

def dist_2_pts(x1, y1, x2, y2):
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

try:
            img = cv2.imread(image_file)
        
            width = 640 # New width
            height = 480 # New height
            img = cv2.resize(img, (width, height))
            
            cv2.imshow('Analog Gauge Reader', img)

            img_blur = cv2.GaussianBlur(img, (5,5), 3)
            gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)  #convert to gray
            height, width = img.shape[:2]

            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, np.array([]), 100, 50, int(height*0.3), int(height*1))
            print(circles.shape)
            a, b, c = circles.shape

            x,y,r = avg_circles(circles, b)
            #y += 5
            #r += 50

            #draw center and circle
            cv2.circle(img, (x, y), r, (0, 0, 255), 3, cv2.LINE_AA)  # draw circle
            cv2.circle(img, (x, y), 2, (0, 255, 0), 3, cv2.LINE_AA)  # draw center of circle
            
            separation = 10.0 #in degrees
            interval = int(360 / separation)
            p1 = np.zeros((interval,2))  #set empty arrays
            p2 = np.zeros((interval,2))
            p_text = np.zeros((interval,2))
            for i in range(0,interval):
                for j in range(0,2):
                    if (j%2==0):
                        p1[i][j] = x + 0.9 * r * np.cos(separation * i * 3.14 / 180) #point for lines
                    else:
                        p1[i][j] = y + 0.9 * r * np.sin(separation * i * 3.14 / 180)
            text_offset_x = 10
            text_offset_y = 5
            for i in range(0, interval):
                for j in range(0, 2):
                    if (j % 2 == 0):
                        p2[i][j] = x + r * np.cos(separation * i * 3.14 / 180)
                        p_text[i][j] = x - text_offset_x + 1.2 * r * np.cos((separation) * (i+9) * 3.14 / 180) #point for text labels, i+9 rotates the labels by 90 degrees
                    else:
                        p2[i][j] = y + r * np.sin(separation * i * 3.14 / 180)
                        p_text[i][j] = y + text_offset_y + 1.2* r * np.sin((separation) * (i+9) * 3.14 / 180)  # point for text labels, i+9 rotates the labels by 90 degrees

            #add the lines and labels to the image
            for i in range(0,interval):
                pass
                #cv2.line(img, (int(p1[i][0]), int(p1[i][1])), (int(p2[i][0]), int(p2[i][1])),(0, 255, 0), 2)
                #cv2.putText(img, '%s' %(int(i*separation)), (int(p_text[i][0]), int(p_text[i][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.3,(0,0,0),1,cv2.LINE_AA)


            gray2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Set threshold and maxValue
            thresh = 100
            maxValue = 255

            # apply thresholding which helps for finding lines
            th, dst2 = cv2.threshold(gray2, thresh, maxValue, cv2.THRESH_BINARY_INV)

            # find lines
            minLineLength = 200
            maxLineGap = 5
            lines = cv2.HoughLinesP(image=dst2, rho=1, theta=np.pi / 180, threshold=300,minLineLength=minLineLength, maxLineGap=maxLineGap)  # rho is set to 3 to detect more lines, easier to get more then filter them out later

            final_line_list = []
            #print "radius: %s" %r
            diffUpperBound = 0.75
            for i in range(0, len(lines)):
                for x1, y1, x2, y2 in lines[i]:
                        diff1 = dist_2_pts(x, y, x1, y1)  # x, y is center of circle
                        diff2 = dist_2_pts(x, y, x2, y2)
                        print(diff1)
                        if ((diff1<diffUpperBound*r) or (diff2<diffUpperBound*r)):
                            final_line_list.append([x1, y1, x2, y2])
                            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

            l = final_line_list[0]
            d = ((l[0] - l[2])**2 +(l[1] - l[3])**2)**(1/2)
            for i in final_line_list:
                    new_d = ((i[0] - i[2])**2 +(i[1] - i[3])**2)**(1/2)
                    if d < new_d:
                            l = i
                            d = new_d

            # assumes the first line is the best one
            x1 = l[0]
            y1 = l[1]
            x2 = l[2]
            y2 = l[3]
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

            #add the lines and labels to the image
            for i in range(0,interval):
                cv2.line(img, (int(p1[i][0]), int(p1[i][1])), (int(p2[i][0]), int(p2[i][1])),(0, 255, 0), 2)
                cv2.putText(img, '%s' %(int(i*separation)), (int(p_text[i][0]), int(p_text[i][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.3,(0,0,0),1,cv2.LINE_AA)

            #for testing purposes, show the line overlayed on the original image
            cv2.imwrite("C:\\Users\\Admin\\Desktop\\mamometer\\" + "/" + "0" + "-needle.jpg", img)

            #find the farthest point from the center to be what is used to determine the angle
            dist_pt_0 = dist_2_pts(x, y, x1, y1)
            dist_pt_1 = dist_2_pts(x, y, x2, y2)
            if (dist_pt_0 > dist_pt_1):
                x_angle = x1 - x
                y_angle = y - y1
            else:
                x_angle = x2 - x
                y_angle = y - y2
            # take the arc tan of y/x to find the angle
            res = np.arctan(np.divide(float(y_angle), float(x_angle)))
            #np.rad2deg(res) #coverts to degrees

            # print x_angle
            # print y_angle
            # print res
            # print np.rad2deg(res)

            #these were determined by trial and error
            res = np.rad2deg(res)
            if x_angle > 0 and y_angle > 0:  #in quadrant I
                final_angle = 270 - res
            if x_angle < 0 and y_angle > 0:  #in quadrant II
                final_angle = 90 - res
            if x_angle < 0 and y_angle < 0:  #in quadrant III
                final_angle = 90 - res
            if x_angle > 0 and y_angle < 0:  #in quadrant IV
                final_angle = 270 - res

            #print final_angle

            old_min = float(min_angle)
            old_max = float(max_angle)

            new_min = float(min_value)
            new_max = float(max_value)

            old_value = final_angle

            old_range = (old_max - old_min)
            new_range = (new_max - new_min)
            new_value = (((old_value - old_min) * new_range) / old_range) + new_min
            
            val = new_value
            #//////////////////////////////////////////////////////////////////////////////////////
            print ("Current reading: %s %s" %(("%.2f" % val), units))
                
except ValueError as ve:
    print('Error read the image!!')
    x = "do nothing"
except IndexError:
    print('Error calculate the value!!')
    x = "do nothing"
