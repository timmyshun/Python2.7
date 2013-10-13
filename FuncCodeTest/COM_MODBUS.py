# -*- coding: utf-8 -*-
"""
制作人 测试部郭顺峰 工号1818 有问题请反馈
请安装编译器python 2.7版本并确保安装pyserial库以及COM_MODBUS_Func.py与本文件在同一文件夹内
"""

#读写参数的高位  FP参数以1F开头

"""
结构信息为(功能码号[读写参数的十进制低位],最大值,最小值,默认值,权限)
最大值最小值忽略小数点(5.30=530)
其中权限0代表运行中停止都不可修改
权限1代码停止中可修改,运行中不可修改
权限2代码运行停止都可修改
"""

#F4组功能码信息
Fgroup = 0xF4
Fdata =[(0,0,59,1,1),(1,0,59,4,1),(2,0,59,9,1),(3,0,59,12,1),(4,0,59,13,1),(5,0,59,0,1),\
	(6,0,59,0,1),(7,0,59,0,1),(8,0,59,0,1),(9,0,59,0,1),(10,0,1000,10,2),\
	(11,0,3,0,1),(12,1,65535,1000,2),(13,0,1000,0,2),(14,-1000,1000,0,2),(15,0,1000,1000,2),\
	(16,-1000,1000,1000,2),(17,0,1000,10,2),(18,0,1000,0,2),(19,-1000,1000,0,2),(20,0,1000,1000,2),\
	(21,-1000,1000,1000,2),(22,0,1000,10,2),(23,-1000,1000,-1000,2),(24,-1000,1000,-1000,2),(25,-1000,1000,1000,2),\
	(26,-1000,1000,1000,2),(27,0,1000,10,2),(28,0,5000,0,2),(29,-1000,1000,0,2),(30,0,5000,5000,2),\
	(31,-1000,1000,1000,2),(32,0,1000,10,2),(33,111,555,321,2),(34,0,111,000,2),(35,0,36000,0,1),\
	(36,0,36000,0,1),(37,0,36000,0,1),(38,0,11111,0,1),(39,0,11111,0,1)]


        
import serial
import sys,time
from COM_MODBUS_Func import scan,str4read,CRC16_ModbusRTU
from COM_MODBUS_Func import Back2org,Stop,Run
from COM_MODBUS_Func import CheckDefault,CheckMinMax_Stop,CheckMinMax_Run 

print "Available COM:\n"   # 扫描可用的端口
available = scan()
print available

ErrorData = []
DefaultError=[]
StopChangeError=[]
RunChangeError=[]
try : # OPEN COM
    ser2 = serial.Serial(0)
    print "COM is opened!"
except serial.SerialException:
    print 'Cannot open COM'
    time.sleep(2)
    sys.exit()

#端口属性设置
ser2.baudrate = 9600   #波特率
                       # (50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,
                       #   9600, 19200, 38400, 57600, 115200)
ser2.bytesize = 8      #数据位  5,6,7,8
ser2.parity = 'N'      #奇偶校验位  'N'无,'O'奇,'E'偶,'M'标志,'S' 空格
ser2.stopbits = 2      #停止位  1 ,1.5, 2
ser2.timeout = 0.05       #响应时间限制 None：无限等待,0无阻塞，x 秒
ser2.xonxoff = False   #software flow control
ser2.rtscts = False    #hardware (RTS/CTS) flow control Ture False
ser2.dsrdtr=False      #hardware (DSR/DTR) Ture False


#停机
Stop(ser2)

MSG = Back2org(ser2)#恢复出厂参数
print MSG


errorcount = 0
for (address,min_data,max_data,default_data,flag) in Fdata:


    #检测出厂参数是否与说明书对应：
    if CheckDefault(ser2,Fgroup,address,default_data) > 0:
        errorcount += 1
        DefaultError.append((address,min_data,max_data,default_data,flag))
        if (address,min_data,max_data,default_data,flag) not in ErrorData:            
            ErrorData.append((address,min_data,max_data,default_data,flag))
  

if Stop(ser2):
    print "Stoped"
else:
    print "Canot Stop"
    
for (address,min_data,max_data,default_data,flag) in Fdata:
    #停止状态下进行参数修改，看是否与说明书对应
    #如果不测试运行状态请将flag直接改为1
    if CheckMinMax_Stop(ser2,Fgroup,address,min_data,max_data,default_data,flag) > 0:
        errorcount += 1
        StopChangeError.append((address,min_data,max_data,default_data,flag))
        if (address,min_data,max_data,default_data,flag) not in ErrorData:            
            ErrorData.append((address,min_data,max_data,default_data,flag))
        
MSG = Back2org(ser2)#恢复出厂参数
print MSG
#设置控制源为通讯
print 'Set F0-02 = 2 '
recvMsg = ''
clockcount = 0
while (recvMsg!='\x01\x06\xF0\x02\x00\x02\x9A\xCB'):
    ser2.flushOutput()
    ser2.flushInput() 
    ser2.write('\x01\x06\xF0\x02\x00\x02\x9A\xCB')
    recvMsg = ser2.read(8)               
    clockcount +=1
    if clockcount>=10:
        print 'Can Not Set F0-02 = 2'
        break

for (address,min_data,max_data,default_data,flag) in Fdata:
    #分别在运行下进行参数修改，看是否与说明书对应
    #会进入运行状态,请确认运行安全,如果不测试运行状态请将flag直接改为1
    if not Run(ser2): #由于运行中更改某些参数会使机器停机F0-02
        print "Cannot Run"
        break
    #遍历最大最小值
    if CheckMinMax_Run(ser2,Fgroup,address,min_data,max_data,default_data,flag) > 0:
        errorcount += 1
        RunChangeError.append((address,min_data,max_data,default_data,flag))
        if (address,min_data,max_data,default_data,flag) not in ErrorData:            
            ErrorData.append((address,min_data,max_data,default_data,flag))
        
Stop(ser2)                    
print "\n\n\nError:%d"%errorcount
print "\nErrorData:"
print ErrorData
print "\nDefaultError:"
print DefaultError
print "\nStopChangeError:"
print StopChangeError
print "\nRunChangeError:"
print RunChangeError


ser2.close()            # 记住使用完后关闭端口

print "\nCOM1 is closed!"

input("Press any key to exit:")
sys.exit()

