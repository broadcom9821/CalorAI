import os
import torch
import torch.nn as nn
from torchvision import models
from sklearn.utils import shuffle
from torchvision import datasets, transforms
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from tqdm import tqdm
import matplotlib.pyplot as plt
from collections import OrderedDict
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)
model = models.densenet201()
classifier = nn.Sequential(
    nn.Linear(1920,1024),
    nn.LeakyReLU(),
    nn.Linear(1024,101),
)

classes = open("./food-101/classes.txt", 'r').read().splitlines()

class Label_encoder:
    def __init__(self, labels):
        labels = list(set(labels))
        self.labels = {label: idx for idx, label in enumerate(classes)}

    def get_label(self, idx):
        return list(self.labels.keys())[idx]

    def get_idx(self, label):
        return self.labels[label]

encoder = Label_encoder(classes)
for i in range(101):
    print(encoder.get_label(i), encoder.get_idx( encoder.get_label(i) ))

model.classifier = classifier

model.to(device)
model_path = './models/modelV2.pth'
if os.path.exists(model_path):

  # Load the model's state dictionary
  state_dict = torch.load(model_path, map_location=torch.device('cpu'))

  # Load the state dictionary into the model
  model.load_state_dict(state_dict)

  model.to(device)

  # Ensure the model is in evaluation mode (no training)
  model.eval()

  print("Model loaded")
else:
  print("model.pth does not exist in the current directory.")

# Preprocessing function for input images
def preprocess_image(image_path):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    image = Image.open(image_path).convert("RGB")
    image_before_preprocessing = image.copy()  # Save a copy for display
    image = transform(image)
    image = image.unsqueeze(0)  # Add batch dimension
    image = image.to(device)
    return image, image_before_preprocessing

# Prediction function
def predict_class(model, image_path, label_encoder):
    # Preprocess the input image
    input_image, image_before_preprocessing = preprocess_image(image_path)

    # Display the original image
    plt.imshow(image_before_preprocessing)
    plt.title('Original Image')
    plt.show()

    # Make the prediction
    with torch.no_grad():
        model.eval()  # Set the model to evaluation mode
        input_image = input_image.to(device)
        output = model(input_image)

    # Get the predicted class index
    _, predicted_idx = torch.max(output, 1)
    predicted_idx = predicted_idx.item()

    # Use the label encoder to get the predicted class label
    predicted_label = label_encoder.get_label(predicted_idx)

    return predicted_label

image_path = 'E:/Datasets/Food101/test/oml.jpg'
predicted_class = predict_class(model, image_path, encoder)
print(f'The predicted class is: {predicted_class}')