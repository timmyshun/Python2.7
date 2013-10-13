#! /usr/bin/env python
#coding=utf-8
import os,math,time
import threading
import wx,wx.grid
import serial
from InterfaceFunc import *
from COM_MODBUS_Func import *
from DataExchange import *

class MyApp(wx.App):
    
    def OnInit(self):
       frame = MyFrame(u"功能码测试工具", (50, 60), (520, 600))
       frame.Show()
       self.SetTopWindow(frame)
       return True
    
class MyFrame(wx.Frame):
    path = ''
    Fgroup = []
    Fdata = []
    DefaultResult = []
    StopResult = []
    RunResult = []
    serialSet = {'COM':0,'Baudrate':9600,'Bytesize':8,'Parity':'N','Stopbits':2,'Timeout':0.05,'Resend':2}
    defaultState = 0
    stopState = 0
    runState = 0
    def __init__(self, title, pos, size):
        wx.Frame.__init__(self, None, -1, title, pos, size)
        self.CreateMenuBar()                
        self.CreateStatusBar()
        self.grid = Grid(self)
        self.grid.EnableEditing(False)

        

                        
        #
    #建立菜单栏
    def createCOMS(self,num):
        COMS = []
        for i in range(num):
            COMS.append(("COM%d"%(i+1), "",self.OnSelectCom,
                           wx.ITEM_RADIO))
        return COMS
    def createBaudrate(self):
        Bps = []
        for i in (9600,50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,
                  19200, 38400, 57600, 115200):
            Bps.append(("%d"%(i), "",self.OnSelectBaudrate ,
                           wx.ITEM_RADIO))
        return Bps
    def createBytesize(self):
        Bitsize = []
        for i in range(8,4,-1):
            Bitsize.append(("%d"%(i),"",self.OnSelectBytesize,
                           wx.ITEM_RADIO))
        return Bitsize
    def createParity(self):
        Verify = []
        for i in (u"N无",u"O奇",u"E偶",u"M标志",u"S空格"):
            Verify.append((i,"",self.OnSelectParity,
                           wx.ITEM_RADIO))
        return Verify
    def createStopbits(self):
        Stopbit = []
        for i in (2,1.5,1):
            Stopbit.append((str(i),"",self.OnSelectStopbits,
                           wx.ITEM_RADIO))
        return Stopbit
    def createTimeout(self):
        Timeout = []
        Timeout.append((str(0.05)+'S',"",self.OnSelectTimeout,
                        wx.ITEM_RADIO))
        for i in range(7):
            t = 0.02 *math.pow(2,i)
            Timeout.append((str(t)+'S',"",self.OnSelectTimeout,
                           wx.ITEM_RADIO))
        return Timeout
    def createResend(self):
        Resend = []
        for i in range(1,10):
            Resend.append((str(i),"",self.OnSelectResend,
                           wx.ITEM_RADIO))
        return Resend
    def menuData(self):
        return [(u"&Q载入测试数据",(
                    (u"&Load载入文件","",self.OnLoadFile),
                    ("", "", ""),
                    (u"&Output输出结果","",self.OnOutputFile))),
                (u"&W串口设置", (
                    (u"查询可用串口","",self.OnCheckCOM),
                    ("", "", ""),
                    (u"串口号",self.createCOMS(12)),
                    (u"波特率",self.createBaudrate()),
                    (u"数据位", self.createBytesize()),
                    (u"奇偶校验位",self.createParity()),
                    (u"停止位", self.createStopbits()),
                    (u"超时时间", self.createTimeout()),
                    (u"重发次数", self.createResend()),
                    ("", "", ""),
                    (u"重新设置已经打开的串口", "", self.OnReFreshCOM))),
                (u"&E开关串口",(
                    (u"&Open打开串口","",self.OnOpenCOM),
                    ("", "", ""),
                    (u"&Close关闭串口","",self.OnCloseCOM))),
                (u"&R测试项目",(
                    (u"测试默认值","",self.OnTestDefault),
                    (u"停止中测试","",self.OnTestStop),
                    (u"运行中测试","",self.OnTestRun),                 
                    ("", "", ""),
                    (u"终止测试","",self.OnEndTest))),
                (u"&O帮助和退出",(
                    (u"帮助","",self.OnHelp),
                    (u"关于..","",self.OnAbout),
                    ("", "", ""),
                    (u"退出..","",self.OnQuit),
                    ))]
    
    def CreateMenuBar(self):
        menuBar = wx.MenuBar()
        for eachMenuData in self.menuData():
            menuLabel = eachMenuData[0]
            menuItems = eachMenuData[1]
            menuBar.Append(self.createMenu(menuItems), menuLabel)
        self.SetMenuBar(menuBar)
        
    def createMenu(self, menuData):
        menu = wx.Menu()
        for eachItem in menuData:
            if len(eachItem) == 2:
                label = eachItem[0]
                subMenu = self.createMenu(eachItem[1])
                menu.AppendMenu(wx.NewId(), label, subMenu)
            else:
                self.createMenuItem(menu, *eachItem)
        return menu
    
    def createMenuItem(self, menu, label, status, handler,
                       kind=wx.ITEM_NORMAL):
        if not label:
            menu.AppendSeparator()
            return
        menuItem = menu.Append(-1, label, status, kind)
        self.Bind(wx.EVT_MENU, handler, menuItem)
   #菜单的事件响应
    def OnLoadFile(self, event):
        wildcard = "Excel source (*.xls)|*.xls|" \
            "All files (*.*)|*.*"
        dialog = wx.FileDialog(None, "Choose a file", os.getcwd(), 
            "", wildcard, wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.path = dialog.GetPath() 
        dialog.Destroy()
        if self.path == '':
            return
        
        self.Fgroup, self.Fdata = LoadExcel(self.path)
        if self.Fgroup == [0] and self.Fdata == [[(0,0,0,0,0)]]:
            wx.MessageBox(u"载入文件失败！！！请检查数据是否正确.", 
                "Failure!!!", wx.OK, self)
            return
        n = len(self.Fgroup)
        l = 0 
        for i in range(n):
            l += len(self.Fdata[i])
        k = self.grid.GetNumberRows()
        if l < k:
            self.grid.DeleteRows(0,k-l,True)
        elif l > k:
            self.grid.AppendRows(l-k,True)
        l = 0
        for i in range(n):
            m = len(self.Fdata[i])
            for j in range(m):
                self.grid.SetCellValue(l, 0, Hex2Str(self.Fgroup[i]))
                self.grid.SetCellValue(l, 1, str(self.Fdata[i][j][0]))
                l += 1
            
        
    def OnOutputFile(self, event):
        pass
    def OnCheckCOM(self, event):
        availableCOM = scan()
        wx.MessageBox(u"可用串口:"+str(availableCOM), 
                u"查询可用串口", wx.OK, self)
    def OnSelectCom(self, event):
        menubar = self.GetMenuBar()
        itemId = event.GetId()
        itemId = event.GetId()
        item = menubar.FindItemById(itemId)
        COM = int(item.GetLabel()[3:]) - 1
        self.serialSet['COM'] = COM
    def OnSelectBaudrate(self, event):
        menubar = self.GetMenuBar()
        itemId = event.GetId()
        itemId = event.GetId()
        item = menubar.FindItemById(itemId)
        Bps = int(item.GetLabel())
        self.serialSet['Baudrate'] = Bps
    def OnSelectBytesize(self, event):
        menubar = self.GetMenuBar()
        itemId = event.GetId()
        itemId = event.GetId()
        item = menubar.FindItemById(itemId)
        Bytesize = int(item.GetLabel())
        self.serialSet['Bytesize'] = Bytesize
    def OnSelectParity(self, event):
        menubar = self.GetMenuBar()
        itemId = event.GetId()
        itemId = event.GetId()
        item = menubar.FindItemById(itemId)
        Parity = item.GetLabel()[0]
        self.serialSet['Parity'] = Parity
    def OnSelectStopbits(self, event):
        menubar = self.GetMenuBar()
        itemId = event.GetId()
        itemId = event.GetId()
        item = menubar.FindItemById(itemId)
        Stopbits = float(item.GetLabel())
        self.serialSet['Stopbits'] = Stopbits
    def OnSelectTimeout(self, event):
        menubar = self.GetMenuBar()
        itemId = event.GetId()
        itemId = event.GetId()
        item = menubar.FindItemById(itemId)
        Timeout = float(item.GetLabel()[:-1])
        self.serialSet['Stopbits'] = Timeout
    def OnSelectResend(self, event):
        menubar = self.GetMenuBar()
        itemId = event.GetId()
        itemId = event.GetId()
        item = menubar.FindItemById(itemId)
        Resend = int(item.GetLabel())
        self.serialSet['Resend'] = Resend
    def OnReFreshCOM(self, event):
        COM = self.serialSet['COM']
        try:            
            self.ser.baudrate = self.serialSet['Baudrate']                          
            self.ser.bytesize = self.serialSet['Bytesize']      
            self.ser.parity = self.serialSet['Parity']      
            self.ser.stopbits = self.serialSet['Stopbits']     
            self.ser.timeout = self.serialSet['Timeout']
            self.SetStatusText(u"已经打开串口COM%d"%(COM+1))
            wx.MessageBox(u"重新设置参数成功 ", 
                u"设置参数成功", wx.OK, self)
        except:
            wx.MessageBox(u"重新设置参数失败！请检查是否打开的串口,端口属性是否适合.", 
                "Failure!!!", wx.OK, self)       
        
    def OnOpenCOM(self, event):
        COM = self.serialSet['COM']
        try:
            self.ser = serial.Serial(COM)            
            self.ser.baudrate = self.serialSet['Baudrate']                          
            self.ser.bytesize = self.serialSet['Bytesize']      
            self.ser.parity = self.serialSet['Parity']      
            self.ser.stopbits = self.serialSet['Stopbits']     
            self.ser.timeout = self.serialSet['Timeout']
            wx.MessageBox(u"已经打开串口COM%d"%(COM+1), 
                u"打开成功", wx.OK, self)
        except:
            wx.MessageBox(u"打开串口COM%d失败！请检查打开的串口是否可用,端口属性是否适合.\n         或者串口已经打开."%(COM+1), 
                "Failure!!!", wx.OK, self)
            
            
    def OnCloseCOM(self, event):
        COM = self.serialSet['COM']       
        try:            
            self.ser.close()
            wx.MessageBox(u"已经关闭串口COM%d"%(COM+1), 
                u"关闭成功", wx.OK, self)
        except:
            try:
                self.ser.flushOutput()
                self.ser.flushInput()
                self.ser.close()
                wx.MessageBox(u"已经关闭串口COM%d"%(COM+1), 
                    u"关闭成功", wx.OK, self)
            except:
                wx.MessageBox(u"关闭串口COM%d失败！请检查是否打开串口."%(COM+1), 
                    "Failure!!!", wx.OK, self)
    def checkstatusOK(self):
        if self.Fgroup == [] or (self.Fgroup == [0] and self.Fdata==[[(0,0,0,0,0)]]):
            wx.MessageBox(u"请先载入测试数据..", 
                "Failure!!!", wx.OK, self)
            return 0
        try:
            self.ser.flushOutput()
            self.ser.flushInput()
        except:
            wx.MessageBox(u"请检查是否打开串口.", 
                "Failure!!!", wx.OK, self)
            return 0
        if (self.defaultState+self.stopState+self.runState)>0:
            wx.MessageBox(u"其他测试正在进行中!", 
                "Failure!!!", wx.OK, self)
            return 0
        return 1
    def defaultTest(self):
        self.DefaultResult = []
        m = 0
        n = self.grid.GetNumberRows()
        for i in range(n):
            self.grid.SetCellValue(i, 2, '  ')
        for i in range(len(self.Fgroup)):            
            self.DefaultResult.append([])
            Fgroup = self.Fgroup[i]
            Fdata = self.Fdata[i]
            #检测出厂参数是否与说明书对应：
            for (address,min_data,max_data,default_data,flag) in Fdata:
                if self.defaultState == 0:
                    return
                errorNum = CheckDefault(self.ser,self.serialSet['Resend'],Fgroup,address,default_data)
                self.DefaultResult[i].append(errorNum)
                if errorNum == 10:
                    self.grid.SetCellValue(m, 2, u'通过')
                else:
                    self.grid.SetCellValue(m, 2, 'Error%d'%(errorNum))
                m += 1
                
        self.defaultState = 0
    def OnTestDefault(self, event):
        COM = self.serialSet['COM']
        if self.checkstatusOK()==0:
            return 
        
        dlg = wx.MessageDialog(None, u'是否恢复出厂参数',
                          u'默认值测试', wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            if not Back2org(self.ser,self.serialSet['Resend']):#恢复出厂参数
                dlg1 = wx.MessageDialog(None, u'恢复出厂参数失败，是否继续测试?',
                          u'默认值测试', wx.YES_NO | wx.ICON_QUESTION)
                result1 = dlg1.ShowModal()
                if result1 == wx.ID_NO:
                    return
            else:
                wx.MessageBox(u"参数恢复成功", 
                    u"参数恢复成功", wx.OK, self)
                
        elif result == wx.ID_NO:
            dlg2 = wx.MessageDialog(None, u'未恢复出厂参数，是否继续测试?',
                          u'默认值测试', wx.YES_NO | wx.ICON_QUESTION)
            result2 = dlg2.ShowModal()
            if result2 == wx.ID_NO:
                return
        self.defaultState = 1
        self.defaultTestThread = threading.Thread( target = self.defaultTest, name = "defaultTestThread" )
        self.defaultTestThread.start()

    def stopTest(self):
        self.StopResult = []
        m = 0
        n = self.grid.GetNumberRows()
        for i in range(n):
            self.grid.SetCellValue(i, 3, '  ')
        for i in range(len(self.Fgroup)):
            self.StopResult.append([])
            Fgroup = self.Fgroup[i]
            Fdata = self.Fdata[i]
            #检测出厂参数是否与说明书对应：
            for (address,min_data,max_data,default_data,flag) in Fdata:
                if self.stopState == 0:
                    return
                errorNum = CheckMinMax_Stop(self.ser,self.serialSet['Resend'],Fgroup,address,min_data,max_data,default_data,flag)
                self.StopResult[i].append(errorNum)
                if errorNum == 10:
                    self.grid.SetCellValue(m, 3, u'通过')
                else:
                    self.grid.SetCellValue(m, 3, 'Error%d'%(errorNum))
                m += 1
                
        self.stopState = 0       
    def OnTestStop(self, event):
        COM = self.serialSet['COM']
        if self.checkstatusOK()==0:
            return
        
        dlg = wx.MessageDialog(None, u'是否发送停止命令?',
                          u'停止修改测试', wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            if not Stop(self.ser,self.serialSet['Resend']):
                dlg1 = wx.MessageDialog(None, u'机器停止失败，是否继续测试?',
                          u'停止修改测试', wx.YES_NO | wx.ICON_QUESTION)
                result1 = dlg1.ShowModal()
                if result1 == wx.ID_NO:
                    return
            else:
                wx.MessageBox(u"机器停止成功", 
                    u"机器停止成功", wx.OK, self)
        self.stopState = 1
        self.stopTestThread = threading.Thread( target = self.stopTest, name = "stopTestThread" )
        self.stopTestThread.start()

    def runTest(self):
        self.RunResult = []
        m = 0
        n = self.grid.GetNumberRows()
        for i in range(n):
            self.grid.SetCellValue(i, 4, '  ')
        for i in range(len(self.Fgroup)):
            self.RunResult.append([])
            Fgroup = self.Fgroup[i]
            Fdata = self.Fdata[i]
            #检测出厂参数是否与说明书对应：
            for (address,min_data,max_data,default_data,flag) in Fdata:
                if self.runState == 0:
                    return
                errorNum = CheckMinMax_Run(self.ser,self.serialSet['Resend'],Fgroup,address,min_data,max_data,default_data,flag)
                self.RunResult[i].append(errorNum)
                if errorNum == 10:
                    self.grid.SetCellValue(m, 4, u'通过')
                else:
                    self.grid.SetCellValue(m, 4, 'Error%d'%(errorNum))
                m += 1
                
        self.runState = 0        
    def OnTestRun(self, event):
        COM = self.serialSet['COM']
        if self.checkstatusOK()==0:
            return 

        dlg = wx.MessageDialog(None, u'是否发送运行命令?',
                          u'运行修改测试', wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        
        if result == wx.ID_YES:
            if not Run(self.ser,self.serialSet['Resend']):
                dlg1 = wx.MessageDialog(None, u'机器运行失败，是否继续测试?',
                          u'运行修改测试', wx.YES_NO | wx.ICON_QUESTION)
                result1 = dlg1.ShowModal()
                if result1 == wx.ID_NO:
                    return
            else:
                wx.MessageBox(u"机器运行成功", 
                    u"机器运行成功", wx.OK, self)
                
        self.runState = 1
        self.runTestThread = threading.Thread( target = self.runTest, name = "runTestThread" )
        self.runTestThread.start()

    def OnEndTest(self, event):
        self.defaultState = 0
        self.stopState = 0
        self.runState = 0 
        if (self.defaultState+self.stopState+self.runState)==0:
            wx.MessageBox(u"成功终止", 
                u"终止!!!", wx.OK, self)
        
    def OnHelp(self, event):
        wx.MessageBox(u"Error:\
                        \n0 通讯失败\
                        \n1 CRC校验错误\
                        \n2 默认值错误\
                        \n3 停止中不可修改的参数在停止中被修改了. \
                        \n4 停止中可修改的参数停止中不能被修改.\
                        \n5 停止中可修改的参数修改超出了范围.\
                        \n6 运行中不可修改的参数在运行中被修改了. \
                        \n7 运行中可修改的参数运行中不能被修改.\
                        \n8 运行中可修改的参数修改超出了范围.", 
                u"帮助", wx.OK | wx.ICON_INFORMATION, self)
         
    def OnAbout(self, event):
        wx.MessageBox(u"测试部1818出品,汇川变频器专用。", 
                u"软件信息", wx.OK | wx.ICON_INFORMATION, self)
    def OnQuit(self, event):
        try:
            self.ser.close()
        except:
            pass
        self.Close()


        
        
    
                
if __name__ == '__main__':
    app = MyApp(False)
    app.MainLoop()
