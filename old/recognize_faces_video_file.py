# USAGE
# python recognize_faces_video_file.py --encodings encodings.pickle --input videos/lunch_scene.mp4
# python3 recognize_faces_video_file.py --encodings encoding/encodings.pickle --input /media/ubuntu/USBEE1-11/sample1.mp4 --output output/output4.mp4 --display 1

# import the necessary packages
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2

framecount = 0
framecountlimit = 10000
start = time.time()


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-e", "--encodings", required=True,
                help="path to serialized db of facial encodings")
ap.add_argument("-i", "--input", required=True,
                help="path to input video")
ap.add_argument("-o", "--output", type=str,
                help="path to output video")
ap.add_argument("-y", "--display", type=int, default=1,
                help="whether or not to display output frame to screen")
ap.add_argument("-d", "--detection-method", type=str, default="cnn",
                help="face detection model to use: either `hog` or `cnn`")
args = vars(ap.parse_args())

# load the known faces and embeddings
print("[INFO] loading encodings...")
data = pickle.loads(open(args["encodings"], "rb").read())

namedict = {"Unknown": 0}

for i in range(len(data["names"])):
	temp={data["names"][i]:0}
	namedict.update(temp)

# initialize the pointer to the video file and the video writer
print("[INFO] processing video...")
stream = cv2.VideoCapture(args["input"])
writer = None

framecount = 0
framecountlimit = 10000000000
frameinit = 30
frametime = frameinit + 10
framecounter = 0
repeater = 1

namedict = {"Unknown": 0}
presencedict = {}

counter=0

confirmedstring = "No data "


for i in range(len(data["names"])):
	temp={data["names"][i]:0}
	namedict.update(temp)
	
confirmeddict=namedict

start = time.time()
# loop over frames from the video file stream
while framecount<framecountlimit:
	# grab the frame from the threaded video stream
    (grabbed, frame) = stream.read()
	
	# convert the input frame from BGR to RGB then resize it to have
	# a width of 750px (to speedup processing)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb = imutils.resize(frame,width=400)
    r = frame.shape[1] / float(rgb.shape[1])
    # detect the (x, y)-coordinates of the bounding boxes
    # corresponding to each face in the input frame, then compute
    # the facial embeddings for each face
    boxes = face_recognition.face_locations(rgb,model=args["detection_method"])
    encodings = face_recognition.face_encodings(rgb, boxes)
    names = []
    # loop over the facial embeddings
    data2 = data
    for encoding in encodings:
		# attempt to match each face in the input image to our known
		# encodings
        matches = face_recognition.compare_faces(data2["encodings"],encoding)
        name = "Unknown"
		# check to see if we have found a match
        if True in matches:
			# find the indexes of all matched faces then initialize a
			# dictionary to count the total number of times each face
			# was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}
            nameindex = {}
			# loop over the matched indexes and maintain a count for
			# each recognized face face
            for i in matchedIdxs:
                name = data["names"][i]
                nameindex[name] = i
                counts[name] = counts.get(name, 0) + 1

			# determine the recognized face with the largest number
			# of votes (note: in the event of an unlikely tie Python
			# will select first entry in the dictionary)
            name = max(counts, key=counts.get)
		
		# update the list of names
        names.append(name)

	# loop over the recognized faces
    for ((top, right, bottom, left), name) in zip(boxes, names):
		# rescale the face coordinates
        top = int(top * r)
        right = int(right * r)
        bottom = int(bottom * r)
        left = int(left * r)
		# draw the predicted face name on the image
        cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 0), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)
    for i in range(len(names)):
        val2 = str(names[i])
        val = int(namedict.get(val2))
        calculate = val + 1
        namedict[names[i]] = calculate
    
    namestring = "In picture :  "
    
    for i in names:
       namestring = namestring + i + ","
    
    cv2.putText(frame,namestring,(0,15), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,255,0),2)
    framecount=framecount+1
    framecounter = framecounter + 1
	
    if framecounter == frametime :
       confirmedstring = "Confirmed presence within " + str(frametime) +"/"+ str(repeater) +" frames : "
       for k,v in namedict.items():
          if v >= frameinit :
              confirmedstring += str(k)
              confirmedstring += ", "
              confirmeddict[k]+=1
          namedict[k] = 0
       framecounter = 0
       repeater = repeater + 1
		
    cv2.putText(frame,confirmedstring,(0,40), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)


    # if the video writer is None *AND* we are supposed to write
    # the output video to disk initialize the writer
    if writer is None and args["output"] is not None:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(args["output"], fourcc, 24,
                                 (frame.shape[1], frame.shape[0]), True)

    # if the writer is not None, write the frame with recognized
    # faces t odisk
    if writer is not None:
        writer.write(frame)

    # check to see if we are supposed to display the output frame to
    # the screen
    if args["display"] > 0:
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
            
    for i in range(len(names)):
	    val2 = str(names[i])
	    val = int(namedict.get(val2))
	    calculate = val + 1
	    namedict[names[i]] = calculate

# close the video file pointers
stream.release()

end = time.time()
totaltime = end - start
fps = framecount/totaltime

# check to see if the video writer point needs to be released
if writer is not None:
    writer.release()

print(framecount)
print(fps)
print(totaltime)

for k,v in namedict.items():
	print(k," = ",v)
