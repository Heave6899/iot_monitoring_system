from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import time
import subprocess
import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("iotscreenoff/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

#def publish(client, userdata, flags,rc):
#    client.publish("iotscreenoff/monitor","OFF")
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
client.loop_start()

camera = PiCamera()
camera.resolution = (300,300)
camera.framerate = 3
rawCapture = PiRGBArray(camera,size=(300,300))
time.sleep(0.1)
i=0
flag=0
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    #cv2.imshow("Image",image)
    faceCascade = cv2.CascadeClassifier('xml/haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(30, 30),flags=cv2.CASCADE_SCALE_IMAGE)
    # for (x, y, w, h) in faces:
    #     cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
    #print(len(faces))

    if len(faces)==0:
        i=i+1
        print(i)
        if i==30:
            #subprocess.call(["xset", "-display",":0","dpms","force","off"])
            flag=1  
            client.publish("iotscreenoff/monitor","OFF")

    else:
        i=0
        print("Restart")
        if flag==1:
            #subprocess.call(["xset", "-display",":0","dpms","force","on"])
            flag=0
            client.publish("iotscreenoff/monitor","ON")


    #cv2.imshow("Image",image)
    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)
    if key == ord("q"):
        client.loop_stop()
        break
    #client.loop()