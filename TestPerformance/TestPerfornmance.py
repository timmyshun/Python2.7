#! /usr/bin/env python
#coding=utf-8
import os,math,time,math
import threading
import wx,wx.grid
import serial
from InterfaceFunc import *
from COM_MODBUS_Func import *
from DataExchange import *
from Data_Func import *

width = 600

class MyApp(wx.App):
    
    def OnInit(self):
       frame = MyFrame(u"测试辅助软件", (50, 60), (width, width*0.618))
       frame.Show()
       self.SetTopWindow(frame)
       return True
    
class MyFrame(wx.Frame):
    
    def __init__(self, title, pos, size):
        wx.Frame.__init__(self, None, -1, title, pos, size)
        self.CreateMenuBar()                
        
        self.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD, 0,'宋体'))
        self.__creatItems()      
        self.__doLayout()

        
        self.serialSet = {'COM':0,'Baudrate':9600,'Bytesize':8,'Parity':'N',\
                          'Stopbits':2,'Timeout':0.05,'Resend':2}

        self.Speed = 5000
        self.Speedup = 20
        self.Speeddown = 20
        self.RunP = 0
        self.Frequent = 60

        self.KeepRunFlag = 0

                       
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
        return [
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
                (u"&O帮助和退出",(
                    (u"帮助","",self.OnHelp),
                    (u"关于..","",self.OnAbout),
                    ("", "", ""),
                    (u"退出","",self.OnQuit),
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

        
    def OnHelp(self, event):
        wx.MessageBox(u"Error:\
                        \n0 通讯失败\
                        \n1 CRC校验错误", 
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

    def __creatItems(self):
        self.TitleLbl = wx.StaticText(self, -1, u"测试辅助软件")
        self.TitleLbl.SetFont(wx.Font(24, wx.SWISS, wx.NORMAL, wx.BOLD,0,'宋体'))

        
        self.SpeedNum = wx.TextCtrl(self, -1, "50.00", size=(50,15))
        self.SpeedLbl = wx.StaticText(self, -1, u"Hz")

        self.SpeedupLbl = wx.StaticText(self, -1, u"上升时间")
        self.SpeedupNum = wx.TextCtrl(self, -1, "20.0", size=(40,15))
        
        self.SpeeddownLbl = wx.StaticText(self, -1, u"减速时间")
        self.SpeeddownNum = wx.TextCtrl(self, -1, "20.0", size=(40,15))

        self.RunPLbl = wx.StaticText(self, -1, u"转向")
        self.RunPButton = wx.Button(self, -1, "+")
        self.Bind(wx.EVT_BUTTON, self.OnRunP, self.RunPButton)
        self.RunPButton.SetMinSize((20,20))

        self.FrequentLbl = wx.StaticText(self, -1, u"载频")
        self.FrequentNum = wx.TextCtrl(self, -1, "06.0", size=(40,15))

        self.UserLbl11 = wx.StaticText(self, -1, u"定义参数1")
        self.UserNum11 = wx.TextCtrl(self, -1, "", size=(23,15))
        self.UserNum12 = wx.TextCtrl(self, -1, "", size=(23,15))
        self.UserLbl12 = wx.StaticText(self, -1, u"--")
        self.UserNum13 = wx.TextCtrl(self, -1, "", size=(38,15))

        self.UserLbl21 = wx.StaticText(self, -1, u"参数2")
        self.UserNum21 = wx.TextCtrl(self, -1, "", size=(23,15))
        self.UserNum22 = wx.TextCtrl(self, -1, "", size=(23,15))
        self.UserLbl22 = wx.StaticText(self, -1, u"--")
        self.UserNum23 = wx.TextCtrl(self, -1, "", size=(38,15))

        self.UserLbl31 = wx.StaticText(self, -1, u"参数3")
        self.UserNum31 = wx.TextCtrl(self, -1, "", size=(23,15))
        self.UserNum32 = wx.TextCtrl(self, -1, "", size=(23,15))
        self.UserLbl32 = wx.StaticText(self, -1, u"--")
        self.UserNum33 = wx.TextCtrl(self, -1, "", size=(38,15))

        self.ClearButton = wx.Button(self, -1, u"清空")
        self.Bind(wx.EVT_BUTTON, self.OnClear, self.ClearButton)
        self.ClearButton.SetMinSize((65,20))
        self.SetButton = wx.Button(self, -1, u"设置参数")
        self.Bind(wx.EVT_BUTTON, self.OnSet, self.SetButton)
        self.SetButton.SetMinSize((65,20))
        self.RunButton = wx.Button(self, -1, u"运行")
        self.Bind(wx.EVT_BUTTON, self.OnRun, self.RunButton)
        self.RunButton.SetMinSize((40,20))
        self.StopButton = wx.Button(self, -1, u"减速停机")
        self.Bind(wx.EVT_BUTTON, self.OnStop, self.StopButton)
        self.StopButton.SetMinSize((65,20))
        self.FreeStopButton = wx.Button(self, -1, u"自由停机")
        self.Bind(wx.EVT_BUTTON, self.OnFreeStop, self.FreeStopButton)
        self.FreeStopButton.SetMinSize((65,20))

        self.KeepRunButton = wx.Button(self, -1, u"不断运行")
        self.Bind(wx.EVT_BUTTON, self.OnKeepRun, self.KeepRunButton)
        self.KeepRunButton.SetMinSize((65,20))
        
        self.CreateStatusBar()

        self.TestLbl11 = wx.StaticText(self, -1, u"测量参数")
        self.TestNum11 = wx.TextCtrl(self, -1, "10", size=(23,15))
        self.TestNum12 = wx.TextCtrl(self, -1, "02", size=(23,15))
        self.TestLbl12 = wx.StaticText(self, -1, u"测量次数")
        self.TestNum14 = wx.TextCtrl(self, -1, "100", size=(38,15))
        self.TestLbl13 = wx.StaticText(self, -1, u"测量间隔(ms)")
        self.TestNum15 = wx.TextCtrl(self, -1, "3", size=(38,15))

        self.TestLbl14 = wx.StaticText(self, -1, u"平均值")
        self.TestNum16 = wx.TextCtrl(self, -1, "", size=(45,15))
        self.TestLbl15 = wx.StaticText(self, -1, u"峰峰值")
        self.TestNum17 = wx.TextCtrl(self, -1, "", size=(45,15))
        self.TestLbl16 = wx.StaticText(self, -1, u"最大值")
        self.TestNum18 = wx.TextCtrl(self, -1, "", size=(45,15))
        self.TestLbl17 = wx.StaticText(self, -1, u"最小值")
        self.TestNum19 = wx.TextCtrl(self, -1, "", size=(45,15))

        self.TestLbl18 = wx.StaticText(self, -1, u"方差")
        self.TestNum20 = wx.TextCtrl(self, -1, "", size=(45,15))
        self.TestLbl19 = wx.StaticText(self, -1, u"标准差")
        self.TestNum21 = wx.TextCtrl(self, -1, "", size=(45,15))
        self.TestLbl20 = wx.StaticText(self, -1, u"均方根")
        self.TestNum22 = wx.TextCtrl(self, -1, "", size=(65,15))
        self.TestButton = wx.Button(self, -1, u"测试数据")
        self.Bind(wx.EVT_BUTTON, self.OnTest, self.TestButton)
        self.TestButton.SetMinSize((65,20))

        


    def __doLayout(self):
        MainSizer = wx.BoxSizer(wx.VERTICAL)
        
        SetSizer = wx.GridSizer(1,15)
        SetSizer.AddSpacer((1,10))
        SetSizer.Add(self.SpeedNum, 0,wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL, 0)
        SetSizer.Add(self.SpeedLbl, 0,wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        SetSizer.Add(self.SpeedupLbl, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        SetSizer.Add(self.SpeedupNum, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        SetSizer.AddSpacer((1,10))
        SetSizer.Add(self.SpeeddownLbl, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        SetSizer.Add(self.SpeeddownNum, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        SetSizer.Add(self.RunPLbl, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        SetSizer.Add(self.RunPButton, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        SetSizer.Add(self.FrequentLbl, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        SetSizer.Add(self.FrequentNum, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        

        UserSizer = wx.GridSizer(1,18)
        UserSizer.AddSpacer((1,10))
        UserSizer.Add(self.UserLbl11, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        UserSizer.Add(self.UserNum11, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        UserSizer.Add(self.UserNum12, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        UserSizer.Add(self.UserLbl12, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        UserSizer.Add(self.UserNum13, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        UserSizer.AddSpacer((1,10))
        UserSizer.Add(self.UserLbl21, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        UserSizer.Add(self.UserNum21, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        UserSizer.Add(self.UserNum22, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        UserSizer.Add(self.UserLbl22, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        UserSizer.Add(self.UserNum23, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        UserSizer.AddSpacer((1,10))
        UserSizer.Add(self.UserLbl31, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        UserSizer.Add(self.UserNum31, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        UserSizer.Add(self.UserNum32, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        UserSizer.Add(self.UserLbl32, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        UserSizer.Add(self.UserNum33, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        ButtonSizer = wx.GridSizer(1,8)
        ButtonSizer.AddSpacer((10,10))
        ButtonSizer.Add(self.ClearButton,0,wx.ALIGN_CENTER_HORIZONTAL , 0)
        ButtonSizer.Add(self.SetButton,0,wx.ALIGN_CENTER_HORIZONTAL , 0)
        ButtonSizer.Add(self.RunButton,0,wx.ALIGN_CENTER_HORIZONTAL , 0)
        ButtonSizer.Add(self.StopButton,0,wx.ALIGN_CENTER_HORIZONTAL , 0)
        ButtonSizer.Add(self.FreeStopButton,0,wx.ALIGN_CENTER_HORIZONTAL , 0)
        ButtonSizer.Add(self.KeepRunButton,0,wx.ALIGN_CENTER_HORIZONTAL , 0)
        
        TestSizer1 = wx.GridSizer(1,13)
        TestSizer1.AddSpacer((1,10))
        TestSizer1.AddSpacer((1,10))
        TestSizer1.Add(self.TestLbl11, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        TestSizer1.Add(self.TestNum11, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TestSizer1.Add(self.TestNum12, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TestSizer1.Add(self.TestLbl12, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TestSizer1.AddSpacer((1,10))
        TestSizer1.Add(self.TestNum14, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TestSizer1.Add(self.TestLbl13, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TestSizer1.AddSpacer((1,10))
        TestSizer1.Add(self.TestNum15, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        TestSizer2 = wx.GridSizer(1,10)
        TestSizer2.AddSpacer((1,10))
        TestSizer2.Add(self.TestLbl14, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TestSizer2.Add(self.TestNum16, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TestSizer2.Add(self.TestLbl15, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TestSizer2.Add(self.TestNum17, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TestSizer2.Add(self.TestLbl16, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TestSizer2.Add(self.TestNum18, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TestSizer2.Add(self.TestLbl17, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TestSizer2.Add(self.TestNum19, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        TestSizer3 = wx.GridSizer(1,10)
        TestSizer3.AddSpacer((1,10))
        TestSizer3.Add(self.TestLbl18, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TestSizer3.Add(self.TestNum20, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TestSizer3.Add(self.TestLbl19, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TestSizer3.Add(self.TestNum21, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TestSizer3.Add(self.TestLbl20, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TestSizer3.Add(self.TestNum22, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TestSizer3.AddSpacer((1,10))
        TestSizer3.Add(self.TestButton, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        
        MainSizer.Add(self.TitleLbl, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)
        MainSizer.Add(SetSizer, 1, wx.EXPAND, 0)
        MainSizer.Add(UserSizer, 1, wx.EXPAND, 0)
        MainSizer.Add(ButtonSizer, 1, wx.EXPAND, 0)
        MainSizer.AddSpacer((width,width*0.618*0.1))
        MainSizer.Add(TestSizer1, 1, wx.EXPAND, 0)
        MainSizer.Add(TestSizer2, 1, wx.EXPAND, 0)
        MainSizer.Add(TestSizer3, 1, wx.EXPAND, 0)
        MainSizer.AddSpacer((width,width*0.618*0.1))
        
        self.SetSizer(MainSizer)
        self.Layout()

    def OnRunP(self, event):
        if self.RunPButton.GetLabel()== "+":
            self.RunPButton.SetLabel("-")
            self.RunP = 1
            SetParameter(self.ser,1,0xF0,0x09,self.RunP)
        elif self.RunPButton.GetLabel() == "-":
            self.RunPButton.SetLabel("+")
            self.RunP = 0
            SetParameter(self.ser,1,0xF0,0x09,self.RunP)
    def OnClear(self, event):
        self.UserNum11.SetValue("")
        self.UserNum12.SetValue("")
        self.UserNum13.SetValue("")
        self.UserNum21.SetValue("")
        self.UserNum22.SetValue("")
        self.UserNum23.SetValue("")
        self.UserNum31.SetValue("")
        self.UserNum32.SetValue("")
        self.UserNum33.SetValue("")
    def OnSet(self, event):
        try:            
            self.Speed = int(float(self.SpeedNum.GetValue())*100)
            self.Speedup = int(float(self.SpeedupNum.GetValue())*10)
            self.Speeddown = int(float(self.SpeeddownNum.GetValue())*10)
            self.Frequent = int(float(self.FrequentNum.GetValue())*10)
        except:
            wx.MessageBox(u"请输入正确的参数", 
                "Failure!!!", wx.OK, self)
            return 0
        ErrorNum = 0
        try:
            ErrorNum += SetParameter(self.ser,1,0xF0,0x08,self.Speed)
            ErrorNum += SetParameter(self.ser,1,0xF0,0x11,self.Speedup)
            ErrorNum += SetParameter(self.ser,1,0xF0,0x12,self.Speeddown)
            ErrorNum += SetParameter(self.ser,1,0xF0,0x09,self.RunP)
            ErrorNum += SetParameter(self.ser,1,0xF0,0x0F,self.Frequent)
        except:
            wx.MessageBox(u"设置参数失败，请检查通讯及设置参数是否正确。", 
                u"失败", wx.OK, self)
            return 0
        if ErrorNum == 0:
            pass
        else:
            wx.MessageBox(u"设置参数失败，请检查通讯及设置参数是否正确。", 
                u"失败", wx.OK, self)

        try:
            if len(self.UserNum11.GetValue()) ==0 or\
               len(self.UserNum12.GetValue()) ==0 or\
               len(self.UserNum13.GetValue()) ==0:
                pass
            else:
                UserHighAdd1 = StrH2Num( self.UserNum11.GetValue())
                UserLowAdd1 = StrD2Num( self.UserNum12.GetValue())
                Userdata1 = StrD2Num( self.UserNum13.GetValue())
                SetParameter(self.ser,1,UserHighAdd1,UserLowAdd1,Userdata1)
        except:
            wx.MessageBox(u"自定义设置参数1失败，设置参数是否正确。", 
                u"失败", wx.OK, self)
        try:
            if len(self.UserNum21.GetValue()) ==0 or\
               len(self.UserNum22.GetValue()) ==0 or\
               len(self.UserNum23.GetValue()) ==0:
                pass
            else:
                UserHighAdd2 = StrH2Num( self.UserNum21.GetValue())
                UserLowAdd2 = StrD2Num( self.UserNum22.GetValue())
                Userdata2 = StrD2Num( self.UserNum23.GetValue())
                SetParameter(self.ser,1,UserHighAdd2,UserLowAdd2,Userdata2)
        except:
            wx.MessageBox(u"自定义设置参数2失败，设置参数是否正确。", 
                u"失败", wx.OK, self)
        try:
            if len(self.UserNum31.GetValue()) ==0 or\
               len(self.UserNum32.GetValue()) ==0 or\
               len(self.UserNum33.GetValue()) ==0:
                pass
            else:
                UserHighAdd3 = StrH2Num( self.UserNum31.GetValue())
                UserLowAdd3 = StrD2Num( self.UserNum32.GetValue())
                Userdata3 = StrD2Num( self.UserNum33.GetValue())
                SetParameter(self.ser,1,UserHighAdd3,UserLowAdd3,Userdata3)
        except:
            wx.MessageBox(u"自定义设置参数3失败，设置参数是否正确。", 
                u"失败", wx.OK, self)
            
    def OnRun(self, event):
        SetParameter(self.ser,1,0xF0,0x02,2)
        Run(self.ser,self.serialSet['Resend'])
        
    def OnStop(self, event):
        Stop(self.ser,self.serialSet['Resend'])
        SetParameter(self.ser,1,0xF0,0x02,0)
    def OnFreeStop(self, event):
        FreeStop(self.ser,self.serialSet['Resend'])
        SetParameter(self.ser,1,0xF0,0x02,0)
    def OnKeepRun(self, event):
        self.KeepRunThread= threading.Thread( \
            target = self.KeepRun, name = "KeepRun" )
        
        if self.KeepRunFlag == 0:
            self.KeepRunFlag = 1
            self.KeepRunThread.start()
        elif self.KeepRunFlag == 1:
            self.KeepRunFlag = 0
            self.KeepRunButton.SetLabel(u'不断运行')
            time.sleep(0.2)
    def KeepRun(self):
        self.KeepRunButton.SetLabel(u'停止运行')

        while(self.KeepRunFlag == 1):
            SetParameter(self.ser,1,0xF0,0x02,2)
            Run(self.ser,self.serialSet['Resend'])
            time.sleep(0.1)
        

    def OnTest(self, event):
        self.TestThread= threading.Thread( \
            target = self.Test, name = "Test" )
        self.TestThread.start()
    def Test(self):
        self.TestButton.SetLabel(u'测试中..')
        self.TestButton.Enable(False)
        self.TestNum16.SetValue('')
        self.TestNum17.SetValue('')
        self.TestNum18.SetValue('')
        self.TestNum19.SetValue('')
        self.TestNum20.SetValue('')
        self.TestNum21.SetValue('')
        self.TestNum22.SetValue('')
        try:
            TestHighAdd = StrH2Num( self.TestNum11.GetValue())
            TestLowAdd = StrD2Num( self.TestNum12.GetValue())
            TestTime = StrD2Num( self.TestNum14.GetValue())
            TestInternal = StrD2Num( self.TestNum15.GetValue())
        except:
            wx.MessageBox(u"设置参数是否正确。", 
                u"失败", wx.OK, self)
            self.TestButton.SetLabel(u'测试数据')
            self.TestButton.Enable(True)
            return 

        try:
            (average,maxdata,peakPeak,variance,avvariance) =\
                DataAnysis(self.ser,1,TestHighAdd,TestLowAdd,TestTime,TestInternal,True)
        except:
            wx.MessageBox(u"参数是否正确,通讯是否正常", 
                u"失败", wx.OK, self)
            self.TestButton.SetLabel(u'测试数据')
            self.TestButton.Enable(True)
            return

        self.TestNum16.SetValue('%s'%average)
        self.TestNum17.SetValue('%s'%peakPeak)
        self.TestNum18.SetValue('%s'%maxdata)
        self.TestNum19.SetValue('%s'%(maxdata-peakPeak))
        self.TestNum20.SetValue('%s'%variance)
        self.TestNum21.SetValue('%s'%math.sqrt(variance))
        self.TestNum22.SetValue('%s'%avvariance)
        self.TestButton.SetLabel(u'测试数据')
        self.TestButton.Enable(True)
    
                
if __name__ == '__main__':
    app = MyApp(False)
    app.MainLoop()
