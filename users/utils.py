from PIL import Image as PilImage
import numpy as np


def image_to_numpy(image):
    img = PilImage.open(image)
    # Convert the PIL image to a NumPy array
    np_image = np.array(img)
    return np_image