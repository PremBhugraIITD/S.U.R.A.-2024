import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from pathlib import Path
# from ADB_extractor import image_retrieval_from_phone
from Thresholds import get_threshes
ref_point = []
cropping = False

# File path to save the data
file_path = "Calibration_result.txt"
with open(file_path, "w") as file:
    file.write("Calibration started...\n")
def crop_image(event, x, y, flags, param):
    '''
    Handles mouse events for cropping an image. Tracks the region selected by the user
    using left mouse button events and dynamically updates the cropping area.

    Args:
        event: OpenCV mouse event (e.g., button press, movement, release).
        x, y: Coordinates of the mouse pointer during the event.
        flags: OpenCV flags for mouse event.
        param: Clone of the image to allow real-time rectangle drawing.
    '''
    global ref_point, cropping

    clone = param.copy()  # Copy the original image to draw the rectangle dynamically

    if event == cv2.EVENT_LBUTTONDOWN:
        ref_point = [(x, y)]
        cropping = True

    elif event == cv2.EVENT_MOUSEMOVE:
        if cropping:
            # Draw a rectangle in real-time as the user selects the ROI
            current_point = (x, y)
            top_left = (min(ref_point[0][0], current_point[0]), min(ref_point[0][1], current_point[1]))
            bottom_right = (max(ref_point[0][0], current_point[0]), max(ref_point[0][1], current_point[1]))
            cv2.rectangle(clone, top_left, bottom_right, (0, 0, 255), 2)  # Draw the rectangle in red
            # Resize the window (width, height)
            
            # Move the window (x, y position on screen)
            cv2.moveWindow("Crop Image", 0 , 0)
            cv2.imshow("Crop Image", clone)

    elif event == cv2.EVENT_LBUTTONUP:
        ref_point.append((x, y))
        cropping = False

        if len(ref_point) != 2:
            with open(file_path, "a") as file:
                file.write("Invalid cropping points. Please select a valid ROI.\n")
            raise ValueError("Invalid cropping points. Please select a valid ROI.")
        
        # Draw the final rectangle around the region of interest
        top_left = (min(ref_point[0][0], x), min(ref_point[0][1], y))
        bottom_right = (max(ref_point[0][0], x), max(ref_point[0][1], y))
        cv2.rectangle(param, top_left, bottom_right, (0, 0, 255), 2)  # Draw the rectangle in red
        # Resize the window (width, height)
        
        # Move the window (x, y position on screen)
        cv2.moveWindow("Crop Image", 0 , 0)
        cv2.imshow("Crop Image", param)
# Function to resize the image to fit within the screen
def resize_to_fit_screen(image, screen_width=1920, screen_height=1080):
    """
    Resizes the image to fit within the screen dimensions while maintaining the aspect ratio.

    Args:
        image: The input image to resize.
        screen_width: Maximum width of the screen.
        screen_height: Maximum height of the screen.

    Returns:
        Resized image and the scale factor.
    """
    h, w = image.shape[:2]
    scale = min(screen_width / w, screen_height / h)
    if scale < 1:  # Resize only if the image is larger than the screen
        resized_image = cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        return resized_image, scale
    return image, 1.0  # Return the original image if no resizing is needed

# Function to allow the user to crop the image
def get_cropped_image(image):
    '''
    Allows the user to interactively crop the input image using OpenCV.

    Args:
        image: Input image to be cropped.

    Returns:
        Cropped portion of the image or the original image if cropping is skipped.
    '''
    global ref_point
    
    if image is None:
        with open(file_path, "a") as file:
            file.write("Input image is None. Please provide a valid image.\n")
        raise ValueError("Input image is None. Please provide a valid image.")
    
    # Resize the image to fit the screen
    resized_image, scale = resize_to_fit_screen(image)

    clone = resized_image.copy()

    # Set up the window and set the mouse callback function for cropping
    cv2.namedWindow("Crop Image")
    # Move the window (x, y position on screen)
    cv2.moveWindow("Crop Image", 0 , 0)
    cv2.setMouseCallback("Crop Image", crop_image, param=clone)

    # Display the image and wait for cropping
    while True:
        cv2.imshow("Crop Image", clone)
        key = cv2.waitKey(1) & 0xFF

        # Press 'r' to reset cropping
        if key == ord("r"):
            ref_point = []  # Clear previous ROI points
            # clone = image.copy()  # Reset the clone to the original image
            print("Reset cropping selection.")
            with open(file_path, "a") as file:
                file.write("Reset cropping selection.\n")

        # Press 'c' to confirm the crop and break the loop
        elif key == ord("c") and len(ref_point) == 2:
            print("Cropping confirmed.")
            cropping =True
            with open(file_path, "a") as file:
                file.write("Cropping confirmed.\n")
            break

        # Press 'n' to skip cropping
        elif key == ord("n"):
            cv2.destroyAllWindows()  # Close the window
            return image  # Return the original image without cropping

        # Check if the window is closed
        if cv2.getWindowProperty("Crop Image", cv2.WND_PROP_VISIBLE) < 1:
            print("Window closed.")
            with open(file_path, "a") as file:
                file.write("Window closed.\n")
            cv2.destroyAllWindows()
            return image  # Return the original image without cropping

    # Close the cropping window after confirmation
    cv2.destroyAllWindows()

    # Crop the selected area
    if len(ref_point) == 2:
        x0, y0 = int(ref_point[0][0] / scale), int(ref_point[0][1] / scale)
        x1, y1 = int(ref_point[1][0] / scale), int(ref_point[1][1] / scale)
        # Get the coordinates in correct order
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        
        if x0 == x1 or y0 == y1:
            with open(file_path, "a") as file:
                file.write("Cropping region must have a non-zero area.\n")
            raise ValueError("Cropping region must have a non-zero area.")
        
        cropped_image = image[y0:y1, x0:x1]
        return cropped_image
    else:
        return image
def read_last_thresholds(file_path2='thresholds_log.txt'):
    """Reads the last logged thresholds from the file."""
    try:
        with open(file_path2, 'r') as file:
            lines = file.readlines()
            # If the file is not empty, get the last line
            if lines:
                last_line = lines[-1].strip()
                # Extract the values of lower and upper thresholds
                lower_threshold = int(last_line.split('Final Lower Threshold: ')[1].split(',')[0])
                upper_threshold = int(last_line.split('Final Upper Threshold: ')[1].split(',')[0])
                return lower_threshold, upper_threshold
            else:
                print("No thresholds found in the file.")
                with open(file_path, "a") as file:
                    file.write("No thresholds found in the file.\n")
                return None, None
    except FileNotFoundError:
        print("Thresholds log file not found.")
        with open(file_path, "a") as file:
            file.write("Thresholds log file not found.\n")
        return None, None
    
def preprocess_image(image_path):
    '''
    Preprocess the input image by reading, converting to grayscale, 
    applying Gaussian blur, and detecting edges using Canny.

    Parameters:
        image_path (str): Path to the input image file.

    Returns:
        tuple: Edges image and original image.

    Raises:
        FileNotFoundError: If the image cannot be loaded.
        ValueError: If the provided path is not a valid image file.
    '''
    try:
        image = cv2.imread(image_path)
        
        if image is None:
            with open(file_path, "a") as file:
                file.write(f"Could not load image from path: {image_path}\n")
            raise FileNotFoundError(f"Could not load image from path: {image_path}")
        global cropped_image
        cropped_image = get_cropped_image(image)
        image = cropped_image    
        get_threshes(image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        lower_threshold, upper_threshold = read_last_thresholds()
        if lower_threshold is not None and upper_threshold is not None:
            edges = cv2.Canny(blurred, lower_threshold, upper_threshold)
        else:
            edges = cv2.Canny(blurred, 50, 150)
        return edges, image
    except Exception as e:
        with open(file_path, "a") as file:
            file.write(f"Error in preprocessing image: {e}\n")
        raise ValueError(f"Error in preprocessing image: {e}")

def find_contour(edges):
    '''
    Identify contours in the edge-detected image and select the largest contour.

    Parameters:
        edges (numpy.ndarray): Edge-detected image.

    Returns:
        tuple: All contours and the largest contour.

    Raises:
        ValueError: If no contours are found.
    '''
    # Find contours in the edges image
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        with open(file_path, "a") as file:
            file.write("No contours found in the edge-detected image.\n")
        raise ValueError("No contours found in the edge-detected image.")
    
    all_points = np.vstack(contours)  # Stack all contour points into one array
    contour = all_points.reshape(-1, 2)
    return contours, contour

def measure_diameters(contour):
    '''
    Calculate the maximum diameter (d_e) and secondary diameter (d_s) of a drop.

    Parameters:
        contour (numpy.ndarray): Largest contour points.

    Returns:
        tuple: Maximum diameter (d_e), secondary diameter (d_s), 
               left and right points at y-level for d_s.

    Raises:
        ValueError: If contour data is not in expected format.
    '''
    try:
        # Get the points in the contour
        points = np.squeeze(contour)
        if points.ndim != 2 or points.shape[1] != 2:
            with open(file_path, "a") as file:
                file.write("Contour points are not in the expected format.\n")
            raise ValueError("Contour points are not in the expected format.")
        # Split the x and y coordinates
        x = points[:, 0]
        y = points[:, 1]

        # Perform interpolation (linear interpolation)
        f_x = interp1d(np.arange(len(x)), x, kind='linear', fill_value="extrapolate")
        f_y = interp1d(np.arange(len(y)), y, kind='linear', fill_value="extrapolate")

        # Generate new set of points
        new_x = f_x(np.linspace(0, len(x)-1, num=500))  # 500 points for smoother curve
        new_y = f_y(np.linspace(0, len(y)-1, num=500))
        # points = np.vstack((new_x, new_y)).T
        # Find the leftmost and rightmost points for d_e
        left_point = points[np.argmin(points[:, 0])]
        right_point = points[np.argmax(points[:, 0])]
        d_e = np.linalg.norm(right_point - left_point)
        
        # Find the lowest point
        bottom_point = points[np.argmax(points[:, 1])]
        
        # Find the y-coordinate d_e units above the bottom point
        y_above = bottom_point[1] - d_e
        
        # Find the points within a small range around y_above
        tolerance = 3  # Adjust this value as needed
        points_at_y_above = points[(points[:, 1] >= y_above - tolerance) & (points[:, 1] <= y_above + tolerance)]

        
        if len(points_at_y_above) == 0:
            print("No points found at y = bottom_y - d_e level.")
            with open(file_path, "a") as file:
                file.write("No points found at y = bottom_y - d_e level.\n")
            return d_e, None, None, None

        left_point_at_y = points_at_y_above[np.argmin(points_at_y_above[:, 0])]
        right_point_at_y = points_at_y_above[np.argmax(points_at_y_above[:, 0])]
        d_s = np.linalg.norm(right_point_at_y - left_point_at_y)
        return d_e, d_s, left_point_at_y, right_point_at_y
    except Exception as e:
        with open(file_path, "a") as file:
            file.write(f"Error in measuring diameters: {e}\n")
        raise ValueError(f"Error in measuring diameters: {e}")

def calculate_needle_diameter(image, blur_kernel=(5, 5)):
    '''
    Calculate the diameter of the needle using edge detection and contour analysis.

    Parameters:
        image (numpy.ndarray): Input image in BGR format.
        blur_kernel (tuple): Gaussian blur kernel size.
        canny_thresholds (tuple): Canny edge detection thresholds.

    Returns:
        tuple: Diameter of the needle in pixels and its key points.

    Raises:
        ValueError: If no contours are found or contour format is incorrect.
    '''
    try:
        # Step 1: Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Step 2: Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, blur_kernel, 0)

        # Step 3: Perform edge detection using Canny
        lower_threshold, upper_threshold = read_last_thresholds()
        if lower_threshold is not None and upper_threshold is not None:
            edges = cv2.Canny(blurred, lower_threshold, upper_threshold)
        else:
            edges = cv2.Canny(blurred, 50, 150)

        # Step 4: Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            with open(file_path, "a") as file:
                file.write("No contours found. Check the image quality or adjust parameters.\n")
            raise ValueError("No contours found. Check the image quality or adjust parameters.")

        # Step 5: Use the largest contour to determine the needle diameter
        all_points = np.vstack(contours)  # Stack all contour points into one array
        largest_contour = all_points.reshape(-1, 2)
        points = np.squeeze(largest_contour)

        if points.ndim != 2 or points.shape[1] != 2:
            with open(file_path, "a") as file:
                file.write("Contour points are not in the expected format.\n")
            raise ValueError("Contour points are not in the expected format.")

        # Step 6: Find the 10th point from the top based on the y-coordinate
        sorted_points = sorted(points, key=lambda x: x[1])  # Sort by y-coordinate
        tenth_point = sorted_points[0]  # 10th point from the top (index 9)
        y_level = tenth_point[1]  # Use the y-coordinate of this point as the reference
        
        # Step 7: Find leftmost and rightmost points at this y-level
        leftmost_point = None
        rightmost_point = None

        for point in points:
            if point[1] == y_level:  # Check if the point is at the specified height
                if leftmost_point is None or point[0] < leftmost_point[0]:
                    leftmost_point = point
                if rightmost_point is None or point[0] > rightmost_point[0]:
                    rightmost_point = point

        # Step 8: Calculate the needle diameter
        if leftmost_point is None or rightmost_point is None:
            with open(file_path, "a") as file:
                file.write("Could not find leftmost or rightmost points at the specified height.\n")
            raise ValueError("Could not find leftmost or rightmost points at the specified height.")

        diameter = np.linalg.norm(np.array(rightmost_point) - np.array(leftmost_point))
        return diameter,leftmost_point,rightmost_point
    except Exception as e:
        with open(file_path, "a") as file:
            file.write(f"Error in calculating needle diameter: {e}\n")
        raise ValueError(f"Error in calculating needle diameter: {e}")


def calculate_corrected_needle_diameter(d_e, d_s, d_n):
    '''
    Calculate corrected needle diameter using measured diameters and known parameters.

    Parameters:
        d_e (float): Maximum diameter of the drop in pixels.
        d_s (float): Secondary diameter of the drop in pixels.
        d_n (float): diameter of the needle in pixels.

    Returns:
        float: Corrected needle diameter in mm.
    '''
    # H = ((d_s/d_e)**2.4898)/(0.35)  # correction coefficient H
    try:
        C_n_d= (((21.292282)*(d_s**2.49)*(d_n**2))/(d_e**4.49))**0.5
        return C_n_d
    except ZeroDivisionError:
        with open(file_path, "a") as file:
            file.write("Maximum diameter (d_e) must not be zero.\n")
        raise ValueError("Maximum diameter (d_e) must not be zero.")
    except Exception as e:
        with open(file_path, "a") as file:
            file.write(f"Error in calibrating: {e}\n")
        raise ValueError(f"Error in calibrating: {e}")

def main(image_path):
    '''
    Main function to process an image, measure diameters, 
    calculate corrected needle diameter

    Parameters:
        image_path (str): Path to the input image file.
    '''
    edges, image = preprocess_image(image_path)
    contours, contour = find_contour(edges)
    de, ds, left_point_at_y, right_point_at_y = measure_diameters(contour)
    if ds is None:
        print("No points found at y = bottom_y - d_e level")
        with open(file_path, "a") as file:
            file.write("No points found at y = bottom_y - d_e level\n")
        return
    
    needle_diameter,nlp,nrp=calculate_needle_diameter(image)
    corrected_needle_diameter = calculate_corrected_needle_diameter(de,ds,needle_diameter)
    
    # Create the text content
    text_content = (
        f"Corrected diameter of the needle after calibration: {corrected_needle_diameter/1000} m\n"   
    )

    # Write the data to a text file
    with open(file_path, "w") as file:
        file.write(text_content)

def get_latest_file(directory):
    """
    Get the most recent file from the specified directory.

    Args:
        directory (str): Path to the directory.

    Returns:
        str: Path to the latest file, or None if no files are found.
    """
    try:
        # Convert directory path to a Path object
        path = Path(directory)

        # List all files in the directory
        files = [f for f in path.iterdir() if f.is_file()]

        if not files:
            print(f"No files found in {directory}.")
            with open(file_path, "a") as file:
                file.write(f"No files found in {directory}.\n")
            return None

        # Find the most recent file based on modification time
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        return str(latest_file)
    except Exception as e:
        with open(file_path, "a") as file:
            file.write(f"An error occurred: {e}\n")
        print(f"An error occurred: {e}")
        return None

def load_latest_image_path():
    # Replace with the directory where files are stored on your PC
    DIRECTORY = r"C:\Users\91982\OneDrive\Desktop\SURA\Retrieved_Data_Input"

    latest_file = get_latest_file(DIRECTORY)
    if latest_file:
        return latest_file
    else:
        print("No file could be retrieved.")
        with open(file_path, "a") as file:
            file.write("No file could be retrieved.\n")

def calibration(O_n_d=1.0194*10**(-3), density=997):
    # image_retrieval_from_phone()
    os.chdir(r"C:\Users\91982\OneDrive\Desktop\SURA")
    # image_path= str(load_latest_image_path())
    image_path = r"C:\Users\91982\Downloads\pdgoniowater.jpg"
    main(image_path)

# calibration()
# image_path = r"C:\Users\91982\Downloads\pdlab3.jpg"

# image_path = r"C:\Users\Prem\OneDrive - IIT Delhi\Desktop\GitHub\S.U.R.A.-2024\python\image_final.png"
# image_path = r"C:\Users\Prem\OneDrive - IIT Delhi\Desktop\GitHub\S.U.R.A.-2024\python\image_sample.png"
image_path = r"C:\Users\Prem\OneDrive - IIT Delhi\Desktop\GitHub\S.U.R.A.-2024\python\water.jpg"
# image_path = r"C:\Users\Prem\OneDrive - IIT Delhi\Desktop\GitHub\S.U.R.A.-2024\python\chloroform.jpg"

main(image_path)