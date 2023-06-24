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

# Create a DXF document
doc = ezdxf.new('R2010')  # Use the DXF R2010 format

# Create a new layer for the contours
contour_layer = doc.layers.new(name='Contours')

# Get the model space of the document
msp = doc.modelspace()

# Create a new polyline entity for each contour and add it to the model space
for contour in contours:
    points = [tuple(point[0]) for point in contour]
    flipped_points = [(x, image.shape[0] - y) for x, y in points]  # Flip the y-coordinates
    flipped_points.append(flipped_points[0])  # Repeat the first point to close the polyline
    msp.add_lwpolyline(flipped_points, dxfattribs={'layer': 'Contours'})

# Save the DXF file
doc.saveas('contours.dxf')
