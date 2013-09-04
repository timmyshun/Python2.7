#! /usr/bin/env python
#coding=utf-8
import os,math,time
import threading
import wx,wx.grid
import winsound

width = 400

class MyApp(wx.App):
    
    def OnInit(self):
       frame = MyFrame("June`s Time", (250, 250), (width, width*0.618))
       frame.Show()
       self.SetTopWindow(frame)
       return True
    
class MyFrame(wx.Frame):    
    def __init__(self, title, pos, size):
        wx.Frame.__init__(self, None, -1, title, pos, size)
        self.SetFont(wx.Font(15, wx.SWISS, wx.NORMAL, wx.BOLD, 0,'宋体'))
        self.__creatItems()      
        self.__doLayout()
        
        self.Alive = 1

        self.Status = 0        
        self.Hour = 0
        self.Minute = 0
        self.Second = 0
        self.Millisecond = 0
        self.sysTimeThread = threading.Thread(target = self.sysTime,name = 'sysTimeThread')
        self.sysTimeThread.start()
        self.beepThread = threading.Thread( target = self.beep, name = "beepThread" )
        self.beepThread.start()
        self.Bind(wx.EVT_CLOSE, self.OnClose, self)

      #  bmp = wx.Image(".\bitmap.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
      #  self.SetBackground(bmp)
        

    def __creatItems(self):
        self.TitleLbl = wx.StaticText(self, -1, u"Time Machine")
        self.TitleLbl.SetFont(wx.Font(24, wx.SWISS, wx.NORMAL, wx.BOLD,0,'Viner Hand ITC'))

        self.HourNum = wx.TextCtrl(self, -1, "00", size=(30,25))        
        self.HourLbl = wx.StaticText(self, -1, u"小时")
        self.HourLbl.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL,0,'幼圆'))
        self.MinuteNum = wx.TextCtrl(self, -1, "00", size=(30,25))
        self.MinuteLbl = wx.StaticText(self, -1, u"分钟")
        self.MinuteLbl.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL,0,'幼圆'))
        self.SecondNum = wx.TextCtrl(self, -1, "00", size=(30,25))
        self.SecondLbl = wx.StaticText(self, -1, u"秒")
        self.SecondLbl.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL,0,'幼圆'))
        self.MillisecondNum = wx.TextCtrl(self, -1, "000", size=(39,25))
        self.MillisecondLbl = wx.StaticText(self, -1, u"毫秒")
        self.MillisecondLbl.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL,0,'幼圆'))

        self.HourBeepCeckBox = wx.CheckBox(self, -1, u"时")
        self.HourBeepCeckBox.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL,0,'幼圆'))
        self.MinuteBeepCeckBox = wx.CheckBox(self, -1, u"分")
        self.MinuteBeepCeckBox.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL,0,'幼圆'))
        self.SecondBeepCeckBox = wx.CheckBox(self, -1, u"秒")
        self.SecondBeepCeckBox.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL,0,'幼圆'))
        self.CountBeepCeckBox = wx.CheckBox(self, -1, u"倒计时")
        self.CountBeepCeckBox.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL,0,'幼圆'))

        
        self.BeginButton = wx.Button(self, -1, u"开始")
        self.Bind(wx.EVT_BUTTON, self.OnBegin, self.BeginButton)
        self.BeginButton.SetMinSize((50,30))
        self.PauseButton = wx.Button(self, -1, u"暂停")
        self.Bind(wx.EVT_BUTTON, self.OnPause, self.PauseButton)
        self.PauseButton.Enable(False)
        self.PauseButton.SetMinSize((50,30))
        self.ResetButton = wx.Button(self, -1, u"置零")
        self.Bind(wx.EVT_BUTTON, self.OnReset, self.ResetButton)
        self.ResetButton.SetMinSize((50,30))
        self.CountdownButton = wx.Button(self, -1, u"倒计时")
        self.Bind(wx.EVT_BUTTON, self.OnCountdown, self.CountdownButton)
        self.CountdownButton.SetMinSize((70,30))
        self.CreateStatusBar()
        self.CountBeepCeckBox.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL,0,'宋体'))

        
    def __doLayout(self):
        MainSizer = wx.BoxSizer(wx.VERTICAL)
        
        TimeSizer = wx.GridSizer(1,10)
        TimeSizer.AddSpacer((20,20))
        TimeSizer.Add(self.HourNum, 0,wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL, 0)
        TimeSizer.Add(self.HourLbl, 0,wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TimeSizer.Add(self.MinuteNum, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        TimeSizer.Add(self.MinuteLbl, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TimeSizer.Add(self.SecondNum, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        TimeSizer.Add(self.SecondLbl, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        TimeSizer.Add(self.MillisecondNum, 0,wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        TimeSizer.Add(self.MillisecondLbl, 0,wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        CheckSizer = wx.GridSizer(1,5)
        CheckSizer.Add(self.HourBeepCeckBox, 0,wx.ALIGN_RIGHT|wx.ALIGN_TOP, 0)
        CheckSizer.Add(self.MinuteBeepCeckBox, 0,wx.ALIGN_RIGHT|wx.ALIGN_TOP, 0)
        CheckSizer.Add(self.SecondBeepCeckBox, 0, wx.ALIGN_RIGHT|wx.ALIGN_TOP, 0)
        CheckSizer.AddSpacer((20,20))
        CheckSizer.Add(self.CountBeepCeckBox, 0, wx.ALIGN_LEFT|wx.ALIGN_TOP, 0)
        

        ButtonSizer = wx.GridSizer(1,6)
        ButtonSizer.AddSpacer((20,20))
        ButtonSizer.Add(self.BeginButton,0,wx.ALIGN_CENTER_HORIZONTAL , 0)
        ButtonSizer.Add(self.PauseButton,0,wx.ALIGN_CENTER_HORIZONTAL , 0)
        ButtonSizer.Add(self.ResetButton,0,wx.ALIGN_CENTER_HORIZONTAL , 0)
        ButtonSizer.Add(self.CountdownButton,0,wx.ALIGN_CENTER_HORIZONTAL , 0)
        
        MainSizer.Add(self.TitleLbl, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)
        MainSizer.Add(TimeSizer, 1, wx.EXPAND, 0)
        MainSizer.Add(CheckSizer, 1, wx.EXPAND, 0)
        MainSizer.Add(ButtonSizer, 1, wx.EXPAND, 0)
        MainSizer.AddSpacer((width,width*0.618*0.2))
        
        self.SetSizer(MainSizer)
        self.Layout()
        
    def OnBegin(self,event):      
        if self.BeginButton.GetLabel() == u'开始':
            if self.Beginclockup() == 0:
                return 
            self.BeginButton.SetLabel(u'停止')
            self.PauseButton.Enable(True)
            self.ResetButton.Enable(False)
            self.CountdownButton.Enable(False)
            self.HourBeepCeckBox.Enable(False)
            self.MinuteBeepCeckBox.Enable(False)
            self.SecondBeepCeckBox.Enable(False)
            self.CountBeepCeckBox.Enable(False)
        elif self.BeginButton.GetLabel() == u'停止':
            self.Status = 0
            self.BeginButton.SetLabel(u'开始')
            self.PauseButton.SetLabel(u'暂停')
            self.PauseButton.Enable(False)
            self.ResetButton.Enable(True)
            self.CountdownButton.Enable(True)
            self.HourBeepCeckBox.Enable(True)
            self.MinuteBeepCeckBox.Enable(True)
            self.SecondBeepCeckBox.Enable(True)
            self.CountBeepCeckBox.Enable(True)
            time.sleep(0.2)
        
    def Beginclockup(self):
        try:            
            self.Hour = int(self.HourNum.GetValue())
            self.Minute =int(self.MinuteNum.GetValue())
            self.Second = int(self.SecondNum.GetValue())
            self.Millisecond = int(self.MillisecondNum.GetValue())
            self.__displaySet()
        except:
            wx.MessageBox(u"请输入正确的起始时间", 
                "Failure!!!", wx.OK, self)
            return 0
        if self.Minute >= 60:
             wx.MessageBox(u"分钟数应该小于60", 
                "Failure!!!", wx.OK, self)
             self.MinuteNum.SetValue('00')
             return 0
        elif self.Second >= 60:
             wx.MessageBox(u"秒数应该小于60", 
                "Failure!!!", wx.OK, self)
             self.SecondNum.SetValue('00')
             return 0
        elif self.Millisecond >= 1000:
             wx.MessageBox(u"毫秒数应该小于1000", 
                "Failure!!!", wx.OK, self)
             self.MillisecondNum.SetValue('000')
             return 0
        elif self.Hour >= 100:
             wx.MessageBox(u"只能显示到99小时", 
                "Failure!!!", wx.OK, self)
             self.HourNum.SetValue('00')
             return 0
        self.BeginTime =  time.time()
        self.Status = 2
        self.clockupThread= threading.Thread( target = self.clockup, name = "clockupThread" )
        self.clockupThread.start()
        
        return 1
        
        
        
    def OnPause(self,event):
        if self.PauseButton.GetLabel() == u'暂停':
            self.Status = 1
            self.PauseButton.SetLabel(u'继续')
            time.sleep(0.1)
        elif self.PauseButton.GetLabel() == u'继续':
            self.Status = 2
            self.PauseButton.SetLabel(u'暂停')
            time.sleep(0.1)
            
    def OnReset(self,event):
        if self.Status == 0:
            self.Millisecond = 0
            self.Second = 0
            self.Minute = 0
            self.Hour = 0
            self.HourNum.SetValue('00')
            self.MinuteNum.SetValue('00')
            self.SecondNum.SetValue('00')
            self.MillisecondNum.SetValue('000')
    def OnCountdown(self,event):
        if self.CountdownButton.GetLabel() == u'倒计时':
            if self.Beginclockdown() == 0:
                return 
            self.CountdownButton.SetLabel(u'终止')
            self.PauseButton.Enable(False)
            self.ResetButton.Enable(False)
            self.BeginButton.Enable(False)
            self.HourBeepCeckBox.Enable(False)
            self.MinuteBeepCeckBox.Enable(False)
            self.SecondBeepCeckBox.Enable(False)
            self.CountBeepCeckBox.Enable(False) 
        elif self.CountdownButton.GetLabel() == u'终止':
            self.Status = 0
            self.CountdownButton.SetLabel(u'倒计时')
            self.PauseButton.Enable(False)
            self.ResetButton.Enable(True)
            self.BeginButton.Enable(True) 
            self.CountdownButton.Enable(True)
            self.HourBeepCeckBox.Enable(True)
            self.MinuteBeepCeckBox.Enable(True)
            self.SecondBeepCeckBox.Enable(True)
            self.CountBeepCeckBox.Enable(True)
            
    def Beginclockdown(self):
        try:            
            self.Hour = int(self.HourNum.GetValue())
            self.Minute =int(self.MinuteNum.GetValue())
            self.Second = int(self.SecondNum.GetValue())
            self.Millisecond = int(self.MillisecondNum.GetValue())
            self.__displaySet()
        except:
            wx.MessageBox(u"请输入正确的起始时间", 
                "Failure!!!", wx.OK, self)
            return 0
        if self.Minute >= 60:
             wx.MessageBox(u"分钟数应该小于60", 
                "Failure!!!", wx.OK, self)
             self.MinuteNum.SetValue('00')
             return 0
        elif self.Second >= 60:
             wx.MessageBox(u"秒数应该小于60", 
                "Failure!!!", wx.OK, self)
             self.SecondNum.SetValue('00')
             return 0
        elif self.Millisecond >= 1000:
             wx.MessageBox(u"毫秒数应该小于1000", 
                "Failure!!!", wx.OK, self)
             self.MillisecondNum.SetValue('000')
             return 0
        elif self.Hour >= 100:
             wx.MessageBox(u"只能显示到99小时", 
                "Failure!!!", wx.OK, self)
             self.HourNum.SetValue('00')
             return 0
        self.BeginTime =  time.time()
        self.Status = 2
        self.clockdownThread= threading.Thread( target = self.clockdown, name = "clockdownThread" )
        self.clockdownThread.start()
        return 1
        
    def clockup(self):
        pauseNum = 0
        while(self.Status > 0):
            self.CurrentTime = time.time()
            if self.Status == 2:
                clockNum = self.CurrentTime - self.BeginTime-pauseNum
                self.Millisecond = int((clockNum*1000)%1000)
                self.Second = int(clockNum%60)
                self.Minute = int(clockNum/60%60)
                self.Hour = int(clockNum/3600%60)
                self.__displaySet()
            elif self.Status == 1:
                pauseNum = self.CurrentTime - self.BeginTime-clockNum
    def clockdown(self):
        downNum = self.Millisecond + self.Second*1000 + self.Minute*1000*60 + self.Hour*1000*60*60        
        while(self.Status > 0):
            self.CurrentTime = time.time()
            passNum = self.CurrentTime - self.BeginTime
            clockNum = float(downNum)/1000.0 - passNum
            if clockNum < 0.001:                
                self.OnCountdown(wx.EVT_BUTTON)
                self.OnReset(wx.EVT_BUTTON)
                if self.CountBeepCeckBox.GetValue():
                    winsound.Beep(1024, 200)
                break
            self.Millisecond = int((clockNum*1000)%1000)
            self.Second = int(clockNum%60)
            self.Minute = int(clockNum/60%60)
            self.Hour = int(clockNum/3600%60)
            self.__displaySet()
            
    def beep(self):
        while(self.Alive):
            if self.Status == 2:
                if self.SecondBeepCeckBox.GetValue() and self.Millisecond == 0:
                    winsound.Beep(1024, 100)
                if self.MinuteBeepCeckBox.GetValue() and self.Millisecond == 0 and self.Second ==0:
                    winsound.Beep(1024, 100)
                if self.HourBeepCeckBox.GetValue() and self.Millisecond == 0 and self.Second ==0 and self.Minute ==0:
                    winsound.Beep(1024, 100)
                    
    def __displaySet(self,Hour=0,Minute=0,Second=0,Millisecond=0):
        def str0(num,lenth):
            string = str(num)
            if len(string) < lenth:
                string = '0'*(lenth-len(string)) +string
            return string
        self.HourNum.SetValue(str0(self.Hour-Hour,2))
        self.MinuteNum.SetValue(str0(self.Minute-Minute,2))
        self.SecondNum.SetValue(str0(self.Second-Second,2))
        self.MillisecondNum.SetValue(str0(self.Millisecond-Millisecond,3))
    def sysTime(self):
        self.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL,0,'幼圆'))
        while self.Alive:
            timestr = time.strftime("%Y %b %d %H:%M:%S", time.localtime())
            self.SetStatusText(timestr)
            time.sleep(0.2)
    def OnClose(self, event):
        """Event handler for closing."""
        self.StopThreads()
        self.Destroy()
    def StopThreads(self):
        self.Alive  = 0
        time.sleep(0.5)
        while(threading.activeCount()>3):
            print threading.activeCount()
            time.sleep(0.5)
    def ThreadFinished(self, thread):
        self.threads.remove(thread)
        self.UpdateCount()
            
            
if __name__ == '__main__':
    app = MyApp(False)
    app.MainLoop()
