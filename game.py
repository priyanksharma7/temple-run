# Author: Priyank Sharma
# Control up, down, left and right movements with facial positions using
# Haar Cascade classifier for face detection and OpenCV KCF tracker

# Import necessary packages
import time
import cv2
import imutils
from imutils.video import VideoStream, FPS
import pyautogui

# Load the haar cascade face detector
print("[INFO] Loading face detector...")
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# Set the tracker to None
tracker = None

# Start the video stream through the webcam
print("[INFO] Starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(1.0)

# Scale factor to resize the frame for faster processing
scale = 2

# Height and Width from the webcam
H = 480 // scale
W = 640 // scale

# Define the boundaries
up = 160 // scale
down = 320 // scale
left = 200 // scale
right = 440 //scale

# By default each key press is followed by a 0.1 second pause
pyautogui.PAUSE = 0.0

# wait sometime until next movement is registered
wait_time = 0.01
start = end = 0

# total number of frames processed thus far and skip frames
totalFrames = 0
skip_frames = 50

# start the FPS estimator
fps = FPS().start()

# loop indefinitely
while True:
	# grab the video frame, laterally flip it and resize it
	frame = vs.read()
	frame = cv2.flip(frame, 1)
	frame = imutils.resize(frame, width=W)

	# initialize the action
	action = None

	# Run the face detector to find or update face position
	if tracker is None or totalFrames % skip_frames == 0:
		print("Detecting")
		# convert the frame to grayscale (haar cascades work with grayscale)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		# Detect all faces
		faces = detector.detectMultiScale(gray, scaleFactor=1.05,
			minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
			
		# Check to see if a face was found
		if len(faces) > 0:

			# Pick the most prominent face
			initBB = faces[0]
			
			# start the tracker
			# print("Found face. Starting the tracker")
			tracker = cv2.legacy_TrackerKCF.create()
			tracker.init(frame, tuple(initBB))
		else:
			print("Face not found")
			tracker = None

	# otherwise the tracker is tracking the face, update the position
	else:
		# grab the new bounding box coordinates of the face
		(success, box) = tracker.update(frame)

		# if tracking was successful, draw the center point
		if success:
			# print("Tracking")
			(x, y, w, h) = [int(v) for v in box]

			# calculate the center of the face
			centerX = int(x + (w / 2.0))
			centerY = int(y + (h / 2.0))

			# draw a bounding box and the center
			cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
			cv2.circle(frame, (centerX, centerY), 5, (0, 255, 0), -1)

			# determine the action
			if centerY < up:
				action = "up"
			elif centerY > down:
				action = "down"
			elif centerX < left:
				action = "left"
			elif centerX > right:
				action = "right"

		else:
			tracker = None

	end = time.time()
	# press the key
	if action is not None and end - start > wait_time:
		print(action)
		pyautogui.press(action)
		start = time.time()

	# draw the lines
	cv2.line(frame, (0, up), (W, up), (255, 255, 255), 2) #UP
	cv2.line(frame, (0, down), (W, down), (255, 255, 255), 2) #DOWN
	cv2.line(frame, (left, up), (left, down), (255, 255, 255), 2) #LEFT
	cv2.line(frame, (right, up), (right, down), (255, 255, 255), 2) #RIGHT

	# increment the totalFrames and update the FPS counter
	totalFrames += 1
	fps.update()
	fps.stop()

	# information to be displayed
	info = [
		("FPS", "{:.2f}".format(fps.fps())),
		("Time", "{:.2f}".format(fps.elapsed())),
		("Action", action)
	]

	# Draw the information on the frame
	for (i, (k, v)) in enumerate(info):
		text = "{}: {}".format(k, v)
		cv2.putText(frame, text, (10, (i * 20) + 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

	# display the output
	cv2.imshow("Game Controls", frame)
	key = cv2.waitKey(1) & 0xFF

	# press 'q' key to break from the loop
	if key == ord("q"):
		break

vs.stop()
cv2.destroyAllWindows()