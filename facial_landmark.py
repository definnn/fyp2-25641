# Import necessary stuff
# PIL IS Python Image Library
from PIL import Image, ImageDraw
import face_recognition

# Loading Image (Make sure your code and image are in same folder else you have to specify the whole path of image)
image = face_recognition.load_image_file("/media/ubuntu/USBEE1-11/dissertation images/passportpic.png")

# The below code identifies all the faces in a picture and length of the list gives the number of faces(In this case it is one)
face_landmarks_list = face_recognition.face_landmarks(image)
print(face_landmarks_list)
print("I found {} face(s) in this photograph.".format(len(face_landmarks_list)))

# To draw on the image
pil_image = Image.fromarray(image)
d = ImageDraw.Draw(pil_image)

# Iterating through all faces in face_landmarks_list(In this case, only one face)
for face_landmarks in face_landmarks_list:
     
     # loop1
     for facial_feature in face_landmarks.keys():
         print("The {} in this face has the following points: {}".format(facial_feature, face_landmarks[facial_feature]))
     
     # loop2
     for facial_feature in face_landmarks.keys():
         d.line(face_landmarks[facial_feature],width=5)
pil_image.show()




