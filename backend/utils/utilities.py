import cv2
import numpy as np


def rect_contour(contours):
    rect_con = []
    for i in contours:
        area = cv2.contourArea(i)
        if area > 200:

            pori = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * pori, True)
            if len(approx) == 4:
                rect_con.append(i)
                # print(area)
    rect_con = sorted(rect_con, key=cv2.contourArea, reverse=True)
    return rect_con


def getCornerPoints(cont):
    pori = cv2.arcLength(cont, True)
    approx = cv2.approxPolyDP(cont, 0.02 * pori, True)
    return approx


def reoder(myPoint):
    myPoint = myPoint.reshape((4, 2))
    myNewPoint = np.zeros((4, 1, 2), np.uint16)
    add = myPoint.sum(1)
    # print(myPoint)
    # print(add)
    myNewPoint[0] = myPoint[np.argmin(add)]
    myNewPoint[3] = myPoint[np.argmax(add)]
    diff = np.diff(myPoint, axis=1)
    myNewPoint[1] = myPoint[np.argmin(diff)]
    myNewPoint[2] = myPoint[np.argmax(diff)]
    # print(diff)
    return myNewPoint


def split_boxes(img, row, col):
    rows = np.vsplit(img, row)
    # cv2.imshow("split", rows[2])
    boxes = []
    for r in rows:

        column = np.hsplit(r, col)
        for box in column:
            boxes.append(box)
    # print(len(boxes))

    return boxes


def showAns(img, myIndex, grading, ans, row, column):
    # def showAns(img, myIndex, row, column):
    secW = int(img.shape[1] / column)
    secH = int(img.shape[0] / row / 2)
    # print(secW, secH)
    x = 0
    y = 1
    while x <= 2 * row and y <= 2 * row:
        myColor = (0, 255, 0)
        myAns = int(myIndex[x])
        cx = (myAns * secW) + secW // 2
        cy = (x * secH) + secH

        if grading[int(x)] == 1:
            myColor = (0, 255, 0)


        else:
            myColor = (0, 0, 255)
            XansPoint = (int(ans[x]) * secW) + secW // 2
            YansPoint = (x * secH) + secH
            cv2.circle(img, (XansPoint, YansPoint), 7, (0, 255, 0), cv2.FILLED)
        cv2.circle(img, (cx, cy), 15, myColor, cv2.FILLED)
        myAns = int(myIndex[y])
        cx = (myAns * secW) + secW // 2
        cy = (y * secH)
        if grading[y] == 1:
            myColor = (0, 255, 0)
        else:
            myColor = (0, 0, 255)
            XansPoint = (int(ans[y]) * secW) + secW // 2
            YansPoint = (y * secH)
            cv2.circle(img, (XansPoint, YansPoint), 7, (0, 255, 0), cv2.FILLED)
        cv2.circle(img, (cx, cy), 15, myColor, cv2.FILLED)

        x += 2
        y += 2
    return img


def show_ans(img, ans, size):
    sec_w = int(img.shape[1] / size[1])
    sec_h = int(img.shape[0] / size[0] / 2)
    print(sec_w, sec_w)


def showMSSV(img, myIndex, row, column):
    secW = int(img.shape[1] / column)
    secH = int(img.shape[0] / row)
    # print(secW, secH)
    # print(myIndex)
    x = 0
    while x < column:
        myColor = (0, 255, 0)
        myAns = myIndex[x]
        # print(myAns)
        cx = (myAns * secW) * 2 + secW
        cy = (x * secH * 2) + secH
        cv2.circle(img, (cy, cx), 30, myColor, cv2.FILLED)
        x += 1
    return img
