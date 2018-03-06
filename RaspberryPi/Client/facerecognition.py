#!/usr/bin/env python

import cv2
import os
import numpy as np
import timeit

def detect_face(img):
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	face_cascade = cv2.CascadeClassifier('FaceDatabase/opencv-files/lbpcascade_frontalface.xml')
	faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5);

	if(len(faces) == 0):
		return None, None

	#print(len(faces))

	(x, y, w, h) = faces[0]
	return gray[y:y+w, x:x+h], faces[0]

def prepare_training_data(data_folder_path):
	dirs = os.listdir(data_folder_path)
	faces = []
	labels = []

	for dir_name in dirs:
		if not dir_name.startswith("s"):
			continue;
		label = int(dir_name.replace("s", ""))
		subject_dir_path = data_folder_path + "/" + dir_name
		subject_images_names = os.listdir(subject_dir_path)

		for image_name in subject_images_names:
			if image_name.startswith("."):
				continue;

			image_path = subject_dir_path + "/" + image_name
			image = cv2.imread(image_path)

			#cv2.imshow("Training on image...", image)
			#cv2.waitKey(100)

			try:
				face, rect = detect_face(image)

				if face is not None:
					faces.append(face)
					labels.append(label)
				else:
					print('Could not detect faces on %s, deleting picture.' % (image_path))
					os.remove(image_path)
			except Exception as e:
				print e

	#cv2.destroyAllWindows()
	#cv2.waitKey(1)
	#cv2.destroyAllWindows()

	return faces, labels

#face_recognizer = cv2.face.EigenFaceRecognizer_create() # Expects all input samples to be equal size
#face_recognizer = cv2.face.FisherFaceRecognizer_create() # Expects all input samples to be equal size
face_recognizer = cv2.face.LBPHFaceRecognizer_create()

def prepare_data():
	start_time = timeit.default_timer()
	print("Preparing data...")
	faces, labels = prepare_training_data("FaceDatabase/training-data")
	print("Data prepared")

	print("Total faces: ", len(faces))
	print("Total labels: ", len(labels))

	face_recognizer.train(faces, np.array(labels))
	elapsed = timeit.default_timer() - start_time
	print('Trained in %s seconds.' % (elapsed))
	print("")

def predict(test_img):
	nparr = np.fromstring(test_img, np.uint8)
	img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

	face, rect = detect_face(img_np)
	if (face is not None):
		label, confidence = face_recognizer.predict(face)
	else: 
		label, confidence = None, None
	return label, confidence

prepare_data();

'''
def draw_rectangle(img, rect):
	(x, y, w, h) = rect
	cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

def draw_text(img, text, x, y):
	cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)

subjects = ["", "Michael Tran", "Sue Park", "Bambi Tran", "Gloria Tran", "Dawn Tran"]

def predict2(test_img):
	img = test_img.copy()
	face, rect = detect_face(img)
	label, confidence = face_recognizer.predict(face)
	print('Label', label)
	print('Confidence', confidence)
	label_text = subjects[label]
	draw_rectangle(img, rect)
	draw_text(img, label_text, rect[0], rect[1]-5)
	return img

print("Predicting images...")

test_img1 = cv2.imread("FaceDatabase/training-data/s4/1.jpg")

predicted_img1 = predict2(test_img1)

print("Prediction complete")

cv2.imshow(subjects[1], predicted_img1)
cv2.waitKey(0)
cv2.destroyAllWindows()
'''