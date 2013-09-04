import urllib,urllib2,cookielib#下载

import sys,os,shutil #删除文件
import urlparse #网页保存
import re  #正则表达式处理
import win32com.client#调用IE
import time
def downloadhtml1(url):
    #网络协议有待学习
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
    opener.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322)')]
    f = opener.open(url)
    s = f.read()
    return s

def downloadhtml(url):
    #网络协议有待学习
    user_agent = "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
    header = { 'User-Agent' : user_agent } 
    req = urllib2.Request(url,headers = header) 
    response = urllib2.urlopen(req) 
    the_page = response.read() 
    return the_page

def GetSearchHtml(engine,site,source,filetype,page):
    word = source.encode('utf-8')+r" "+filetype+r" site:"+site
    if engine == "google":
        pass  
    else:
        urlpost = r"http://www.baidu.com/s?"
        params = urllib.urlencode({
                                    'ie':'utf-8',#关键词编码
                                    'wd': word,
                                    'pn':page*20,#页数
                                    'rn':20,#一页内行数
                                    'cl':3,#搜索类型 网页搜索
                                    'lm':0,#时间限制0  无限制
                                    'q5':0,#搜索位置限制 0 无限制
                                    })
        url = urlpost+params
        html = downloadhtml(url)
        return (url,html)
def SaveHtml(url,html,chdir):
    if(os.path.exists(u".\html")==False):
        os.mkdir(u".\html")
    if(os.path.exists(u".\html\\"+chdir)==False):
        os.mkdir(u".\html\\"+chdir)
    urlp = urlparse.urlparse(url)
    host = urlp.netloc
    i = 0
    while i<1024:
        name = host+str(i)+".html"
        if(os.path.exists(u".\html\\"+chdir+u"\\"+name)==False):
            fhtml = open(".\html\\"+chdir+u"\\"+name,'w+')
            fhtml.write(html)
            return True
        i +=1
        if i==1023:
            return False
def ClearHtml():
    if(os.path.exists(u".\html")==False):
        os.mkdir(u".\html")
    else:
        shutil.rmtree(u".\html")
        os.mkdir(u".\html")
    
def GetFileUrls(html):
    goodurls = []
    htmlp = html.replace(' ','')
    htmlp = htmlp.replace('\n','')
    htmlp = htmlp.replace('\t','')
    urls=re.findall(r"http://www.baidu.com/link.*?target=",htmlp,re.I)#利用正则表达式提前链接标签
    #进一步处理链接
    for url in urls:
        goodurls.append(url[:-8])
    return goodurls

class IshareHtml():
    fileID = ""
    html = ""
    fileName = ""
    fileCent = ""
    fileSize = ""
    phoneDownLoadURL = ""
    pcDownLoadUrl = ""
    def __init__(self,isharehtml):
        self.html=isharehtml
        if(self.GetFileCent()==""):
            return
        self.GetFileID()
        self.GetFileName()
        self.GetFileSize()
        self.GetPhoneDownLoadURL()
    def GetFileName(self):
        if len(self.fileName)>0:
            return self.fileName
        html = self.html.replace(" ","")
        names =re.findall( "<h1class=\"f14\"style=\"display:inline;\">.*?</h1>",html,re.I)#利用正则表达式提前链接标签
        if len(names) > 0 :
            name = names[0][38:-5]
            self.fileName = name
            return name
        else:
            return ''
    def GetFileID(self):
        if len(self.fileID)>0:
            return self.fileID
        html = self.html.replace(" ","")
        ids =re.findall("<inputtype=\"hidden\"name=\"file_id\"id=\"file_id\"value=\".*?\">",html,re.I)#利用正则表达式提前链接标签
        if len(ids) > 0 :
            ID = ids[0][52:-2]
            self.fileID = ID
            return ID
        else:
            return ""
    def GetFileCent(self):
        if len(self.fileCent)>0:
            return self.fileCent
        html = self.html.replace(" ","")
        cents =re.findall("<tdwidth=\"184\"height=\"37\"align=\"right\">.*?<br>",html,re.I)#利用正则表达式提前链接标签
        if len(cents) > 0 :
            cent = str(cents[0][-7])
            self.fileCent = cent
            return cent
        else:
            return ''
    def GetFileSize(self):
        if len(self.fileSize)>0:
            return self.fileSize
        html = self.html.replace(" ","")
        sizes =re.findall("<tdwidth=\"184\"height=\"37\"align=\"right\">.*?</span>",html,re.I)#利用正则表达式提前链接标签
        if len(sizes) > 0 :
            size = sizes[0][63:-7]
            self.fileSize = size
            return size
        else:
            return ""
    def GetPhoneDownLoadURL(self):
        if len(self.phoneDownLoadURL)>0:
            return self.phoneDownLoadURL
        try:
            sizeNum = float(self.fileSize[:-2])
        except:
            sizeNum = 0
        sizeUnit = self.fileSize[-2:]
        if (sizeUnit == "MB" and sizeNum <=5)or(sizeUnit == "KB"):
            self.phoneDownLoadURL = ("http://ishare.sina.cn/dintro.php?id="+self.fileID)
        else:
            self.phoneDownLoadURL = ""
        return self.phoneDownLoadURL
    def GetPCDownLoadURL(self):
        if len(self.pcDownLoadUrl)>0:
            return self.pcDownLoadUrl
        try:
            centNum = self.fileCent[0]
        except:
            centNum = -1
        if (centNum =="0"):
            self.pcDownLoadUrl = ("http://ishare.iask.sina.com.cn/download/explain.php?fileid="+self.fileID)
        else:
            self.pcDownLoadUrl = ""
        return self.pcDownLoadUrl
    def PCDownLoadIE(self):
        if self.pcDownLoadUrl == "":
            return False
        iewindow = win32com.client.DispatchEx('InternetExplorer.Application.1')
        iewindow.Visible = 1  # 1表示IE窗口显示，你可以换0试试
        targetURL = self.pcDownLoadUrl
        iewindow.Navigate(targetURL) # 打开网页
        return True
    

        
class IsharePhoneHtml():
    html = ""
    phoneDownLoadURL = ""
    def __init__(self,isharephonehtml):
        self.html = isharephonehtml
        self.GetPhoneDownLoadURL()
    def GetPhoneDownLoadURL(self):
        if len(self.phoneDownLoadURL)>0:
            return self.phoneDownLoadURL
        html = self.html.replace(" ","")
        phoneDownLoadURLs =re.findall( "<ahref=\"http://sinastorage.cn/.*?\">立即下载",html,re.I)#利用正则表达式提前链接标签
        if len(phoneDownLoadURLs) > 0 :
            phoneDownLoadURL = phoneDownLoadURLs[0][8:-14]
            self.phoneDownLoadURL = phoneDownLoadURL
            return phoneDownLoadURL
        else:
            return ''
        
    def PhoneDownLoadIE(self):
        if self.phoneDownLoadURL == "":
            return False
        iewindow = win32com.client.DispatchEx('InternetExplorer.Application.1')
        iewindow.Visible = 0  # 1表示IE窗口显示，你可以换0试试
        targetURL = self.phoneDownLoadURL
        iewindow.Navigate(targetURL) # 打开网页
        return True
    def Download(self):
        pass
                



    
    
    


if __name__ == "__main__":
    #获取搜索页面
    url,searchhtml = GetSearchHtml("baidu","ishare.iask.sina.com.cn","opencv","",0)
    #解析搜索页面获得文件页面
    urls = GetFileUrls(searchhtml)
    print urls
    for ur in urls:
        html=downloadhtml(ur)
        isharehtml = IshareHtml(html)
        isharehtml.GetPCDownLoadURL()
        isharehtml.PCDownLoadIE()
    
      

