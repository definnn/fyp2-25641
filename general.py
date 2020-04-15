import boto3
from botocore.exceptions import ClientError
from profile import profiledict
import checkconnection as ch
from boto3.dynamodb.conditions import Key, Attr
import mysql.connector

import pickle
import os
from imutils.video import VideoStream
import face_recognition
import argparse
import imutils
import pickle
import cv2
import copy

from datetime import datetime
from datetime import timedelta
import time
from time import sleep 

from face_recogold import recognize_faces
from face_recog_warm import recognize_faces_warmup
import uuid



xss= open("guru99.txt","w+")
xss.close()
#INIT INFO

device_id = profiledict["device_id"]
print("\n-------------------------\n FRAT node : ",device_id,"\n-------------------------\n")
dynamodb = boto3.resource('dynamodb')
bucket = "fyp-25641"
s3 = boto3.client('s3')
warmup_min = 1
warmup_value = warmup_min * 60
duration = 10
duration_value = duration * 60
attendance_percentage_threshold = 50
sleep_sec=60


mydb = mysql.connector.connect(
  host="fras-1.cqsokkynctpe.ap-southeast-1.rds.amazonaws.com",
  user="admin",
  passwd="suzuki23",
  database="frat"
)
mycursor = mydb.cursor()


while 1>0 :
    #MAKE CONNECTION
    connection = ch.initconnection(device_id)

    #RUN JOBS IF CONNECTION SUCCESS
    
    start_cycle = False
    
    if connection is True :

	
	    #Check frat_scheduler for jobs
        strdevice_id = str(device_id)
        print("Checking Job for node")
        mycursor.execute("SELECT * FROM fras_scheduler WHERE device_id = '"+strdevice_id+"' AND job_status = 'active'")
        testtemp = mycursor.fetchone()
            
        #run cycle
        
        
        if testtemp :
            print("Found Job!")
            print(str(testtemp[2]))
            s3 = boto3.client('s3')
            encodingkey = str(testtemp[2]) + ".pickle"
            
            try:
                s3.download_file(bucket, encodingkey, encodingkey)
                print("Success download class encoding")
                class_id = testtemp[2]
                class_duration = testtemp[4]
                class_start = str(testtemp[3])
                mycursor.execute("SELECT * FROM class_info WHERE class_id = '"+class_id+"' LIMIT 1")
                testtemp2 = mycursor.fetchone()
                class_location = testtemp2[9]
                class_time_start = datetime.strptime(class_start, '%Y-%m-%d %H:%M:%S')
                class_time_end = class_time_start + timedelta(minutes=int(class_duration))
                class_buffer = class_time_start - timedelta(minutes=warmup_min)

                start_cycle = True
            except ClientError as e:
                print("Failed to download encoding")
                print(e.response['Error']['Message'])

                start_cycle = False
        else:
            print("No scheduled Jobs or Error, sleeping for ",sleep_sec," seconds")
                
        if start_cycle is True :
            print("Starting Job for class : ",str(testtemp[2]))
            print("Waiting until class start")
            while class_buffer > datetime.now():
                sleep(10)
            

            print("Scoring attendance for : ",class_duration," minutes")
            confirmeddict,repeater = recognize_faces(encodingkey,0,1,int(class_duration))	
	
            for k,v in confirmeddict.items():
	            
	            if k != "Unknown":
	            
	                table = dynamodb.Table('attendance_log')
	                attendance_id = str(uuid.uuid4())
	                calculate =  (v/repeater)*100
	                
	                if calculate >= attendance_percentage_threshold :
	                    attendance_status = "present"
	                else:
	                    attendance_status = "absent"
	                    
	                class_datetime = str(class_start)
	                
	                user_id = str(k)
	                mycursor.execute("INSERT INTO attendance_log (user_id,class_id,class_location,class_datetime,attendance_status) VALUES ('"+user_id+"','"+class_id+"','"+class_location+"','"+class_datetime+"','"+attendance_status+"')")
	                mydb.commit()
	                print("Success update attendace for : ",user_id,"/",attendance_status)

            #cleanup
            os.remove(encodingkey)
	
	    #close connection
        connection = ch.closeconnection(device_id)
        
        

    sleep(sleep_sec)



