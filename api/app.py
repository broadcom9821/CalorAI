from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sys
from PIL import Image
import io
import base64
sys.path.append('./api/')  # Replace with the actual path to the directory
from test import VolumeEstimation
import requests
sys.path.append('./classification/')  # Replace with the actual path to the directory
from foodClassify import make_prediction, load_model  # Import make_prediction from prediction_module

densities = {
    "apple": 620,
    "banana": 520,
    "pizza": 968.7966649,
    "donut": 526.9,
    "hotdog": 430,
    "hamburger": 550,
    "icecream": 750,
    "french_fries": 240.92,
    "cup_cakes": 390,
}

app = FastAPI()
model = load_model('./classification/models/modelV2.pth')

class Prediction(BaseModel):
    label: str

def wolframAPI(query):
    app_id = "T7RKQX-T94YKAJ69R"
    url = "http://api.wolframalpha.com/v2/spoken?appid=" + app_id + "&i=" + query
    response = requests.get(url)
    return response.text    

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

def process_image(imageData):
    # Decode base64 string to bytes
    decoded_data = base64.b64decode(imageData)

    # Create a BytesIO object from the decoded bytes
    image_bytes = io.BytesIO(decoded_data)

    # Open the image using PIL
    image = Image.open(image_bytes)
    image = image.rotate(-90).convert('RGBA')
    image = crop_center(image, 1440, image.height)
    # image = bordercrop.crop(image)

    # Process the image as needed
    # ...

    # Return a response, if necessary
    return {"status": "success", "image": image}

@app.post("/predict", response_model=Prediction)
async def predict(data: dict):
    # image_bytes = base64.b64decode(data['cameraImage'])
    # Convert bytes to numpy array
    # np_array = np.frombuffer(image_bytes, dtype=np.uint8)

    # Read the image using OpenCV
    # image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    # image_raw = imutils.resize(image, width=1440, height=1440)
    image = data['cameraImage']

    image = process_image(image)['image']
    # we want to convert the image to RGBA format
    image = image.convert('RGB')

    image = image.resize((224, 224))
    # ouput the image with matplotlib
    # import matplotlib.pyplot as plt
    # plt.imshow(image)
    # plt.show()

    # Process the image
    # image = Image.open(io.BytesIO(await file.read()))

    # Make the prediction using the imported function
    prediction_label = make_prediction(model, image, "./classification/food-101/classes.txt")

    volume = VolumeEstimation(data)

    mass = volume * densities[prediction_label]
    mass = round(mass, 3)
    pred_label = prediction_label.replace("_", " ")
    query = "How many calories are in " + pred_label + " " + str(mass) + " kilograms"
    print(query)

    # Return the prediction
    return JSONResponse(content={"label": prediction_label, "volume": volume, "mass": mass, "calories": wolframAPI(query)})