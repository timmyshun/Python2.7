#! /usr/bin/env python
#coding=utf-8
import wx,wx.grid
#建立表        
class Grid(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1)
        self.CreateGrid(25, 5)
        self.SetColLabelValue(0, u"功能码组")
        self.SetColLabelValue(1, u"功能码号")
        self.SetColLabelValue(2, u"默认值")
        self.SetColLabelValue(3, u"停止中修改")
        self.SetColLabelValue(4, u"运行中修改")
