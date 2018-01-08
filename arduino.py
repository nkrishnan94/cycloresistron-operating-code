import serial.tools.list_ports
import numpy as np
import time
from matplotlib import pyplot as plt
import threading 
import datetime

ports = serial.tools.list_ports.comports()

#find arduino
for port in ports:
    # print(str.split(str(port),' - '))
    if 'Arduino' in str(port):
        print(port)
        arduino_port  = str.split(str(port),' - ')[0]

plt.ion() # set plot to animated

#establish connection with arduiono
ser = serial.Serial(arduino_port, baudrate = 9600, timeout=1)

#for plot
ydata = [0] * 1000
# colour_data = ['k'] * 1000
# ax1=plt.axes() 

#
arduinoData = 0
line = plt.plot(arduinoData)
num_cham = 16

#pumps
mediapump1 = 2
drugpump1 = 3
wastepump1 = 4

#pumpcalbration
#mp1ontime= 5/3.25
#dp1ontime= 5/3.35
#wp1ontime= 5/4.45

#control pumps
def pump_ctrl(pnum, pstate):
    ser.flush() #flush before sending signal
    ser.write(('PUMP %d %d\n' % (pnum, pstate)).encode()) #send signal telling Arduino to turn off pump 

#measure OD in all arduino analog inputs (we only have 1 as of now)
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

#code to begin to precisely record and keep track of time
#yet to be fully implemented   
start_time = get_currtime()  
        
#loop counter
i = 0
#how often morbidostat algorithm is implimented
intervals = 30
#number of most recent OD measurements thats averaged for morbidostat algorthm
avgnum = 5
#wastetime = 5
while 1:
    #arduinoData  = str(np.round(np.random.rand()*50 + 950).astype(int))
    
    #only interested in first channel for now
    arduinoData = measure(16)[0]
    #arduinoData = ser.readline().decode('ascii')
    #print(data)
    #arduinoData=(measure(1).decode('ascii'))
    
    #formatting data something something
    if(len(arduinoData) > 0):
        arduinoData = int(arduinoData)
    else:
        arduinoData = 0
    print(arduinoData)

    ydata.append(arduinoData) 
    #makes sure everythings off
    pump_ctrl(drugpump1,0)
    pump_ctrl(mediapump1,0)
    pump_ctrl(wastepump1,0)
    
    #'morbdostat algorithm'
    if (i % intervals) == 0:
        if np.mean(ydata[-avgnum:-1]) >400:
            pump_ctrl(drugpump1,1)
            
        else: 
            pump_ctrl(mediapump1,1)
            
    #turn on waste after the media is infused        
    if (i % intervals) == 1:
        pump_ctrl(wastepump1,1)
    #if i == 5:
    #    pump_ctrl(was ntepump,1)
    #if arduinoData > 975: 
    #    color = 'r'
    #else: 
    #    color = 'k'
    
    
    ydata.append(arduinoData) 
    
    #ensure measurements are taken every two seconds
    time.sleep(2)
    i = i+1
    #plot data
    #this can be better
    plt.axis([0, len(ydata), 0, 1000])
    plt.ion()
    
    plt.plot(np.arange(len(ydata)), ydata,color = 'r')
    plt.setp(line, linewidth=2.0,color = 'r')

    plt.pause(.0000000001)


