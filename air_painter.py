import cv2
import numpy as np
import mediapipe as mp
import time
import math

# Camera setup
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Mediapipe hands
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

# Canvas
canvas = np.zeros((720, 1280, 3), dtype=np.uint8)

# Default values
drawColor = (255, 0, 255)
brushThickness = 10
eraserThickness = 50
currentColorName = "Purple"
mode = 'draw'  # draw, rectangle, star, heart

# Colors [(BGR), name]
colors = [
    ((255, 0, 255), "Purple"),
    ((255, 0, 0), "Blue"),
    ((0, 255, 0), "Green"),
    ((0, 0, 255), "Red"),
    ((0, 0, 0), "Eraser")
]

# Draw color buttons
def drawColorButtons(img):
    x = 100
    for color, name in colors:
        cv2.rectangle(img, (x, 20), (x + 100, 100), color, cv2.FILLED)
        text_color = (255, 255, 255) if color == (0, 0, 0) else (0, 0, 0)
        cv2.putText(img, name, (x + 10, 120), cv2.FONT_HERSHEY_PLAIN, 1.2, text_color, 2)
        x += 120

# Star drawing
def draw_star(img, center, size, color):
    cx, cy = center
    points = []
    for i in range(5):
        outer_angle = i * 2 * math.pi / 5 - math.pi / 2
        inner_angle = outer_angle + math.pi / 5
        outer_x = int(cx + size * math.cos(outer_angle))
        outer_y = int(cy + size * math.sin(outer_angle))
        inner_x = int(cx + (size // 2) * math.cos(inner_angle))
        inner_y = int(cy + (size // 2) * math.sin(inner_angle))
        points.append((outer_x, outer_y))
        points.append((inner_x, inner_y))
    points = np.array(points, np.int32).reshape((-1, 1, 2))
    cv2.polylines(img, [points], isClosed=True, color=color, thickness=3)

# Heart drawing
def draw_heart(img, center, size, color):
    cx, cy = center
    t = np.linspace(0, 2 * np.pi, 100)
    x = size * 16 * np.sin(t) ** 3
    y = -size * (13 * np.cos(t) - 5 * np.cos(2 * t) -
                 2 * np.cos(3 * t) - np.cos(4 * t))
    points = np.array([[int(cx + x[i]), int(cy + y[i])] for i in range(len(t))], np.int32)
    points = points.reshape((-1, 1, 2))
    cv2.polylines(img, [points], isClosed=True, color=color, thickness=3)

# Previous point
xp, yp = 0, 0

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    drawColorButtons(img)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lmList = []
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((cx, cy))

            if lmList:
                x1, y1 = lmList[8]  # Index
                x2, y2 = lmList[12]  # Middle

                fingersUp = y1 < y2

                # Brush circle
                cv2.circle(img, (x1, y1), 10, drawColor, cv2.FILLED)

                if fingersUp:  # Drawing Mode
                    if mode == 'draw':
                        if xp == 0 and yp == 0:
                            xp, yp = x1, y1
                        if drawColor == (0, 0, 0):
                            cv2.line(img, (xp, yp), (x1, y1), drawColor, eraserThickness)
                            cv2.line(canvas, (xp, yp), (x1, y1), drawColor, eraserThickness)
                        else:
                            cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                            cv2.line(canvas, (xp, yp), (x1, y1), drawColor, brushThickness)
                        xp, yp = x1, y1
                    elif mode == 'rectangle':
                        cv2.rectangle(canvas, (x1 - 60, y1 - 40), (x1 + 60, y1 + 40), drawColor, 3)
                    elif mode == 'star':
                        draw_star(canvas, (x1, y1), 50, drawColor)
                    elif mode == 'heart':
                        draw_heart(canvas, (x1, y1), 1, drawColor)
                else:
                    xp, yp = 0, 0
                    if y1 < 100:
                        x = 100
                        for color, name in colors:
                            if x < x1 < x + 100:
                                drawColor = color
                                currentColorName = name
                            x += 120

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    # Combine img and canvas
    imgGray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 20, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, canvas)

    # UI Text
    cv2.putText(img, f"Brush: {brushThickness}px", (1000, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, drawColor, 2)
    cv2.putText(img, f"Color: {currentColorName}", (1000, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, drawColor, 2)
    cv2.putText(img, f"Mode: {mode.upper()}", (1000, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, drawColor, 2)

    # Bottom instructions
    cv2.putText(img, "Press D: Draw | 1: Rect | 2: Star | 3: Heart", (20, 680), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200,200,200), 2)
    cv2.putText(img, "C: Clear | S: Save | +/-: Brush Size | ESC: Exit", (20, 710), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200,200,200), 2)

    # Show
    cv2.imshow("Air Painter", img)
    key = cv2.waitKey(1)

    if key == ord('d'):
        mode = 'draw'
    elif key == ord('1'):
        mode = 'rectangle'
    elif key == ord('2'):
        mode = 'star'
    elif key == ord('3'):
        mode = 'heart'
    elif key == ord('+') or key == ord('='):
        brushThickness += 5
    elif key == ord('-') or key == ord('_'):
        brushThickness = max(5, brushThickness - 5)
    elif key == ord('c'):
        canvas = np.zeros((720, 1280, 3), dtype=np.uint8)
    elif key == ord('s'):
        filename = f"drawing_{int(time.time())}.png"
        cv2.imwrite(filename, canvas)
        print(f"✅ Drawing saved as {filename}")
    elif key == 27:
        break

cap.release()
cv2.destroyAllWindows()
