# Flask application to capture live webcam stream and send the frames
# to the web page that is displaying the game

# Import necessary packages
from flask import Flask, render_template, Response
import time
import cv2
import imutils
from imutils.video import VideoStream
import pyautogui

app = Flask(__name__)

# generate frames and yield to Response
def gen_frames():

	# Load the haar cascade face detector
	detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

	# Set the tracker to None
	tracker = None

	# Start the video stream through the webcam
	vs = VideoStream(src=0).start()

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
				tracker = cv2.legacy_TrackerKCF.create()
				tracker.init(frame, tuple(initBB))
			else:
				tracker = None

		# otherwise the tracker is tracking the face, update the position
		else:
			# grab the new bounding box coordinates of the face
			(success, box) = tracker.update(frame)

			# if tracking was successful, draw the center point
			if success:
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
			# print(action)
			pyautogui.press(action)
			start = time.time()

		# draw the lines
		cv2.line(frame, (0, up), (W, up), (255, 255, 255), 2) #UP
		cv2.line(frame, (0, down), (W, down), (255, 255, 255), 2) #DOWN
		cv2.line(frame, (left, up), (left, down), (255, 255, 255), 2) #LEFT
		cv2.line(frame, (right, up), (right, down), (255, 255, 255), 2) #RIGHT

		# increment the totalFrames and draw the action on the frame
		totalFrames += 1
		text = "{}: {}".format("Action", action)
		cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

		# Generate a stream of frame bytes
		ret, buffer = cv2.imencode('.jpg', frame)
		frame = buffer.tobytes()
		yield (b'--frame\r\n'
			b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Video streaming route
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)