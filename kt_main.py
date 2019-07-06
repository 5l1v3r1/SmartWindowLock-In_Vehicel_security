import cv2
import serial
import numpy as np
import time
from time import sleep
import pyttsx as p
from tkinter import *
import tkinter
import PIL.Image, PIL.ImageTk
import serial.tools.list_ports as ports
from imutils.video import FPS

class Gui():

    def __init__(self,window,window_title,video_source=1):

        self.control_system=control_system(115200)
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.confidence=0.2
        self.fps = FPS().start()
        self.override_flag=False
        self.CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
        self.ELEM_CLASSES = ["background","bicycle", "bird", "bus", "car", "cat", "cow",
	"dog", "horse", "motorbike", "person", "sheep"]
        
        self.COLORS = np.random.uniform(0, 255, size=(len(self.CLASSES), 3))


        self.main_run()

    def main_run(self):

        print("[INFO] loading model...")
        self.net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt.txt","MobileNetSSD_deploy.caffemodel")

        # initialize the video stream, allow the cammera sensor to warmup,
        # and initialize the FPS counter
        print("[INFO] starting video stream...")

        self.vid = cv2.VideoCapture(self.video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", self.video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        #print("width",self.width)
        #print("height",self.height)


        self.b1_x1=int(round(self.width/2))-125
        self.b1_y1=0
        self.b1_x2=int(round(self.width/2))-125
        self.b1_y2=int(self.height)
        
        self.b2_x1=int(round(self.width/2))+125
        self.b2_y1=0
        self.b2_x2=int(round(self.width/2))+125
        self.b2_y2=int(self.height)
        
        self.canvas = tkinter.Canvas(self.window, width = self.width, height = self.height)
        self.canvas.pack()

        self.override_btn=tkinter.Button(self.window,text="manual override",width=30,command=self.kill_process)
        self.override_btn.pack(side=tkinter.RIGHT)
        self.override_btn=tkinter.Button(self.window,text="Stop",width=30,command=self.stop)
        self.override_btn.pack(side=tkinter.RIGHT)
        self.engage_btn=tkinter.Button(self.window,text="Engage",width=30,command=self.ck_ovrd)
        self.engage_btn.pack(side=tkinter.LEFT)
        self.disengage_btn=tkinter.Button(self.window,text="Dis-Engage",width=30,command=self.ck_d_ovrd)
        self.disengage_btn.pack(side=tkinter.LEFT)
        self.delay = 15
        self.update()
        self.fps.update()
        self.window.mainloop()

    def get_frame(self):
        if self.vid.isOpened():
            self.ret, frame = self.vid.read()
            if self.ret:
                frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                cv2.putText(frame,"Kribo Tech",(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),2)
                cv2.putText(frame,time.strftime("%d-%m-%Y-%H-%M-%S"),(10,50),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),2)
                #print("ck",self.override_flag)
                # Return a boolean success flag and the current frame converted to BGR
                if self.override_flag==True:
                    return (self.ret, self.sys_event(frame))
                else:
                    return (self.ret,frame)
            else:
                return (self.ret, None)
        else:
            return (self.ret, None)

    def ck_ovrd(self):
        self.override_flag=True
        
    def ck_d_ovrd(self):
        self.override_flag=False

    def respond(self,pos,i_object):
        message="The object detected by system is"+i_object+"to the"+pos+"of your vehicle"            
        self.control_system.speak_me(message)
        
    
    def sys_event(self,frame):
        
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),0.007843, (300, 300), 127.5)
        self.net.setInput(blob)
        detections = self.net.forward()
        cv2.line(frame,(self.b1_x1,self.b1_y1),(self.b1_x2,self.b1_y2),(0,0,255),2)
        cv2.line(frame,(self.b1_x1,30),(50,self.b1_y1+30),(0,255,255),2)
        cv2.line(frame,(self.b1_x1,int(round(self.height/2))),(50,int(round(self.height/2))),(0,255,255),2)
        cv2.line(frame,(self.b1_x1,int(round(self.height))-50),(50,int(round(self.height))-50),(0,255,255),2)
        cv2.line(frame,(self.b2_x1,self.b2_y1),(self.b2_x2,self.b2_y2),(0,0,255),2)
        cv2.line(frame,(self.b2_x1,30),(self.b2_x1+125,self.b2_y1+30),(0,255,255),2)
        cv2.line(frame,(self.b2_x1,int(round(self.height/2))),(self.b2_x1+125,int(round(self.height/2))),(0,255,255),2)
        cv2.line(frame,(self.b2_x1,int(round(self.height))-50),(self.b2_x1+125,int(round(self.height))-50),(0,255,255),2)

        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > self.confidence:
                idx = int(detections[0, 0, i, 1])
                #print("i",idx)
                #cv2.putText(frame,self.fps,(10,10),cv2.FONT_HERSHEY_SIMPLEX,0.5,self.COLORS[idx],2)
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                if self.CLASSES[idx] not in self.ELEM_CLASSES:
                    continue
                """ uncomment all the self.respond classes for the voice id """
                if (startX < self.b1_x1 and  endX <self.b1_x2) :
                    print("left")
                    self.control_system.left_plane()
                    #self.respond("left",self.CLASSES[idx])
                if (startX > self.b1_x1 and  endX > self.b1_x2) and (startX < self.b2_x1 and  endX < self.b2_x2):
                    print("center")
                    self.control_system.center_plane()
                    #self.respond("center",self.CLASSES[idx])    
                if (startX > self.b2_x1 and  endX > self.b2_x2) :
                    print("right")
                    self.control_system.right_plane()
                    #self.respond("right",self.CLASSES[idx])
                    
                
                
                #if self.CLASSES[idx] == "person":
                #    continue
                label = "{}: {:.2f}%".format(self.CLASSES[idx],confidence * 100)
                cv2.rectangle(frame, (startX, startY), (endX, endY),self.COLORS[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(frame, label, (startX, y),cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLORS[idx], 2)
        
        return frame
               
    """def tst(self,frame):
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),0.007843, (300, 300), 127.5)
        self.net.setInput(blob)
        detections = self.net.forward()

        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            
            confidence = detections[0, 0, i, 2]
            if confidence > self.confidence:
                idx = int(detections[0, 0, i, 1])
                print("i",idx)
                #cv2.putText(frame,self.fps,(10,10),cv2.FONT_HERSHEY_SIMPLEX,0.5,self.COLORS[idx],2)
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                if self.CLASSES[idx] == "person":
                    continue
                label = "{}: {:.2f}%".format(self.CLASSES[idx],confidence * 100)
                cv2.rectangle(frame, (startX, startY), (endX, endY),self.COLORS[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(frame, label, (startX, y),cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLORS[idx], 2)
        cv2.putText(frame,"kt",(10,10),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0,2))
        return frame"""

                        
    def update(self):
        # Get a frame from the video source
        ret, frame = self.get_frame()

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
            

        self.window.after(self.delay, self.update)

    def kill_process(self):
        self.override_flag=False
        self.window.destroy()
        if self.vid.isOpened():
            cv2.destroyAllWindows()
            if self.vid.isOpened():
                self.vid.release()
            self.fps.stop()
            print("[INFO] elapsed time: {:.2f}".format(self.fps.elapsed()))
            print("[INFO] approx. FPS: {:.2f}".format(self.fps.fps()))
            print("quit")
        exit()   

    def stop(self):
        sleep(1)
        self.kill_process()

    def __del__(self):
        self.override_flag=False
        if self.vid.isOpened():
            cv2.destroyAllWindows()
            if self.vid.isOpened():
                self.vid.release()
            self.fps.stop()
            print("[INFO] elapsed time: {:.2f}".format(self.fps.elapsed()))
            print("[INFO] approx. FPS: {:.2f}".format(self.fps.fps()))
            print("quit")
        exit()   



class control_system:

    def __init__(self,com_port):
        print("Initialising all Hardware accesories")
        self.message1="Object approaching near the vehicle"
        self.message2="Object approaching to the left of the vehicle"
        self.message3="Object approaching to the right of the vehicle"
        self.com_port=com_port
        self.ports=list(ports.comports())
        self.addr_list=[]
        for i in self.ports:
            a=str(i)
            #print(a)
            #a=a[:12] # for linux systems
            a=a[:4]  # for windows systems
            #print(type(i))
            self.addr_list.append(a)
        #print("addr:",self.addr_list)
        l=len(self.addr_list)
        if l==1:
            pos=0
        else:
            pos=1
        self.ser_connect=serial.Serial(self.addr_list[pos],self.com_port)

        if self.ser_connect.isOpen():
            print("serial connection establsied @ %d port",self.com_port)

    def center_plane(self):

        """ uncomment all the self.speak_me classes for the voice id """
        
        self.ser_connect.write("a".encode('utf-8'))
        #self.speak_me(self.message1)

    def right_plane(self):
        self.ser_connect.write("r".encode('utf-8'))
        #self.speak_me(self.message3)

    def left_plane(self):
        self.ser_connect.write("l".encode('utf-8'))
        #self.speak_me(self.message2)

    def speak_me(self,inp):
        # replay to the word you want
        speak=p.init()
        speak.say(inp)
        rate = speak.getProperty('rate')
        speak.setProperty('rate', rate-1000)
        #if init_speak.isBusy() == False:
        speak.runAndWait()
        speak.stop()


    def __del__(self):
        self.ser_connect.close()


class main_ctrl(Gui,control_system):

    def __init__(self):

        print("Press 's'  key on the keybaord to start the proess")
        inp=input('')
        if inp=='s':
            Gui(tkinter.Tk(), "kt_window")






if __name__=="__main__":
    main_ctrl()


#m=speak_me("Person in fornt off drive careful ")
