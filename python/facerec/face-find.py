import sys
import dlib
import cv2
import face_recognition
import os
import postgresql

if len(sys.argv) < 2:
    print("Usage: face-find <image>")
    exit(1)

if not os.path.exists("./.faces"):
    os.mkdir("./.faces")

db = postgresql.open('pq://user:pass@localhost:5434/db')

# Create a HOG face detector using the built-in dlib class
face_detector = dlib.get_frontal_face_detector()

def facerec(file_name):
	# Load the image
	image = cv2.imread(file_name)

	# Run the HOG face detector on the image data
	detected_faces = face_detector(image, 1)

	print("Found {} faces in the image file {}".format(len(detected_faces), file_name))

	# Loop through each face we found in the image
	for i, face_rect in enumerate(detected_faces):
	    # Detected faces are returned as an object with the coordinates
	    # of the top, left, right and bottom edges
	    print("- Face #{} found at Left: {} Top: {} Right: {} Bottom: {}".format(i, face_rect.left(), face_rect.top(),
	                                                                             face_rect.right(), face_rect.bottom()))
	    crop = image[face_rect.top():face_rect.bottom(), face_rect.left():face_rect.right()]

	    encodings = face_recognition.face_encodings(crop)
	    if len(encodings) > 0:
	        query = "SELECT file FROM vectors ORDER BY " + \
	                "(CUBE(array[{}]) <-> vec_low) + (CUBE(array[{}]) <-> vec_high) ASC LIMIT 1".format(
	            ','.join(str(s) for s in encodings[0][0:63]),
	            ','.join(str(s) for s in encodings[0][64:127]),
	        )
	        print(db.query(query))
	    else:
	        print("No encodings")

# Take the image file name from the command line
file_name = sys.argv[1]
facerec(file_name)