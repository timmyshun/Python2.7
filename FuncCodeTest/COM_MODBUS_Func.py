#制作人 测试部郭顺峰 工号1818 有问题请反馈
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


def Back2org(ser2,u):
    """恢复出厂参数并等待恢复完成，返回完成提示字符串"""
    sendMsg = '\x01\x06\x1F\x00\x00\x00\x8E\x1E'
    recvMsg = ''
    clockcount = 0
    iBaudrate = ser2.baudrate
    sleeptime = 2*len(sendMsg)*8/iBaudrate
    while(recvMsg!='\x01\x06\x1F\x00\x88\x88\xE8\x78'):
        ser2.flushOutput()
        ser2.flushInput()
        ser2.write(sendMsg)
        time.sleep(sleeptime)
        recvMsg = ser2.read(8)
        clockcount +=1
        if clockcount>u:
            return 0

    sendMsg = '\x01\x06\x1F\x01\x00\x01\x1E\x1E'
    recvMsg = ''
    clockcount = 0
    while(recvMsg!='\x01\x06\x1F\x01\x00\x01\x1E\x1E'):
        ser2.flushOutput()
        ser2.flushInput()
        ser2.write(sendMsg)
        recvMsg = ser2.read(8)
        clockcount +=1
        if clockcount>=u:
            return 'Can not Return to default!'
    sendMsg = '\x01\x06\xF0\x02\x00\x00\x1B\x0A'
    recvMsg = ''
    clockcount = 0
    while(recvMsg!='\x01\x06\xF0\x02\x00\x00\x1B\x0A'):
        time.sleep(0.5)
        ser2.flushOutput()
        ser2.flushInput()
        ser2.write(sendMsg)
        time.sleep(sleeptime)
        recvMsg = ser2.read(8)
        clockcount +=1
        if clockcount>=20:
            return 0           
    return 1

def Stop(ser2,u):
    #使变频器停止并检测是否停止成功停止返回1否则返回0
   
    sendMsg = '\x01\x06\x20\x00\x00\x05\x42\x09'
    recvMsg = ''
    clockcount = 0
    iBaudrate = ser2.baudrate
    sleeptime = 2*len(sendMsg)*8/iBaudrate
    while(recvMsg!='\x01\x06\x20\x00\x00\x05\x42\x09'):
        ser2.flushOutput()   #这种保证传输的处理方式有些过于严格,使脚本速度比较慢
        ser2.flushInput() 
        ser2.write(sendMsg)
        time.sleep(sleeptime)
        recvMsg = ser2.read(8)               
        clockcount +=1
        if clockcount>=u:
            return 0
    sendMsg = '\x01\x03\x30\x00\x00\x01\x8B\x0A'
    recvMsg = ''
    clockcount = 0
    while(recvMsg!='\x01\x03\x00\x02\x00\x03\xA4\x0B'):
        ser2.flushOutput()
        ser2.flushInput() 
        ser2.write(sendMsg)
        time.sleep(sleeptime)
        recvMsg = ser2.read(8)               
        clockcount +=1        
        if clockcount>=20:
            return 0
    return 1

def Run(ser2,u):
    #使变频器运行并检测是否运行成功运行返回1否则返回0
    
    sendMsg = '\x01\x06\x20\x00\x00\x01\x43\xCA'
    recvMsg = ''
    clockcount = 0
    iBaudrate = ser2.baudrate
    sleeptime = 2*len(sendMsg)*8/iBaudrate
    while(recvMsg!='\x01\x06\x20\x00\x00\x01\x43\xCA'):
        ser2.flushOutput()
        ser2.flushInput() 
        ser2.write(sendMsg)
        time.sleep(sleeptime)
        recvMsg = ser2.read(8)
        clockcount +=1
        if clockcount>=u:
            return 0
    


    sendMsg = '\x01\x03\x30\x00\x00\x01\x8B\x0A'
    recvMsg = ''
    clockcount = 0
    while(recvMsg!='\x01\x03\x00\x02\x00\x01\x25\xCA'):
        ser2.flushOutput()
        ser2.flushInput() 
        ser2.write(sendMsg)
        time.sleep(sleeptime)
        recvMsg = ser2.read(8)               
        clockcount +=1
        if clockcount>=10:           
            return 0
    return 1
def CreatRange(Min,Max):
    if Max <=50:
        Step = Max/5
    else:
        Step = max(1,int((Max-Min)/5))
    if Min >=0:
	Range = range(max(0,Min-Step*5),min(65535,Max+Step*5),Step)
    else:
	Range = range(max(-32768,Min-Step*5),min(32767,Max+Step*5),Step)

    if Min not in Range:
        Range.append(Min)
    if Max not in Range:
        Range.append(Max)
    return Range

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

def CheckMsg(sendMsg,recvMsg,data,min_data,max_data,flag):
    if data >= min_data and data <= max_data:
        if recvMsg[4:6] == sendMsg[4:6]:
            if flag == 0:
                   errorcount +=1
                   print "Check "+Hex2Str(Fgroup)+' '+str(address)+' '+'write:'+str(i)+"  changed"
                   return 1
            else:
                if flag != 0:
                    errorcount +=1
                    print "Check "+Hex2Str(Fgroup)+' '+str(address)+' '+'write:'+str(i)+"   CannotChanged"
                    return 1
        else:
            if recvMsg[2] != '\x80':
                errorcount +=1
                print "Check "+Hex2Str(Fgroup)+' '+str(address)+' '+'write:'+str(i)+"  ChangeOutArrange"
                return 1

def CheckDefault(ser2,u,Fgroup,address,default_data):
    #检测功能码是否与默认值对应   
    #发送数据 
    sendMsg = CreatMsg('\x01\x03',Fgroup,address,1)
    #接收数据
    recvMsg = ''
    clockcount = 0
    iBaudrate = ser2.baudrate
    sleeptime = 2*len(sendMsg)*8/iBaudrate
    while(len(recvMsg)<8):
        ser2.flushOutput()
        ser2.flushInput()
        ser2.write(sendMsg)
        time.sleep(sleeptime)
        recvMsg = ser2.read(8)        
        clockcount += 1
        if clockcount>=u:            
            return 0

    
    if recvMsg[-2:] == CRC16_ModbusRTU(recvMsg[:-2]):
        pass
    else :
        return 1

    #检查数据默认值 
    if default_data >=0:
        default_dataH = chr(default_data>>8)
        default_dataL = chr(default_data&0x00FF)
    else:
        default = default_data + 65536
        default_dataH = chr(default>>8)
        default_dataL = chr(default&0x00FF)
    
        
    if recvMsg[4] == default_dataH and recvMsg[5]== default_dataL :
        return 10
    else:
        return 2


    
def CheckMinMax_Stop(ser2,u,Fgroup,address,min_data,max_data,default_data,flag):
    #检测功能码在停机状态下修改是否正确

    checknum = CreatRange(max_data,max_data)
    iBaudrate = ser2.baudrate
    sleeptime = 2*8*8/iBaudrate	
    for i in checknum:
        sendMsg = CreatMsg('\x01\x06',Fgroup,address,i)
        #发送和接收数据
        recvMsg = ''
        clockcount = 0
        while(len(recvMsg)<8):
            ser2.flushOutput()
            ser2.flushInput() 
            ser2.write(sendMsg)
            time.sleep(sleeptime)
            recvMsg = ser2.read(8)
            clockcount +=1
            if clockcount>=u:
                return 0
        
        if i >= min_data and i <= max_data:
            if recvMsg == sendMsg :
                if flag ==0:
                    return 3
            else:
                if flag != 0:
                    return 4
        else:
            if recvMsg[2] != '\x80':
                return 5
 

    if(flag ==1 or flag ==2 ):     
        sendMsg = CreatMsg('\x01\x06',Fgroup,address,default_data)
        #发送和接收数据
        recvMsg = ''
        clockcount = 0
        while( recvMsg!= sendMsg ):
            ser2.flushOutput()
            ser2.flushInput() 
            ser2.write(sendMsg)
            time.sleep(sleeptime)
            recvMsg = ser2.read(8)
            clockcount +=1
            if clockcount>=u:
                return 11
    
    return 10


def CheckMinMax_Run(ser2,u,Fgroup,address,min_data,max_data,default_data,flag):
    #检测功能码在运行机状态下修改是否正确
    checknum = CreatRange(max_data,max_data)
    iBaudrate = ser2.baudrate
    sleeptime = 2*8*8/iBaudrate	
    for i in checknum:
        sendMsg = CreatMsg('\x01\x06',Fgroup,address,i)
        #发送和接收数据
        recvMsg = ''
        clockcount = 0
        while(len(recvMsg)< 8):
            ser2.flushOutput()
            ser2.flushInput() 
            ser2.write(sendMsg)
            time.sleep(sleeptime)
            recvMsg = ser2.read(8)
            clockcount +=1
            if clockcount>=u:                
                return 0
        
        if i >= min_data and i <= max_data:
            if recvMsg == sendMsg :
               if flag ==0 or flag ==1:
                   return 6
            else:
                if flag == 2:   		
		    return 7
        else:
            if recvMsg[2] != '\x80':
		return 8

    if(flag ==2 and sendMsg[2:4]!='\xF0\x02'):     
        sendMsg = CreatMsg('\x01\x06',Fgroup,address,default_data)
        #发送和接收数据
        recvMsg = ''
        clockcount = 0
        while( recvMsg!= sendMsg ):
            ser2.flushOutput()
            ser2.flushInput() 
            ser2.write(sendMsg)
            time.sleep(sleeptime)
            recvMsg = ser2.read(8)
            if clockcount>=u:
                return 11
    return 10




