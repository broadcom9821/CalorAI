from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import sys
sys.path.append('../classification/')  # Replace with the actual path to the directory
from foodClassify import make_prediction, load_model  # Import make_prediction from prediction_module
from torchvision import transforms
from PIL import Image
import io

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

class Prediction(BaseModel):
    label: str

@app.post("/predict", response_model=Prediction)
async def predict(file: UploadFile = File(...)):
    # Process the image
    image = Image.open(io.BytesIO(await file.read()))

    model = load_model('../classification/models/modelV2.pth')
    # Make the prediction using the imported function
    prediction_label = make_prediction(model, image, "../classification/food-101/classes.txt")

    # Return the prediction
    return JSONResponse(content={"label": prediction_label})