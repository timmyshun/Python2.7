# -*- coding: utf-8 -*-
import serial
import sys,time

def Hex2Str(num):#将数转换成16进制字符串   
    hexdic = { 10:'A', 11:'B',12:'C', 13:'D',14:'E', 15:'F' }
    numH = (num>>4)
    numL = num%16
    hexstr = ''
    if numH > 9:
        hexstr +=  hexdic[numH]
    else :
        hexstr +=  str(numH)
    if numL > 9:
        hexstr +=  hexdic[numL]
    else :
        hexstr +=  str(numL)
    return hexstr

def StrH2Num(string):
    strdic = { '0':0,'1':1,'2':2,'3':3,'4':4,\
               '5':5,'6':1,'6':6,'7':7,'8':8,'9':9,\
               'A':10, 'B':11,'C':12, 'D':13,'E':14, 'F':15,\
               'a':10, 'b':11,'c':12, 'd':13,'e':14, 'f':15}
    lenght = len(string)
    Num = 0
    for i in range(lenght):
        Num += strdic[string[i]]*pow(16,lenght-i-1)
    return Num

def StrD2Num(string):
    lenght = len(string)
    Num = 0
    k=0
    for i in range(lenght):
        if ord(string[lenght-i-1])>47 and ord(string[lenght-i-1])<58:
            Num += int(string[lenght-i-1])*pow(10,i-k)
        else:
            k +=1
    return Num
        
def scan():
    """函数搜索可用的串口"""    
    available = []
    for i in range(256):
        try:
            s = serial.Serial(i)
            available.append( (i, s.portstr))
            s.close()   # explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass
    """
    if (0,'COM1') in available: #检测打开的端口是否可用
        print 'COM1 is  available'
    else:
        print 'COM1 is not  available'
    """
    return available

def str4read( Msg = "" ):
    """把传输数据转换成显示"""
    
    length = len(Msg)
    hexdic = { 10:'A', 11:'B',12:'C', 13:'D',14:'E', 15:'F' }
    readMsg = ""

    for i in range(length):
        num = ord(Msg[i])   #ord() 把ASC字符变成数字，反操作 chr()（或unichr）把数字变成ASC字符
        numH = int(num/16)
        numL = num%16
        if numH > 9:
            readMsg +=  hexdic[numH]
        else :
            readMsg +=  str(numH)
        if numL > 9:
            readMsg +=  hexdic[numL]
        else :
            readMsg +=  str(numL)

        readMsg +=  ' '
        
    return readMsg

def CRC16_ModbusRTU(data = ''):#生成MODBUS CRC校验码
    """生成Modbus协议的CRC校验
       CRC16= X16+X15+X2+1
    """
    crc_value = 0xFFFF # 预置FFFF的16位寄存器
    lenght = len(data)
    for k in range(lenght):
        crc_value^=ord(data[k])  #每八位与低位寄存器异或
        for i in range(8):
            if(crc_value&0x0001): 
                crc_value = (crc_value>>1)^0xa001 #X15+X2+1为100A反转多项式为A001 让低位在前
            else:
                crc_value = crc_value>>1
    crc_Hig = chr(crc_value>>8)       #高位
    crc_Low = chr(crc_value&0x00FF)   #低位
    crcMsg = crc_Low + crc_Hig        #高低位置入消息交换
    return crcMsg

def SendMessage(serial,sendMsg):
    #发送数据并取得回复数据一次
    sleeptime = 20.0/1000
    recvMsg = ''

    serial.flushInput()
    serial.flushOutput()
    serial.write(sendMsg)
    time.sleep(sleeptime)
    recvMsg = serial.read(4)
    if len(recvMsg) < 4:
        return ''
    if recvMsg[2] == '\x80':   #如果为错误码就读4+4字节-4
        recvMsg += serial.read(4)
        if len(recvMsg) <8:
            return ''
    elif recvMsg[1] == '\x03':   #读操作
        byteNum = ord(recvMsg[3])  # 读的字节数 2(头)+1(字节数)+n+2(CRC)-4
        recvMsg += serial.read(byteNum+2)
        if len(recvMsg) <byteNum+6:
            return ''
    elif recvMsg[1] == '\x06': #写2字节操作  8-4
        recvMsg += serial.read(4)
        if len(recvMsg) <8:
            return ''

    if CheckCrc(recvMsg):
        return recvMsg
    else:
        return ''
    
    return recvMsg

def CheckCrc(Msg):
    if(len(Msg)<5):
        return False
    RightCrc = CRC16_ModbusRTU(Msg[:-2])
    if(RightCrc==Msg[-2:]):
        return True
    else:
        return False
def ReSendMessage(serial,sendMsg,u):
    #发送数据并取得回复数据u次
    recvMsg = ''
    for i in range(u):
        recvMsg = SendMessage(serial,sendMsg)
        if len(recvMsg) != 0:
            return recvMsg
    return ''

def Back2org(serial,u):
    """恢复出厂参数并等待恢复完成，返回1"""
    sendMsg = '\x01\x06\x1F\x01\x00\x01'
    sendMsg += CRC16_ModbusRTU(sendMsg)   #ModbusRTU CRC16冗余校验信息附加
    recvMsg = ReSendMessage(serial,sendMsg,3)

    time.sleep(0.5)
    return 1

def Stop(serial,FreNum,u):
    #使变频器停止并检测是否停止成功停止返回1否则返回0

    Header = chr(FreNum)+'\x06'
    sendMsg = CreatMsg(Header,0x20,0x00,6)
    recvMsg = ReSendMessage(serial,sendMsg,u)
    return 1

def FreeStop(serial,u):
    #使变频器停止并检测是否停止成功停止返回1否则返回0
   
    sendMsg = CreatMsg('\x01\x06',0x20,0x00,5)
    recvMsg = ReSendMessage(serial,sendMsg,3)
    return 1

def Run(serial,FreNum,u):
    #使变频器运行并检测是否运行成功运行返回1否则返回0
    Header = chr(FreNum)+'\x06'
    sendMsg = CreatMsg(Header,0x20,0x00,1)
    recvMsg = ReSendMessage(serial,sendMsg,u)
    return 1


def CreatMsg(Header,HighAddress,LowAddress,data):
    Msg = ''
    Msg += Header
    Msg += chr(HighAddress)
    Msg += chr(LowAddress)
    if data >= 0:
        Msg  += chr(data>>8)     
        Msg  += chr(data&0x00FF)  
    else:
        z = data + 65536
        Msg  += chr(z>>8)       
        Msg  += chr(z&0x00FF)   
    Msg += CRC16_ModbusRTU(Msg)   #ModbusRTU CRC16冗余校验信息附加
    return Msg



def SetParameter(serial,stationNum,highAddress,lowAddress,data):

    recvMsg = ''
    errorNum = 0
    #写入。
    Header1 = chr(stationNum)+'\x03'
    Header2 = chr(stationNum)+'\x06'
    
    sendMsg = CreatMsg(Header2,highAddress,lowAddress,data)      
    recvMsg = ReSendMessage(serial,sendMsg,5)

    #再读取参数,参数与所要写的不一致就报错。
    sendMsg = CreatMsg(Header1,highAddress,lowAddress,1)
    recvMsg = ReSendMessage(serial,sendMsg,3)
    if len(recvMsg) == 8:
        Ordata = ord(recvMsg[4])*256 + ord(recvMsg[5])
        if Ordata == data :
            return True
        else:
            return False
    else:
        return False
    return True

def GetParameter(serial,stationNum,highAddress,lowAddress):

    recvMsg = ''
    errorNum = 0
    Header1 = chr(stationNum)+'\x03'
    sendMsg = CreatMsg(Header1,highAddress,lowAddress,1)
    recvMsg = ReSendMessage(serial,sendMsg,3)
    if len(recvMsg) == 8:
        Ordata = ord(recvMsg[4])*256 + ord(recvMsg[5])   
        return (Ordata,True)
    else:
        return (0,False)



def TestPerformance(serial,Frequence,timelong,internal):
    maxFre = 1
    n = len(Frequence)
    SetParameter(serial,1,0xF0,2,2)
    SetParameter(serial,1,0xF0,8,0)
    AccendTime,flag = GetParameter(serial,1,0xF0,17)
    AccendTime /= 10
    for i in range(n-1):
        maxFre = max(maxFre,Frequence[i+1]-Frequence[i])
    sleeptime = AccendTime*maxFre/50+1
    averageV = []
    maxV = []
    minV = []
    
    Run(serial,3)
    for i in range(n):
        SetParameter(serial,1,0xF0,8,Frequence[i]*100)
        time.sleep(sleeptime)
        (average,maxdata,mindata) = DataAnysis(serial,1,0x10,0x1E,timelong,internal)
        averageV.append(average)
        maxV.append(maxdata)
        minV.append(mindata)
    Stop(serial,3)

    return (averageV,maxV,minV)
    
if __name__ == '__main__':
    print CheckCrc('\x01\x03\xf0\x08\x00\x01\x36\xc8')
    """
    try : # OPEN COM
        ser2 = serial.Serial(0)
        print "COM is opened!"
    except serial.SerialException:
        print 'Cannot open COM'
        time.sleep(2)
        sys.exit()

    #端口属性设置
    ser2.baudrate = 38400   #波特率
    ser2.bytesize = 8      #数据位  5,6,7,8
    ser2.parity = 'N'      #奇偶校验位  'N'无,'O'奇,'E'偶,'M'标志,'S' 空格
    ser2.stopbits = 2      #停止位  1 ,1.5, 2
    ser2.timeout = 0.05       #响应时间限制 None：无限等待,0无阻塞，x 秒
    ser2.xonxoff = False   #software flow control
    ser2.rtscts = False    #hardware (RTS/CTS) flow control Ture False
    ser2.dsrdtr=False      #hardware (DSR/DTR) Ture False

    Frequence = [1,10,20]
    (averageV,maxV,minV) = TestPerformance(ser2,Frequence,100,1)
    for i in range(len(Frequence)):
        print u"速度:",Frequence[i],u"平均:",averageV[i],u"最大:",maxV[i],u"最小",minV[i]
    ser2.close()            # 记住使用完后关闭端口

    print "\nCOM1 is closed!"
    """

