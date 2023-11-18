import numpy as np 
import matplotlib.pyplot as plt
import cv2
from sklearn import preprocessing
import os.path
import tensorflow as tf

model = tf.keras.models.load_model('models/modelV1.h5')

image_dir = 'E:\Datasets\Food101\images\*'
food_dir = 'E:\Datasets\Food101'
SIZE = 224

train_labels = []
test_labels = []

with open(os.path.join(food_dir, 'meta/meta', 'labels.txt'), 'r') as f:
    for line in f:
        label = line
        train_labels.append(label)
        test_labels.append(label)
test_labels = np.array(test_labels)

encoder = preprocessing.LabelEncoder()
encoder.fit(test_labels)
test_labels_encoded = encoder.transform(test_labels)
encoder.fit(train_labels)
train_labels_encoded = encoder.transform(train_labels)

# Predict one image from a path
def predict_one_image(path):
    img = cv2.imread(path)
    img = cv2.resize(img, (SIZE, SIZE))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = np.array(img)
    img = img.astype('float32')
    img /= 255
    plt.imshow(img)
    input_img = np.expand_dims(img, axis=0)
    predictions = model.predict(input_img)
    # sort predictions from least to greatest
    sorted_index_array = np.argsort(predictions)
    # get the top 5 predictions
    top_5_predictions = sorted_index_array[0][-5:]
    # get the top 5 probabilities
    top_5_probabilities = predictions[0][top_5_predictions]
    # get the classes for each of the top 5 predictions
    top_5_classes = encoder.inverse_transform(top_5_predictions)
    prediction = np.argmax(predictions)  
    prediction = encoder.inverse_transform([prediction]) 
    print("The prediction for this image is:", prediction[0])
    return top_5_classes, top_5_probabilities

img = 'E:/Datasets/Food101/test/pizza3.jpeg'
print(predict_one_image(img))