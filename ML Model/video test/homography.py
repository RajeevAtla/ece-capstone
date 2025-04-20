import cv2
import numpy as np

# Load your provided image
img = cv2.imread('first_frame.jpg')
img_copy = img.copy()

# Store selected points
points = []

# Mouse callback for collecting 4 points
def select_point(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
        points.append((x, y))
        cv2.circle(img_copy, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow('Select 4 Corners of the Lot', img_copy)

cv2.imshow('Select 4 Corners of the Lot', img)
cv2.setMouseCallback('Select 4 Corners of the Lot', select_point)

print("🖱️ Click the 4 corners (clockwise or counterclockwise) of the desired area on the image.")

# Wait for user to select points
while True:
    cv2.imshow('Select 4 Corners of the Lot', img_copy)
    key = cv2.waitKey(1) & 0xFF
    if len(points) == 4:
        break
    elif key == 27:  # ESC to exit early
        cv2.destroyAllWindows()
        exit()

cv2.destroyAllWindows()

# Convert to NumPy array
pts_src = np.float32(points)

# Output size for bird's-eye view (adjust as needed)
width, height = 800, 600
pts_dst = np.float32([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]])

# Compute homography
H, status = cv2.findHomography(pts_src, pts_dst)

# Warp the image
warped = cv2.warpPerspective(img, H, (width, height))

# Show the result
cv2.imshow('Warped Top-Down View', warped)
cv2.waitKey(0)
cv2.destroyAllWindows()