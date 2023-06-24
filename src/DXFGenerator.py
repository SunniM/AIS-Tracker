import cv2
import numpy as np
import ezdxf

def generate_dxf_from_contours(contours, width, height, border_size, output_file):
    if len(contours) == 0:
        return  # Exit if no contours are provided

    # Create a DXF document
    doc = ezdxf.new('R2010')  # Use the DXF R2010 format

    # Create a new layer for the contours
    contour_layer = doc.layers.new(name='Contours')

    # Get the model space of the document
    msp = doc.modelspace()

    # Calculate the border coordinates
    border_coords = [
        (border_size, border_size),
        (width - border_size, border_size),
        (width - border_size, height - border_size),
        (border_size, height - border_size),
        (border_size, border_size)
    ]

    # Add the border as a polyline entity to the model space
    msp.add_lwpolyline(border_coords, dxfattribs={'layer': 'Contours', 'closed': True})

    # Scale and flip the contour points for each contour
    for contour in contours:
        if len(contour) > 0:
            # Scale the contour points based on the desired size
            scale_x = (width - 2 * border_size) / float(image.shape[1])
            scale_y = (height - 2 * border_size) / float(image.shape[0])
            scaled_contour = contour[:, 0, :] * np.array([scale_x, scale_y])

            # Flip the y-coordinates of the scaled contour points
            flipped_contour = np.array([(point[0] + border_size, height - point[1] - border_size) for point in scaled_contour])

            # Create a new polyline entity for the contour and add it to the model space
            msp.add_lwpolyline(list(flipped_contour), dxfattribs={'layer': 'Contours'})

    # Save the DXF file
    doc.saveas(output_file)

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

# Specify the desired size of the DXF drawing and the border size
width = 610  # Width in units (e.g., millimeters)
height = 432  # Height in units (e.g., millimeters)
border_size = 2.0  # Border size in units (e.g., millimeters)

# Generate a single DXF file for all contours with a border
output_file = 'contours.dxf'
generate_dxf_from_contours(contours, width, height, border_size, output_file)
