import os
import torch
import torch.nn as nn
from torchvision import models
from torchvision import transforms
from PIL import Image
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)

class Label_encoder:
    def __init__(self, labels):
        classes = labels
        labels = list(set(labels))
        self.labels = {label: idx for idx, label in enumerate(classes)}

    def get_label(self, idx):
        return list(self.labels.keys())[idx]

    def get_idx(self, label):
        return self.labels[label]

def load_model(model_path):
    model = models.densenet201()
    classifier = nn.Sequential(
        nn.Linear(1920,1024),
        nn.LeakyReLU(),
        nn.Linear(1024,101),
    )
    model.classifier = classifier

    model.to(device)
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
    return model
# Preprocessing function for input images
def preprocess_image_from_path(image_path):
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

def preprocess_image(image):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # image = Image.open(image_path).convert("RGB")
    
    image_before_preprocessing = image.copy()  # Save a copy for display
    image = transform(image)
    image = image.unsqueeze(0)  # Add batch dimension
    image = image.to(device)
    return image, image_before_preprocessing

# Prediction function
def predict_class_from_path(model, image_path, classes_path):
    classes = open(classes_path, 'r').read().splitlines()
    label_encoder = Label_encoder(classes)
    # Preprocess the input image
    input_image, image_before_preprocessing = preprocess_image(image_path)

    # Display the original image
    # plt.imshow(image_before_preprocessing)
    # plt.title('Original Image')
    # plt.show()

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

# Prediction function
def make_prediction(model, image, classes_path):
    classes = open(classes_path, 'r').read().splitlines()
    # Preprocess the input image
    label_encoder = Label_encoder(classes)
    input_image, image_before_preprocessing = preprocess_image(image)

    # Display the original image
    # plt.imshow(image_before_preprocessing)
    # plt.title('Original Image')
    # plt.show()

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

# model = load_model('./classification/models/modelV2.pth')
# image_path = 'E:/Datasets/Food101/test/pizza2.png'
# image = Image.open(image_path).convert("RGB")
# predicted_class = make_prediction(model, image, "./classification/food-101/classes.txt")
# print(f'The predicted class is: {predicted_class}')