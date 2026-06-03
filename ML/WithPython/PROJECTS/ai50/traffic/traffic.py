import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    all_loaded_images = []
    all_image_category_labels = []
    
    # gonna loop thru 0 to 42 for the different sign categories
    for folder_number in range(NUM_CATEGORIES):
        
        # safely build the path to the folder using os.path so it works on mac and windows
        current_category_folder_path = os.path.join(data_dir, str(folder_number))
        
        # make sure it actually exists before we try to open it
        if os.path.exists(current_category_folder_path):
            
            for specific_image_file in os.listdir(current_category_folder_path):
                full_path_to_image = os.path.join(current_category_folder_path, specific_image_file)
                
                raw_image_data = cv2.imread(full_path_to_image)
                
                if raw_image_data is not None:
                    # resize it so the neural network doesnt freak out over different sizes
                    standardized_image_matrix = cv2.resize(raw_image_data, (IMG_WIDTH, IMG_HEIGHT))
                    
                    # save with category number
                    all_loaded_images.append(standardized_image_matrix)
                    all_image_category_labels.append(folder_number)
                    
    return (all_loaded_images, all_image_category_labels)


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    # stack up the layers for the neural net
    convolutional_neural_network = tf.keras.models.Sequential([
        
        # 1f irst pass: look for basic shapes and lines using a 3x3 filter
        tf.keras.layers.Conv2D(
            32, (3, 3), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
        ),
        
        # shrink it down to focus on the important bits
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
        
        # 2 second pass: get a little more complex with 64 filters
        tf.keras.layers.Conv2D(
            64, (3, 3), activation="relu"
        ),
        
        # shrink it again
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
        
        # flatten the grid into a single long line of data for the hidden layers
        tf.keras.layers.Flatten(),
        
        # dense hidden layer where the actual thinking happens
        tf.keras.layers.Dense(128, activation="relu"),
        
        # droppout is  basically randomly ignoring some neurons so it doesn't just memorize the data
        tf.keras.layers.Dropout(0.5),
        
        # needs exactly 43 nodes for the 43 signs
        tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax")
    ])
    
    convolutional_neural_network.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    
    return convolutional_neural_network


if __name__ == "__main__":
    main()
