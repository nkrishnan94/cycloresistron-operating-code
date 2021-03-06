import serial.tools.list_ports
import numpy as np
import time
from matplotlib import pyplot as plt
import threading 
import datetime
import subprocess 
import csv
import os
ports = serial.tools.list_ports.comports()

for port in ports:
    # print(str.split(str(port),' - '))
    if 'Arduino' in str(port):
        print(port)
        arduino_port  = str.split(str(port),' - ')[0]
# s
plt.ion() # set plot to animated
ser = serial.Serial(arduino_port, baudrate = 9600, timeout=1)


ODdata = []
pump_nut = []
pump_drug = [] 
pump_waste = []
timer = []
# colour_data = ['k'] * 1000
# ax1=plt.axes() 

arduinoData = 0
line = plt.plot(arduinoData)
num_cham = 16

#pumps
mediapump1 = 2
drugpump1 = 3
wastepump1 = 4

#pumpcalbration
mp1ontime= 5/3.25
dp1ontime= 5/3.35
wp1ontime= 5/4.45

OD_avg_length = 30
#control pump
def pump_ctrl(pnum, pstate):
    ser.flush() #flush before sending signal
    ser.write(('PUMP %d %d\n' % (pnum, pstate)).encode()) #send signal telling Arduino to turn off pump 

#measure OD from all arduion analog inputs
def measure(num_cham):
    #self.ser.flush() #flush before sending signal
    ser.flushInput()
    ser.flushOutput()
    ser.write(('MEASURE\n').encode()) #send signal telling Arduino to send data
    
    # now read all lines sent by the Arduino
    data = []
    #data = ser.readline().decode('ascii') 
    # read analog channels
    for i in range(0,num_cham): # now read the 8 analog channel
        #data.append( int(self.ser.readline()[0:-2]) ) #this line will crash when running "test" because it sends strings not ints
        
        #data = ser.readline().decode('ascii')
        data.append(ser.readline().decode('ascii')) 
    return data

    
def get_currtime():
    ## convenient function to get current time 
    return datetime.datetime.now().replace(microsecond=0)

start_time = get_currtime()  

#code to plot data
def plotdata(ydata):
    plt.axis([0, len(ydata), 0, 1000])
    plt.ion()
    
    plt.plot(np.arange(len(ydata)), ydata,color = 'r')
    #plt.setp(line, linewidth=2.0,color = 'r')

    plt.pause(.0000000001)


start_time = get_currtime()          
loop_count = 0
addmediafreq = 10
avgnum = 5
#morbidostat algorithm, set to trigger pumps and keep them on according to calibrated time

outdir = "data-%d%.2d%.2d-%.2d%.2d" % (start_time.year, start_time.month, start_time.day, start_time.hour, start_time.minute)
os.makedirs(outdir) 
filesize = 10
filenum = 0 
def savefunc(loop_count, ODdata, pump_nut, pump_drug, pump_waste, timing,outdir,filenum, filesize):
    if loop_count % filesize == 0:
        filenum +=1
     
    outfile = "%s/%s.%d.csv" % (outdir, outdir, filenum)
    l = [ODdata,pump_nut, pump_drug,pump_waste,timing]
    out = open(outfile, 'a')
    with out as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(l) 
    ODdata = []
    pump_nut = []
    pump_drug = []
    pump_waste = []
    timing = []
    return ODdata, pump_nut, pump_drug, pump_waste, timing, filenum


def cycloresistron(loop_count, addmediafreq, avgnum,dp1ontime,mp1ontime,wp1ontime, ODdata, pump_drug, pump_nut, pump_waste, avOD_buffer): 
    avOD_buffer = np.append(avOD_buffer, ODdata)  
    # then remove the first item in the array, i.e. the oldest 
    avOD_buffer = np.delete(avOD_buffer, 0, axis=0)          
    # calculate average for each flask
    avOD = np.mean(avOD_buffer, axis=0)
    if (loop_count % addmediafreq)==0 and loop_count>0:
        if avOD >400:
            pump_ctrl(drugpump1,1)
            threading.Timer(dp1ontime,pump_ctrl, args = (drugpump1,0)).start()
            threading.Timer(dp1ontime,pump_ctrl, args = (wastepump1,1)).start()
            threading.Timer(dp1ontime+wp1ontime,pump_ctrl, args = (wastepump1,0)).start()
            pump_drug=1
            pump_nut=0
            pump_waste =1
            
        else: 
            pump_ctrl(mediapump1,1)
            threading.Timer(mp1ontime,pump_ctrl, args = (mediapump1,0)).start()
            threading.Timer(dp1ontime,pump_ctrl, args = (wastepump1,1)).start()
            threading.Timer(mp1ontime+ wp1ontime,pump_ctrl, args = (wastepump1,0)).start()
            pump_nut =1
            pump_drug=0
            pump_waste =1
    else:
        pump_nut=0
        pump_waste=0
        pump_drug=0
    return pump_drug, pump_nut, pump_waste, avOD_buffer

avOD_buffer = np.zeros(OD_avg_length)
#how many loops this should run for
endloops =100 
#recursive loop function thing


def on_timer(loop_count, addmediafreq,avgnum, start_time, endloops, dp1ontime,mp1ontime,wp1ontime,ODdata, pump_drug, pump_nut, pump_waste, timing, avOD_buffer, outdir, filenum,filesize):

    timing = get_currtime() 
    #arduinoData  = str(np.round(np.random.rand()*50 + 950).astype(int))
    #measure OD from 1st channel only for know
    ODdata = measure(16)[0]
    #arduinoData = ser.readline().decode('ascii')
    #print(data)
    #arduinoData=(measure(1).decode('ascii'))

    #format data something something
    if(len(ODdata) > 0):
        ODdata = int(ODdata)
    else:
        ODdata = 0
    print(ODdata)
    
 
    #pump_ctrl(drugpump1,0)
    #pump_ctrl(mediapump1,0)
    #pump_ctrl(wastepump1,0)
    pump_drug, pump_nut, pump_waste, avOD_buffer = cycloresistron(loop_count, addmediafreq, avgnum,dp1ontime,mp1ontime,wp1ontime, ODdata, pump_drug, pump_nut, pump_waste, avOD_buffer)
    loop_count += 1
    #run plot function for every iteration

    ODdata, pump_nut, pump_drug, pump_waste, timing, filenum = savefunc(loop_count, ODdata, pump_nut, pump_drug, pump_waste, timing,outdir,filenum,filesize)

    

    
    #we only want the morbidostat algorithm to run every 2 seconds, but this is not the way to do t
    if loop_count != endloops:
        timerobject = threading.Timer(2, on_timer, args = (loop_count, addmediafreq,avgnum, start_time, endloops, dp1ontime,mp1ontime,wp1ontime,ODdata, pump_drug, pump_nut, pump_waste, timing, avOD_buffer,outdir,filenum,filesize))
        timerobject.start()
        print(filenum)
    

on_timer(loop_count, addmediafreq,avgnum, start_time, endloops, dp1ontime,mp1ontime,wp1ontime,ODdata, pump_drug, pump_nut, pump_waste, start_time, avOD_buffer,outdir,filenum,filesize)


