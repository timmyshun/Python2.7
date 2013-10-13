# -*- coding: utf-8 -*-
import xlwt as bookwrite
import xlrd as bookread
import os

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


def Str2Hex(numstr):#将字符串转换成数
    hexdic = { '0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,\
               '9':9,'A':10, 'B':11,'C':12, 'D':13,'E':14, 'F':15 ,\
               'a':10, 'b':11,'c':12, 'd':13,'e':14, 'f':15}
    num = 0
    for i in range(len(numstr)):
        if numstr[i] in hexdic.keys():
            num *=16
            num +=hexdic[numstr[i]]
    return num

def CreatExcel():
    return bookwrite.Workbook()

def AddToExcel(book,group,data):
    title = Hex2Str(group)
    sheet = book.add_sheet(title)

    colcount = 5
    rowcount = len(data)

    sheet.write(0,0,u"功能组")
    sheet.write(0,1,title)
    sheet.write(1,0,u"功能码号")
    sheet.write(1,1,u"最小值")
    sheet.write(1,2,u"最大值")
    sheet.write(1,3,u"默认值")
    sheet.write(1,4,u"修改权限")

    for col in xrange(colcount):
        for row in range(2,rowcount+2):
            sheet.write(row,col,data[row-2][col])
    return book

def AddToExcels(book,group,data):
    groupcount = len(group)
    datacount = len(data)

    if groupcount != datacount:
        return 0
    else:
        for i in range(groupcount):
            book = AddToExcel(book,group[i],data[i])
        return book

def SaveExcel(book,name='data.xls'):
    if(os.path.exists(name)):
        try:
            os.remove(name)
        except:
            return 0
    book.save(name)
    return 1

def LoadSheet(sheet):
    rowcount = sheet.nrows
    colcount = sheet.ncols

    if colcount == 5 :
        Fgroup = Str2Hex(sheet.cell(0,1).value)
        Fdata = []
    else:
        return 0,[(0,0,0,0,0)]

    for i in range(2,rowcount):
        try:
            num = int(sheet.cell(i,0).value)
            min_data = int(sheet.cell(i,1).value)
            max_data = int(sheet.cell(i,2).value)
            default_data = int(sheet.cell(i,3).value)
            flag = int(sheet.cell(i,4).value)
        except:
            return 0,[(0,0,0,0,0)]
        Fdata.append((num,min_data,max_data,default_data,flag))

    return Fgroup,Fdata


def LoadSheetByIndex(index=0,name='data.xls'):
    if(os.path.exists(name)):
        try:
            book = bookread.open_workbook(name)
        except:
            return 0,[(0,0,0,0,0)]
    sheetNum = book.nsheets
    if index >= sheetNum:
        return 0,[(0,0,0,0,0)]
    else:
        sheet = book.sheet_by_index(index)

    Fgroup,Fdata = LoadSheet(sheet)
    return Fgroup,Fdata

def LoadSheetByGroup(group,name='data.xls'):
    if(os.path.exists(name)):
        try:
            book = bookread.open_workbook(name)
        except:
            return 0,[(0,0,0,0,0)]
    sheetname = Hex2Str(group)
    if sheetname in book.sheet_names() :
        sheet = book.sheet_by_name(sheetname)
        Fgroup,Fdata = LoadSheet(sheet)
        return Fgroup,Fdata
    else:
        for sheet0 in book.sheets():
            if sheetname == sheet0.cell(0,1).value:
                sheet = sheet0
                Fgroup,Fdata = LoadSheet(sheet)
                return Fgroup,Fdata
        return 0,[(0,0,0,0,0)]

def LoadExcel(name='data.xls'):
    if(os.path.exists(name)):
        try:
            book = bookread.open_workbook(name)
        except:
            return [0],[[(0,0,0,0,0)]]
    Fgroups = []
    Fdatas = []
    for sheet in book.sheets():
        Fgroup,Fdata = LoadSheet(sheet)
        Fgroups.append(Fgroup)
        Fdatas.append(Fdata)
    return Fgroups,Fdatas

if __name__ == '__main__':
    book = CreatExcel()
    Fgroup=[0xF0]
    Fdata1=[(0,1,2,2,0),(1,0,2,0,1),(2,0,2,0,2),(3,0,9,0,1),(4,0,9,0,1),\
        (5,0,1,0,2),(6,0,150,100,2),(7,0,34,0,2),(8,0,5000,5000,2),(9,0,1,0,2),\
        (10,5000,60000,5000,1),(11,0,5,0,1),(12,0,5000,5000,2),(13,0,5000,0,2),(14,0,5000,0,2),\
        (15,5,160,40,2),(16,0,1,1,2),(17,0,65000,200,2),(18,0,65000,200,2),(19,0,2,1,1),\
        (21,0,5000,0,2),(22,1,2,2,1),(23,0,1,0,2),(24,0,3,0,1),(25,0,2,0,1),(26,0,1,0,1),\
        (27,0,9999,0,2)]

    Fdata =[Fdata1]
    book = AddToExcels(book,Fgroup,Fdata)
   # SaveExcel(book)
  #  Fgroup,Fdata = LoadSheetByIndex()
   # Fgroup,Fdata = LoadSheetByGroup(0xf0)
    print LoadExcel()

