import json
from pydantic import BaseModel
from io import BytesIO
from PIL import Image
import base64
import numpy as np
import matplotlib.pyplot as plt
from skimage import io, transform
import bordercrop
import cv2
import mediapipe as mp
import imutils

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

def resize_and_crop(source_image, target_size):
    # Open the source image

    # Calculate the target aspect ratio
    target_aspect_ratio = target_size[0] / target_size[1]

    # Calculate the aspect ratio of the source image
    source_aspect_ratio = source_image.width / source_image.height

    # Determine which dimension to maximize
    if source_image.width < source_image.height:
        # Maximize width
        new_height = int(source_image.width / target_aspect_ratio)
        resized_image = source_image.resize((target_size[0], new_height), Image.Resampling.LANCZOS)

    else:
        # Maximize height
        new_width = int(source_image.height * target_aspect_ratio)
        resized_image = source_image.resize((new_width, target_size[1]), Image.Resampling.LANCZOS)
    # Crop the resized image to the target size
    left = (resized_image.width - target_size[0]) / 2
    top = (resized_image.height - target_size[1]) / 2
    right = (resized_image.width + target_size[0]) / 2
    bottom = (resized_image.height + target_size[1]) / 2

    cropped_image = resized_image.crop((left, top, right, bottom))

    return cropped_image

def process_image(imageData):
    # Decode base64 string to bytes
    decoded_data = base64.b64decode(imageData)

    # Create a BytesIO object from the decoded bytes
    image_bytes = BytesIO(decoded_data)

    # Open the image using PIL
    image = Image.open(image_bytes)
    image = image.rotate(-90).convert('RGBA')
    image = crop_center(image, 1440, image.height)
    # image = bordercrop.crop(image)

    # Process the image as needed
    # ...

    # Return a response, if necessary
    return {"status": "success", "image": image}
def PIL2CV(image):
    open_cv_image = np.array(image)
    # Convert RGB to BGR
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    return open_cv_image
def process_image_cv(img):
    # Converting the input to grayscale
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(gray_image)
    # Returning the detected hands to calling function
    return results

def draw_hand_connections(img, results):
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape

                # Finding the coordinates of each landmark
                cx, cy = int(lm.x * w), int(lm.y * h)

                # Printing each landmark ID and coordinates
                # on the terminal
                print(id, cx, cy)

                # Creating a circle around each landmark
                cv2.circle(img, (cx, cy), 10, (0, 255, 0),
                           cv2.FILLED)
                # Drawing the landmark connections
                mpDraw.draw_landmarks(img, handLms,
                                      mpHands.HAND_CONNECTIONS)

        return img
def process_depth_image(imageData):
    # Decode base64 string to bytes
    decoded_data = base64.b64decode(imageData)

    # Create a BytesIO object from the decoded bytes
    image_bytes = BytesIO(decoded_data)

    # Open the image using PIL
    image = Image.open(image_bytes)
    image = image.convert('RGBA')
    image = crop_center(image, 1440, image.height)
    # image = bordercrop.crop(image)

    # Process the image as needed
    # ...

    # Return a response, if necessary
    return {"status": "success", "image": image}

keys = [['cameraEulerAngle', 'camImageResolution', 'timeStamp', \
         'cameraImage', 'depthMap', 'cameraIntrinsics', \
         'cameraTransform', 'cameraPos', 'depthMapResolution','depthMapImage']]

data = read_json("scan 8.json")
cmap = plt.get_cmap('viridis')
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils
def AffineTransformThingy(scaleX,scaleY):
    return transform.AffineTransform(
        scale=(scaleX, scaleY),
    )


print(data.keys())
image = data['cameraImage']
depthImage = data['depthMapImage']
depthImage = process_depth_image(depthImage)
image = process_image(image)
# image['image'].show()
# depthImage['image'].show()
# depthImage['image'] = depthImage['image'].resize((1440,depthImage['image'].height*1440/depthImage['image'].width), resample = Image.Resampling.LANCZOS)
# depthImage['image'] = crop_center(depthImage['image'], 1440, image['image'].height)
# image['image'] = crop_center(image['image'], min(image['image'].width, depthImage['image'].width), min(image[
#                                                                                                            'image'].height,\
#                                                                                                       depthImage['image'].height))
# depthImage['image'] = crop_center(depthImage['image'], min(image['image'].width,depthImage['image'].width), min(image['image'].height,\
#                                                                                                       depthImage['image'].height))
# image['image'].show()# depth_map = np.array(data['depthMap'])[:, ::-1]
# depth_colored = (cmap(depth_map / np.max(depth_map)) * 255).astype('uint8')
# display_image = Image.fromarray(depth_colored)
# display_image.show()
# display_image = display_image.transform((image['image'].size[0], image['image'].size[1]),method = Image.Transform.AFFINE, resample = Image.LANCZOS)
# display_image = crop_center(display_image, image['image'].size[0], image['image'].size[1])
# display_image = resize_and_crop(display_image, image['image'].size)

# matrix1 = AffineTransformThingy(1/depth_colored.shape[0], 1/depth_colored.shape[1])
# depth_colored_resized_affine = transform.warp(depth_colored, matrix1.inverse)
#
# matrix2 = AffineTransformThingy(image['image'].size[0], image['image'].size[1])
#
# final_depth_map = transform.warp(depth_colored_resized_affine, matrix2)

alpha = 0.6  # Adjust the alpha value as needed

depthImage['image'] = depthImage['image'].resize((1803,1440), resample = Image.Resampling.LANCZOS)
depthImage['image'] = crop_center(depthImage['image'], 1440, 1440)
result_image = Image.blend(image['image'], depthImage['image'], alpha)
# Display the result
# result_image.show()
image_cv = imutils.resize(np.array(image['image']), width=1440, height=1440)
results = process_image_cv(image_cv)
draw_hand_connections(image_cv, results)
disp = draw_hand_connections(image_cv, results)

# Displaying the output
cv2.imshow("Hand tracker", disp)

