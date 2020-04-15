import boto3
from botocore.exceptions import ClientError
from profile import profiledict
import mysql.connector

###INITIALIZE DEVICE INFO TO AWS




 
mydb = mysql.connector.connect(
  host="fras-1.cqsokkynctpe.ap-southeast-1.rds.amazonaws.com",
  user="admin",
  passwd="suzuki23",
  database="frat"
)
mycursor = mydb.cursor()



def initconnection(device_id):
    try:
        sql = "UPDATE devices SET device_status = 'active' WHERE device_id = '"+str(device_id)+"'"
        mycursor.execute(sql)
        mydb.commit()
        print("Connection successful")
        return True

    except TypeError as e:
        print(e)
        return False
        
def closeconnection(device_id):
    
    try:
        sql = "UPDATE devices SET device_status = 'not active' WHERE device_id = '"+str(device_id)+"'"
        mycursor.execute(sql)
        mydb.commit()
        print("Connection closed")
        return True

    except TypeError as e:
        print(e)
        return False
        

