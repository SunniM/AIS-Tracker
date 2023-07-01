import cv2
import numpy as np
import ezdxf
import matplotlib.pyplot as plt

def generate_dxf_from_contours(contours, width, height, output_file, min_contour_area):
    if len(contours) == 0:
        return  # Exit if no contours are provided

    # Create a DXF document
    doc = ezdxf.new('R2010')  # Use the DXF R2010 format

    # Create a new layer for the contours
    contour_layer = doc.layers.new(name='Contours')

    # Get the model space of the document
    msp = doc.modelspace()

    # Calculate the scaling factors
    image_width = image.shape[1]
    image_height = image.shape[0]

    scale_x = width / image_width
    scale_y = height / image_height

    # Scale and flip the contour points for each contour
    for contour in contours:
        if len(contour) > 0:
            # Calculate the area of the contour
            contour_area = cv2.contourArea(contour)

            # Check if the contour area is below the threshold for closing gaps
            if contour_area < min_contour_area:
                # Close the contour by adding the first point as the last point
                if not np.array_equal(contour[0], contour[-1]):
                    contour = np.vstack((contour, [contour[0]]))

            # Scale the contour points based on the desired size
            scaled_contour = contour[:, 0, :] * np.array([scale_x, scale_y])

            # Flip the y-coordinates of the scaled contour points
            flipped_contour = np.array([(point[0], height - point[1]) for point in scaled_contour])

            # Create a new polyline entity for the contour and add it to the model space
            msp.add_lwpolyline(list(flipped_contour), dxfattribs={'layer': 'Contours'})

    # Save the DXF file
    doc.saveas(output_file)

# Load the image
image = cv2.imread('d:\Programming Projects\C++\AIS Tracker\AIS-Tracker\src\map_image.png', cv2.IMREAD_UNCHANGED)

# Convert img to gray
img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# Set a threshold
thresh = 170
# Get threshold image
ret, thresh_img = cv2.threshold(img_gray, thresh, 255, cv2.THRESH_BINARY)
# Find contours
contours, hierarchy = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Specify the desired size of the DXF drawing and the minimum contour area to close gaps
width = 0.609682  # Width in units (e.g., meters)
height = 0.4316  # Height in units (e.g., meters)
min_contour_area = 150000  # Minimum contour area to close gaps (adjust as needed)

# Generate a single DXF file for all contours
output_file = 'contours.dxf'
generate_dxf_from_contours(contours, width, height, output_file, min_contour_area)

# Preview the contour image
plt.imshow(cv2.cvtColor(img_gray, cv2.COLOR_BGR2RGB))
plt.title('Contour Image')
plt.show()
