import json
from PIL import Image
import base64
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import distance as dist
import cv2
import mediapipe as mp
import imutils
pixel_mm_cal = 1
def crop_center(image, crop_width, crop_height):
    # Get the center coordinates of the image
    center_x = image.width / 2
    center_y = image.height / 2

    # Calculate the coordinates of the crop box
    left = center_x - crop_width / 2
    top = center_y - crop_height / 2
    right = center_x + crop_width / 2
    bottom = center_y + crop_height / 2

    # Crop the image using the calculated coordinates
    cropped_image = image.crop((left, top, right, bottom))

    return cropped_image
def read_json(json_path):
    with open(json_path, "r") as json_file:
        json_data = json.load(json_file)
    return json_data


def find_largest_ellipse(image):
    # Read the image

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use Canny edge detection to find edges
    edges = cv2.Canny(blurred, 10, 200)

    # Find contours in the edge-detected image
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize variables to store the largest ellipse
    largest_ellipse = None
    max_area = 0

    # Iterate over the contours
    for contour in contours:
        # Fit an ellipse to the contour
        if len(contour) >= 5:
            ellipse = cv2.fitEllipse(contour)
            (x, y), (major_axis, minor_axis), angle = ellipse

            # Calculate the area of the ellipse
            area = np.pi * major_axis * minor_axis / 4

            # Update the largest ellipse if the current one has a larger area
            if area > max_area:
                max_area = area
                largest_ellipse = ellipse

    # Draw the largest ellipse on the original image
    if largest_ellipse is not None:
        mask = np.zeros_like(image)
        cv2.ellipse(mask, largest_ellipse, (255, 255, 255), thickness=-1)

        # Bitwise AND the original image with the mask
        roi = cv2.bitwise_and(image, mask)

        # Display the result

        # cv2.imshow("Largest Ellipse", roi)
        # cv2.waitKey(0)
        return roi, largest_ellipse
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils
def find_contours_inside(big_contour, all_contours, distance_threshold=10):
    """
    Find contours that are inside the big given contour and calculate distances.

    Parameters:
    - big_contour: The large contour to which we compare other contours.
    - all_contours: List of all contours to be checked.
    - distance_threshold: Threshold for considering a contour inside the big contour.

    Returns:
    - List of contours inside the big contour and their corresponding distances.
    """

    # Calculate the area of the big contour
    big_contour_area = cv2.contourArea(big_contour)

    # Filter contours based on area and hierarchy
    inside_contours = []
    for contour in all_contours:
        # Calculate area of each contour
        contour_area = cv2.contourArea(contour)

        # Check if the contour is inside and the area is smaller than the big contour
        if contour_area < big_contour_area and cv2.pointPolygonTest(big_contour, tuple(contour[0][0]), False) > 0:
            # Calculate the distance between the contours
            distance = cv2.pointPolygonTest(big_contour, tuple(contour[0][0]), True)

            # Check if the distance is within the threshold
            if abs(distance) < distance_threshold:
                inside_contours.append((contour, distance))

    return inside_contours
def depth_map_compensation(image, depth_map):
    """
    Apply depth map compensation to an image to correct for perspective effects.

    Parameters:
    - image: The input image.
    - depth_map: The depth map corresponding to the image.

    Returns:
    - Compensated image.
    """

    # Ensure the image and depth map have the same dimensions
    if image.shape[:2] != depth_map.shape:
        raise ValueError("Image and depth map dimensions do not match.")

    # Convert the depth map to the range [0, 1]
    normalized_depth = cv2.normalize(depth_map, None, 0, 1, cv2.NORM_MINMAX)

    # Create a 3D matrix with depth values for each channel
    depth_stack = np.dstack([normalized_depth] * 3)

    # Compensate the image based on the depth map
    compensated_image = image * depth_stack

    # Convert the result back to uint8 format
    compensated_image = (compensated_image * 255).astype(np.uint8)

    return compensated_image
def find_objects(roi,ellipse,threshold=20):
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(roi_gray, (5, 5), 0)
    wide = cv2.Canny(blurred, 10, 200)
    # cv2.imshow("Wide Edge Map", wide)
    # cv2.waitKey(0)


    # Apply Canny edge detection to the region inside the ellipse

    # Find contours in the Canny edge-detected image
    contours, _ = cv2.findContours(wide, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)

    # Find the largest contour
    biggie = max(contours, key=cv2.contourArea)
    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
    prev_contour_area = cv2.contourArea(sorted_contours[0])
    target_contour = None
    for id, contour in enumerate(sorted_contours):
        if prev_contour_area - cv2.contourArea(contour) > 1000:
            cv2.drawContours(roi, contour, -1, (0, 255, 0), 6)
            target_contour = contour
            # cv2.imshow("Contours", roi)
            # cv2.waitKey(0)
            # break
    target_contour_area = cv2.contourArea(target_contour)

    # Find contours inside the largest contour
    # Draw the contours on the original image
    # result = roi.copy()
    # cv2.drawContours(result, target_contour, -1, (0, 255, 0), 10)
    # # Display the result
    # cv2.imshow('Result', result)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return target_contour,target_contour_area

        # Draw the largest contour on the original image









def process_image(img):
    # Converting the input to grayscale
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(gray_image)

    # Returning the detected hands to calling function
    return results

def calculateDistbtw2Lms(l1,l2,img):
    h, w, c = img.shape
    c1x, c1y = int(l1.x * w), int(l1.y * h)
    c2x, c2y = int(l2.x * w), int(l2.y * h)
    distance = dist.euclidean((c1x, c1y), (c2x, c2y))
    return distance
def draw_hand_connections(img, results,cal_dist = 0.19):
    global pixel_mm_cal
    point0 = None
    point12 = None
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                if id == 0:
                    point0 = lm
                if id == 12:
                    point12 = lm
                h, w, c = img.shape

                # Finding the coordinates of each landmark
                cx, cy = int(lm.x * w), int(lm.y * h)

                # Printing each landmark ID and coordinates
                # on the terminal
                print(id, cx, cy)

                # Creating a circle around each landmark
                cv2.circle(img, (cx, cy), 10, (0, 255, 0),
                           cv2.FILLED)
                cv2.putText(img, str(id), (cx+10, cy+10),
                            cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
                # Drawing the landmark connections
                mpDraw.draw_landmarks(img, handLms,
                                      mpHands.HAND_CONNECTIONS)
        if point0 and point12:
            cv2.line(img, (int(point0.x * w), int(point0.y * h)), (int(point12.x * w), int(point12.y * h)), (0, 255, 0), 2)
            print("Distance between 0 and 12:", pixel_mm_cal*calculateDistbtw2Lms(point0, point12, img))
            if abs(pixel_mm_cal*calculateDistbtw2Lms(point0, point12, img) - cal_dist) > 0.4:
                pixel_mm_cal = cal_dist / calculateDistbtw2Lms(point0, point12, img)

        return img
def getCals(volume, food):
    volume = volume
    question = "How many calories are there in a %.02f cubic meter %s" % \
               (volume, food)
    res = client.query(question)
    answer = next(res.results).text
    return answer

def VolumeEstimation(json_data):
    data = json_data
    cmap = plt.get_cmap('viridis')

    image_bytes = base64.b64decode(data['cameraImage'])
    depth_image_bytes = base64.b64decode(data['depthMapImage'])
    # Convert bytes to numpy array
    np_array = np.frombuffer(image_bytes, dtype=np.uint8)

    # Read the image using OpenCV
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    image_raw = imutils.resize(image, width=1440, height=1440)
    results = process_image(image_raw)
    draw_hand_connections(image, results, 0.34)

    # Displaying the output
    # cv2.imshow("Hand tracker", image)
    # cv2.waitKey(0)

    # find_largest_circle(image_raw)
    roi, ellipse = find_largest_ellipse(image_raw)

    target, area = find_objects(roi, ellipse, threshold=20)
    area = area * pixel_mm_cal * pixel_mm_cal
    scaling_coef = 4500
    area = area * scaling_coef
    volume = area * 0.05
    print("Area of the object is: ", area, "m^2")
    print("Volume of the object is: ", volume, "m^3")
    return volume
    
def main():

    keys = [['cameraEulerAngle', 'camImageResolution', 'timeStamp', \
            'cameraImage', 'depthMap', 'cameraIntrinsics', \
            'cameraTransform', 'cameraPos', 'depthMapResolution', 'depthMapImage']]

    data = read_json("scan 9.json")
    cmap = plt.get_cmap('viridis')


    image_bytes = base64.b64decode(data['cameraImage'])
    depth_image_bytes = base64.b64decode(data['depthMapImage'])
    # Convert bytes to numpy array
    np_array = np.frombuffer(image_bytes, dtype=np.uint8)

    # Read the image using OpenCV
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    image_raw = imutils.resize(image, width=1440, height=1440)
    results = process_image(image_raw)
    draw_hand_connections(image, results, 0.34)

    # Displaying the output
    # cv2.imshow("Hand tracker", image)
    # cv2.waitKey(0)

    # find_largest_circle(image_raw)
    roi, ellipse = find_largest_ellipse(image_raw)

    target, area = find_objects(roi,ellipse,threshold=20)
    area = area * pixel_mm_cal *pixel_mm_cal
    scaling_coef = 4500
    area = area * scaling_coef
    print("Area of the object is: ", area, "m^2")
    print("Volume of the object is: ", area * 0.05, "m^3")


    # print("Calories in the object is: ", getCals(area * 0.05, "apple"), "calories")





if __name__ == "__main__":
    main()