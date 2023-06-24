import cv2
import numpy as np
import ezdxf

# Load the image
image = cv2.imread('d:\Programming Projects\C++\AIS Tracker\AIS-Tracker\src\map_image.jpg', cv2.IMREAD_UNCHANGED)

# Convert img to gray
img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# Set a threshold
thresh = 85
# Get threshold image
ret, thresh_img = cv2.threshold(img_gray, thresh, 255, cv2.THRESH_BINARY)
# Find contours
contours, hierarchy = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Create an empty image for contours
img_contours = np.zeros(image.shape, dtype=np.uint8)
# Draw the contours on the empty image
cv2.drawContours(img_contours, contours, -1, (0, 255, 0), 2)
# Save image
cv2.imwrite('contours.png', img_contours)

squeezed = [np.squeeze(cnt, axis=1) for cnt in contours]
inverted_squeezed = [arr * [1, -1] for arr in squeezed]

dwg = ezdxf.new("R2010")
msp = dwg.modelspace()
dwg.layers.new(name="greeny green lines", dxfattribs={"color": 3})

for ctr in inverted_squeezed:
   for n in range(len(ctr)):
        if n >= len(ctr) - 1:
            n = 0
        try:
            msp.add_line(ctr[n], ctr[n + 1], dxfattribs={"layer": "greeny green lines", "lineweight": 20})
        except IndexError:
            pass

dwg.saveas("output.dxf")