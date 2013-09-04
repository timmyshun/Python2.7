#! /usr/bin/env python
#coding=utf-8
import os,math,time,math
import threading
import wx,wx.grid
from multiprocessing import process



import Url

width = 600

class MyApp(wx.App):
    
    def OnInit(self):
       mm=wx.DisplaySize()
       frame = MyFrame(u"爱问不问搜索器", (mm[0]/4, mm[1]/4), (width, width*0.618))
       frame.Show()
       self.SetTopWindow(frame)
       return True
    
class MyFrame(wx.Frame):
    SearchName = []
    SearchCent = []
    SearchSize = []
    SelectedSearch = []
    isharehtmls = []

    path = ".\download"
    
    def __init__(self, title, pos, size):
        wx.Frame.__init__(self, None, -1, title, pos, size)

        self.CreateMenuBar()                
        
        self.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD, 0,'幼圆'))
        self.creatItems()      
        self.doLayout()
        self.DownButton.Enable(False)
        self.UpButton.Enable(False)
        self.SetStatusText(u"~~搜索文档~~")
        self.i = 0



        
    #建立菜单栏
    def menuData(self):
        return [
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
 

    def OnHelp(self, event):
        wx.MessageBox(u"我才懒得帮你。",
                u"帮助", wx.OK | wx.ICON_INFORMATION, self)
        
    def OnAbout(self, event):
        wx.MessageBox(u"1818出品。", 
                u"软件信息", wx.OK | wx.ICON_INFORMATION, self)
    def OnQuit(self, event):
        self.Close()

    def creatItems(self):
        #建立列表框标签
        self.NameLabel = wx.StaticText(self, -1, u"文件名")
        self.CentLabel = wx.StaticText(self, -1, u"分数")
        self.SizeLabel = wx.StaticText(self, -1, u"大小")
        #搜索文件名列表框
        self.NameListBox = wx.ListBox(self, -1, (20, 20), (width*0.618*0.53 , width*0.618*0.73),
                                               self.SearchName, wx.LB_MULTIPLE)
        self.Bind(wx.EVT_LISTBOX,self.SelectName,self.NameListBox)

        #搜索文件分列表框
        self.CentListBox = wx.ListBox(self, -1, (230, 20), (width*0.05 , width*0.618*0.73),
                                               self.SearchCent, wx.LB_MULTIPLE)
        self.Bind(wx.EVT_LISTBOX,self.SelectName,self.CentListBox)
        #搜索文件大小列表框
        self.SizeListBox = wx.ListBox(self, -1, (275, 20), (width*0.1 , width*0.618*0.73),
                                               self.SearchSize, wx.LB_MULTIPLE)
        self.Bind(wx.EVT_LISTBOX,self.SelectName,self.SizeListBox)

               
        #搜索设置
        self.SearchButton = wx.Button(self, -1, u"搜索")
        self.Bind(wx.EVT_BUTTON, self.Search, self.SearchButton)
        self.SearchButton.SetMinSize((65,22))
        self.SearchText = wx.TextCtrl(self, -1, "", size=(225,17))
        self.choiceFiletype = [u"全部","pdf","doc","txt","rar"]
        self.FiletypeChoice = wx.Choice(self, -1, (40, 15),choices=self.choiceFiletype)
        self.FiletypeChoice.SetSelection(0)
        #翻页按钮
        self.DownButton = wx.Button(self, -1, u"下一页")
        self.Bind(wx.EVT_BUTTON, self.OnDown, self.DownButton)
        self.DownButton.SetMinSize((65,20))
        self.UpButton = wx.Button(self, -1, u"上一页")
        self.Bind(wx.EVT_BUTTON, self.OnUp, self.UpButton)
        self.UpButton.SetMinSize((65,20))

        #下载按钮
        self.DownLoadButton = wx.Button(self, -1, u"下载")
        self.Bind(wx.EVT_BUTTON, self.OnDownLoad, self.DownLoadButton)
        self.DownLoadButton.SetMinSize((65,20))

        #下载路径设置
        self.PathLabel = wx.StaticText(self, -1, u"下载路径")
        self.PathText = wx.TextCtrl(self, -1, self.path, size=(225,20))
        self.PathButton = wx.Button(self, -1, u"路径...")
        self.PathButton.SetMinSize((65,20))
        self.Bind(wx.EVT_BUTTON, self.OnSelectPath, self.PathButton)
        self.CreateStatusBar()
        
    def SelectName(self, event):
        Selected = self.NameListBox.GetSelections()
        forname = self.CentListBox.GetSelections()
        forsize = self.SizeListBox.GetSelections()
        #先取消其他选择框的选项再重新根据文件名
        for i in forname:
            self.CentListBox.SetSelection(i,False)
        for i in forsize:
            self.SizeListBox.SetSelection(i,False)
        for i in Selected:
            self.CentListBox.SetSelection(i)
            self.SizeListBox.SetSelection(i)
    def SelectCent(self, event):
        pass
    def Search(self, event):
        self.SearchButton.Enable(False)
        self.UpButton.Enable(False)
        self.DownButton.Enable(False)
        self.pageNum = 0
        self.isharehtmls = []
        self.searchThread= threading.Thread( target = self.GetSearchPage, name = "SearchThread" )
        self.searchThread.start()
        self.dialog = wx.ProgressDialog(u"搜索进度",u"已经开始搜索文档",
                                            20,
                                            style=wx.PD_ELAPSED_TIME)
        while(self.searchThread.isAlive()):
            wx.MilliSleep(250)
            self.dialog.Update(self.i,u"~~搜索到"+str(self.i)+u"个文档~~")
        self.dialog.Destroy()
        
    def GetSearchPage(self):
        self.SetStatusText(u"~~已经开始搜索~~")
        self.i=0
        #获取搜索信息
        n = self.pageNum
        keyWord = self.SearchText.GetValue()
        fileType = self.choiceFiletype[self.FiletypeChoice.GetSelection()]
        if fileType == u"全部":
            fileType ="" #全部等于无约束
        #检测是否有搜索信息
        if len(keyWord)>0:
            #清除List框和对于的数组
            self.NameListBox.Clear()
            self.CentListBox.Clear()
            self.SizeListBox.Clear()
            self.SearchName=[]
            self.SearchCent=[]
            self.SearchSize=[]
            #缓存不够则增加缓存数组
            if len(self.isharehtmls)<n+1:
                self.isharehtmls.append([])
            #如果页面已然存在就直接调用
            if len(self.isharehtmls[n])>0 :
                for ihtml in self.isharehtmls[n]:
                    self.SearchName.append(ihtml.fileName)#获取函数在获取一次后就直接调用不重复获取
                    self.SearchCent.append(ihtml.fileCent)
                    self.SearchSize.append(ihtml.fileSize)
                #调用完毕后设置ListBox和按钮
                self.SetListBox(n)
                return
            #页面不存在先清楚原页面信息
            self.isharehtmls[n] = []
            #获取搜索页面
            url,searchhtml = Url.GetSearchHtml("baidu","ishare.iask.sina.com.cn",keyWord,fileType,n)
            
            #解析搜索页面获得文件页面
            urls = Url.GetFileUrls(searchhtml)

            #解析文件页面
            for ur in urls:
                html=Url.downloadhtml(ur)
                isharehtml = Url.IshareHtml(html)
                if(isharehtml.fileCent!=""):
                    self.i+=1
                    self.isharehtmls[n].append(isharehtml)
                    self.SearchName.append(isharehtml.fileName)
                    self.SearchCent.append(isharehtml.fileCent)
                    self.SearchSize.append(isharehtml.fileSize)
                    self.SetStatusText(u"~~搜索到"+str(self.i)+u"个文档~~")
        #完毕后设置ListBox和按钮
        self.SetListBox(n)
        self.SetStatusText(u"~~搜索结束~~"+u"~~搜索到"+str(self.i)+u"个文档~~")
        self.i = 0

    def SetListBox(self,n):
        self.NameListBox.InsertItems(self.SearchName, 0)
        self.CentListBox.InsertItems(self.SearchCent, 0)
        self.SizeListBox.InsertItems(self.SearchSize, 0)
        if n > 0:
            self.UpButton.Enable(True)
        else:
            self.UpButton.Enable(False)
        self.DownButton.Enable(True)
        self.SearchButton.Enable(True)
        
        
    def OnDown(self, event):
        self.SearchButton.Enable(False)
        self.UpButton.Enable(False)
        self.DownButton.Enable(False)     
        self.pageNum += 1
        self.downThread= threading.Thread( target = self.GetSearchPage, name = "downThread" )
        self.downThread.start()
        self.dialog = wx.ProgressDialog(u"搜索进度",u"已经开始搜索文档",
                                            20,
                                            style=wx.PD_ELAPSED_TIME)
        while(self.downThread.isAlive()):
            wx.MilliSleep(250)
            self.dialog.Update(self.i,u"~~搜索到"+str(self.i)+u"个文档~~")
        self.dialog.Destroy()
    def OnUp(self, event):  
        if self.pageNum >=1:
            self.pageNum -= 1
        else:
            return
        self.SearchButton.Enable(False)
        self.DownButton.Enable(False)
        self.UpButton.Enable(False)
        self.GetSearchPage()
    def OnDownLoad(self, event):
        selectedIsharehtmls = []
        unDownLoad = []
        for i in self.NameListBox.GetSelections():
            selectedIsharehtmls.append(self.isharehtmls[self.pageNum][i])
        for ishare in selectedIsharehtmls:
            if len(ishare.phoneDownLoadURL)>0:
                html=Url.downloadhtml(ishare.phoneDownLoadURL)
                phonedownload = Url.IsharePhoneHtml(html)
                phonedownload.PhoneDownLoadIE()
            else:
                unDownLoad.append(ishare)
        unDownladFileName = ""
        for unDown in unDownLoad:
            unDownladFileName = unDownladFileName+unDown.fileName+"\n"
        wx.MessageBox(unDownladFileName,
                u"未下载的文件", wx.OK | wx.ICON_INFORMATION, self)
            
            
        
    def OnSelectPath(self, event):
        dialog = wx.DirDialog(None, u'选择下载路径',os.getcwd(), 0,
                              wx.DefaultPosition, wx.DefaultSize)
        result = dialog.ShowModal()
        if result == 5100:
            self.path = dialog.GetPath()
            self.PathText .SetValue(self.path)
        dialog.Destroy()

    def doLayout(self):
        MainSizer = wx.BoxSizer(wx.VERTICAL)

        LabelSizer = wx.GridSizer(1,6)
        LabelSizer.Add(self.NameLabel,0,wx.ALIGN_CENTER_HORIZONTAL , 0)
        LabelSizer.AddSpacer((20,20))
        LabelSizer.Add(self.CentLabel,0,wx.ALIGN_CENTER_HORIZONTAL , 0)
        LabelSizer.Add(self.SizeLabel,0,wx.ALIGN_LEFT , 0)

        SearchSizer = wx.GridSizer(2,5)
        SearchSizer.AddSpacer((20,20))
        SearchSizer.AddSpacer((20,20))
        SearchSizer.AddSpacer((20,20))
        SearchSizer.Add(self.SearchText,0,wx.ALIGN_LEFT , 0)
        SearchSizer.AddSpacer((20,20))
        SearchSizer.AddSpacer((20,20))
        SearchSizer.AddSpacer((20,20))
        SearchSizer.AddSpacer((20,20))
        SearchSizer.Add(self.FiletypeChoice,0,wx.ALIGN_LEFT , 0)
        SearchSizer.Add(self.SearchButton,0,wx.ALIGN_LEFT , 0)

        ButtonSizer = wx.GridSizer(2,5)
        ButtonSizer.AddSpacer((20,20))
        ButtonSizer.AddSpacer((20,20))
        ButtonSizer.AddSpacer((20,20))
        ButtonSizer.Add(self.DownButton,0,wx.ALIGN_LEFT , 0)
        ButtonSizer.AddSpacer((20,20))
        ButtonSizer.AddSpacer((20,20))
        ButtonSizer.AddSpacer((20,20))
        ButtonSizer.AddSpacer((20,20))
        ButtonSizer.Add(self.UpButton,0,wx.ALIGN_LEFT , 0)
        

        DownLoadSizer = wx.GridSizer(3,5)
        DownLoadSizer.AddSpacer((20,20))
        DownLoadSizer.AddSpacer((20,20))
        DownLoadSizer.AddSpacer((20,20))
        DownLoadSizer.Add(self.PathLabel,0,wx.ALIGN_LEFT , 0)
        DownLoadSizer.AddSpacer((20,20))
        DownLoadSizer.AddSpacer((20,20))
        DownLoadSizer.AddSpacer((20,20))
        DownLoadSizer.AddSpacer((20,20))
        DownLoadSizer.Add(self.PathText,0,wx.ALIGN_LEFT ,9)
        DownLoadSizer.AddSpacer((20,20))
        DownLoadSizer.AddSpacer((20,20))
        DownLoadSizer.AddSpacer((20,20))
        DownLoadSizer.AddSpacer((20,20))
        DownLoadSizer.Add(self.PathButton,0,wx.ALIGN_LEFT , 0)
        DownLoadSizer.Add(self.DownLoadButton,0,wx.ALIGN_LEFT , 0)
        


        MainSizer.AddSpacer((20,5))
        MainSizer.Add(LabelSizer, 0.1, wx.EXPAND, 0)
        MainSizer.Add(SearchSizer, 0.1, wx.EXPAND, 0)
        MainSizer.AddSpacer((20,5))
        MainSizer.Add(ButtonSizer, 0.2, wx.EXPAND, 0)
        MainSizer.AddSpacer((20,5))
        MainSizer.Add(DownLoadSizer, 0.1, wx.EXPAND, 0)
        MainSizer.AddSpacer((width,width*0.618*0.5))
    
        self.SetSizer(MainSizer)
        self.Layout()
   
      
    
                
if __name__ == '__main__':
    app = MyApp(False)
    app.MainLoop()
