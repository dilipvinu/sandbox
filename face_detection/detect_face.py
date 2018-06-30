import cv2
import sys
import os
import urllib.request
from urllib.error import URLError


def get_face_count(image_path, cascade_path):
    # Create the haar cascade
    face_cascade = cv2.CascadeClassifier(cascade_path)

    # Read the image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
        # flags = cv2.CV_HAAR_SCALE_IMAGE
    )

    if len(faces) > 0:
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow("Faces found", image)
        cv2.waitKey(0)

    return len(faces)


def detect_face(image_url):
    try:
        image_path, headers = urllib.request.urlretrieve(image_url)
        cascades = ["haarcascade_frontalface_default.xml",
                    "haarcascade_profileface.xml",
                    "haarcascade_upperbody.xml",
                    "haarcascade_fullbody.xml"]

        face_count = 0
        for cascade in cascades:
            print("Detecting with {0}".format(cascade))
            face_count = get_face_count(image_path, 'face_detection/haarcascades/' + cascade)
            if face_count > 0:
                break

        os.remove(image_path)
        print("Found {0} faces".format(face_count))

        return face_count > 0
    except URLError as e:
        print(e)
        return 0


# Get user supplied values
imageUrl = sys.argv[1]
if detect_face(imageUrl):
    print('\033[32m\033[1mFace found\033[0m')
else:
    print('\033[31m\033[1mNo face found\033[0m')
