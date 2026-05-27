import numpy as np
import cv2

# Create synthetic image: black background with a bright circle (simulated IR LED)
img = np.zeros((480, 640), dtype=np.uint8)
cv2.circle(img, (320, 200), 10, 255, -1)  # center at (320,200)

# Apply same pipeline as tracking_2d.py
_, thresh = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY)
M = cv2.moments(thresh)

if M['m00'] == 0:
    print('FAIL: No bright region detected')
    raise SystemExit(2)

cX = int(M['m10']/M['m00'])
cY = int(M['m01']/M['m00'])
print(f'Detected centroid: X={cX}, Y={cY}')

# Simple check (allow small offset due to rasterization)
if abs(cX - 320) <= 1 and abs(cY - 200) <= 1:
    print('PASS: centroid matches expected location')
    raise SystemExit(0)
else:
    print('FAIL: centroid differs from expected')
    raise SystemExit(3)
