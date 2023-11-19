from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sys
sys.path.append('../classification/')  # Replace with the actual path to the directory
from foodClassify import make_prediction, load_model  # Import make_prediction from prediction_module
from PIL import Image
import io

app = FastAPI()

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