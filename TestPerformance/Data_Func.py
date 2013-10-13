import os,math,time,math
import serial
from COM_MODBUS_Func import *


def GetMsg(serial,sendMsg):
    iBaudrate = serial.baudrate
    sleeptime = 2*8*8/iBaudrate
    recvMsg = ''
    errorNum = 0
    while( recvMsg[0:2]!= sendMsg[0:2] ):
        serial.flushOutput()
        serial.flushInput() 
        serial.write(sendMsg)
        time.sleep(sleeptime)
        recvMsg = serial.read(8)
        if errorNum >= 3:
            return ("",0)
        else:
            errorNum += 1
    return (recvMsg,1)
            
def DataAnysis(serial,stationNum,highAdd,lowAdd,timelong,internal):
    data = []
    average = 0
    maxdata = 0
    peakPeak = 0
    variance = 0
    avvariance = 0
    
    header = chr(stationNum) + '\x03'
    sendMsg = CreatMsg(header,highAdd,lowAdd,1)
    recvMsg = ''
    flag = 0

    counter = timelong
    for i in range(counter):
        (recvMsg,flag) = GetMsg(serial,sendMsg)
        if flag == 1:
            data.append(ord(recvMsg[5])+ord(recvMsg[4])*256)
        time.sleep(internal/1000)
    n = len(data)
    for i in range(n):
        average += data[i]
    average = average/n
    for i in range(n):
        variance += math.pow((data[i]-average),2)
        avvariance += math.pow(data[i],2)
    variance /= n
    avvariance /= n
    avvariance = math.sqrt(avvariance)
    maxdata = max(data)
    peakPeak = maxdata  - min(data)
    
    return (average,maxdata,peakPeak,variance,avvariance)
    
        
