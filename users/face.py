import face_recognition as fr
import numpy as np
from .models import User, Image


def is_ajax(request):
  return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def get_encoded_faces():
    """
    This function loads all user profile images and encodes their faces
    """
    # Retrieve all users from the database
    users = User.query.all()

    # Create a dictionary to hold the encoded face for each user
    encoded = {}

    for user in users:
        # Initialize the encoding variable with None
        encoding = None

        # Load the user's images and encode their faces
        user_images = [fr.load_image_file(image.filename) for image in user.images]

        # Encode faces (if detected) from all user's images
        for image in user_images:
            face_encodings = fr.face_encodings(image)
            if len(face_encodings) > 0:
                encoding = face_encodings[0]  # Assuming only one face per image
                break  # Stop processing further images once a face is detected

        # Add the user's encoded face to the dictionary if encoding is not None
        if encoding is not None:
            encoded[user.id] = encoding
        else:
            print(f"No face found for user with ID: {user.user_id}")

    # Return the dictionary of encoded faces
    return encoded


def classify_face(img):
    """
    This function takes an image as input and returns the user model of the owner of the classified faces
    """
    # Load all the known faces and their encodings
    faces = get_encoded_faces()  # Assuming get_encoded_faces() retrieves the faces from your database
    faces_encoded = list(faces.values())
    known_face_ids = list(faces.keys())


    # Load the input image
    img = fr.load_image_file(img)
 
    try:
        # Find the locations of all faces in the input image
        face_locations = fr.face_locations(img)

        # Encode the faces in the input image
        unknown_face_encodings = fr.face_encodings(img, face_locations)


        # Identify the faces in the input image
        recognized_users = []
        for face_encoding in unknown_face_encodings:
            # Compare the encoding of the current face to the encodings of all known faces
            matches = fr.compare_faces(faces_encoded, face_encoding)

            # Find the known face with the closest encoding to the current face
            face_distances = fr.face_distance(faces_encoded, face_encoding)
            best_match_index = np.argmin(face_distances)

            # If the closest known face is a match for the current face, get the user model associated with it
            if matches[best_match_index]:
                user_id = known_face_ids[best_match_index]
                user = User.query.filter_by(id=user_id).first()  # Assuming you can retrieve user information from the database using its ID
                # print(user)
                recognized_users.append(user)

        # print(f'It matches {matches}')
        # Return the list of recognized users
        return recognized_users
    except:
        # If no faces are found in the input image or an error occurs, return an empty list
        return []


def encode_and_compare_faces(input_face, user_faces, tolerance=0.7):
    """
    Encode the faces of the user in the database and compare them to the input face with a given tolerance.
    
    Parameters:
        - user_faces (list): List of face images belonging to the user in the database
        - input_face (numpy.ndarray): Face image submitted during login
        - tolerance (float): Tolerance threshold for face comparison
        
    Returns:
        - bool: True if the input face matches any of the user's faces within the given tolerance, False otherwise
    """
    # Encode the faces of the user in the database
    encoded_user_faces = [fr.face_encodings(face)[0] for face in user_faces]

    # Encode the input face
    input_face_encodings = fr.face_encodings(input_face)
    if not input_face_encodings:
        return False  # No face detected in the input image
    input_face_encoding = input_face_encodings[0]

    # Compare the input face encoding with the encoded faces of the user
    matches = fr.compare_faces(encoded_user_faces, input_face_encoding, tolerance=tolerance)

    # Return True if the input face matches any of the user's faces within the given tolerance, False otherwise
    return any(matches)


def face_check(image_np_array):
    """
    Check if there are faces in the given image numpy array.

    Parameters:
        image_np_array (numpy.ndarray): Image in the form of a numpy array.

    Returns:
        bool: True if faces are detected, False otherwise.
    """
    # Use face_recognition library to detect faces in the image
    face_locations = fr.face_locations(image_np_array)

    # Return True if faces are detected, False otherwise
    return bool(face_locations)
