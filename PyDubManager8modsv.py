import wx
import os
import time
import win32gui
#https://github.com/wuxc/pywin32doc/blob/master/md/win32gui.md
import win32con
import win32process
import psutil
#from ObjectListView import ObjectListView, ColumnDefn
import pdb
from datetime import datetime
import wx.stc

import pygame
import win32api
import win32ui

import pickle

import base64

import clr
clr.AddReference('NAudio') #ildasm used on NAudio.dll showed this was the namespace
clr.AddReference('Jacobi.Vst.Core')
clr.AddReference('Jacobi.Vst.Framework')
#clr.AddReference('Jacobi.Vst3.Interop')
import NAudio as NAudio
#print("import clr succeeded, NAudio imported")

ID_BUTTON=100
ID_EXIT=200
ID_SPLITTER=300

pathL = ""
pathR = ""

filetgt = ""
#set by message box
counter1 = 0
#passt2 = ""

#looks like this was based on the code here http://zetcode.com/wxpython/skeletons/

#geany Build - Set Build Commands - Execute:
#"C:\Python27\python.exe" -i "%f"

def fixString(streng):
	#remove trailing \\
	tempstr = streng.split('\\')
	#if tempstr[len(tempstr)-1] == '':
		#tempstr.pop()
	if len(tempstr) > 1:
		return "\\".join(tempstr)
	else:
		return str(tempstr) + "\\"
		
def addSlash(streng):
	#if necessary
	if streng.endswith("\\"):
		pass
	else:
		streng = streng + "\\"
	return streng
	
def justfile(streng):
	tempstr = streng.split('\\')
	return tempstr[len(tempstr)-1]
	#pydubmanager5 for use in def File
	
#def justdir(streng):
	#example inputs C:\program files
	#example input2 c:\program files\
	
def upDir(streng):
	tempstr = streng.split('\\')
	tempstr2 = "\\".join(tempstr[0:len(tempstr)-1])
	if len(tempstr2) == 2:
		tempstr2 = tempstr2 + '\\'
	return tempstr2
	
def get_hwnds_for_pid(pid):
	def callback(hwnd, hwnds):
		if win32gui.IsWindowVisible(hwnd) \
			and win32gui.IsWindowEnabled(hwnd):
			(_, found_pid) = win32process.GetWindowThreadProcessId(hwnd)
			if found_pid == pid:
				hwnds.append(hwnd)
		return True

	hwnds = []
	win32gui.EnumWindows(callback, hwnds)
	return hwnds
	
def checkTgt(hwnd):
	file1 = open(filetgt,"a+")
	#file1.write(str(win32gui.GetWindowText(int(hwnd))) + "\r\n")
	file1.write(str(win32gui.GetWindowText(int(hwnd))) + "\n")
	file1.close()
	file1a = open(filetgt,"r+")
	filelines = file1a.readlines()
	if len(filelines)>2:
		if filelines[len(filelines)-1] == filelines[len(filelines)-2]:
			filelines.pop()
	file1a.close()
	file2 = open(filetgt,"w")
	file2.writelines(filelines)
	file2.close()
	'''
	filelines = file1.readlines()
	if filelines[len(filelines)-1] == filelines[len(filelines)-2]:
		filelines.pop()
	file1.close()
	'''
	'''
	file2 = open(filetgt,"w")
	file2.writelines(filelines)
	file2.close()
	'''
	#pdb.set_trace()
	#print(file1.read())
	
	#print(win32gui.GetWindowText(int(hwnd)))

def hideConsole():
	#pids = psutil.pids()
	try:
		os.system('"' + "winhide.exe PyDubManager1.exe" + '"')
	except:
		pass
		
def unhideConsole():
	try:
		os.system('"' + "winshow.exe cmd.exe" + '"')
	except:
		pass

class MyListCtrl(wx.ListCtrl):
	def __init__(self, parent, id):
		wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT)
		
		files = os.listdir('.')
		
		images = ['empty.png','folder.png','sourcepy.png','image.png','pdf.png','up16.png']
		
		self.InsertColumn(0, 'Name')
		self.InsertColumn(1, 'Ext')
		self.InsertColumn(2, 'Size', wx.LIST_FORMAT_RIGHT)
		self.InsertColumn(3, 'Modified')
		self.SetColumnWidth(0, 220)
		self.SetColumnWidth(1, 70)
		self.SetColumnWidth(2, 100)
		self.SetColumnWidth(3, 420)
		
		self.il = wx.ImageList(16,16)
		for i in images:
			self.il.Add(wx.Bitmap(i))
		self.SetImageList(self.il,wx.IMAGE_LIST_SMALL)
		
		j = 1
		self.InsertItem(0,'..')
		self.SetItemImage(0,5)
		#new label logic to try to handle different directories
		global pathL
		global pathR
		pathL = os.getcwd()
		pathR = os.getcwd()
		##print('init path')
		##print('repr(pathL)>' + repr(pathL))
		##print('repr(pathR)>' + repr(pathR))
		#print(self.mypath)
		
		#images = 
		j=1
		self.Bind(wx.EVT_KEY_UP,self.prockey)
		for i in files:
			(name, ext) = os.path.splitext(i)
			ex = ext[1:]
			size = os.path.getsize(i)
			sec = os.path.getmtime(i)
			self.InsertItem(j, i)
			self.SetItem(j, 1, ex)
			self.SetItem(j, 2, str(size) + ' B')
			self.SetItem(j, 3, time.strftime('%Y-%m-%d %H:%M', 
			time.localtime(sec)))

			if os.path.isdir(i):
				self.SetItemImage(j, 1)
			elif ex == 'py':
				self.SetItemImage(j, 2)
			elif ex == 'jpg':
				self.SetItemImage(j, 3)
			elif ex == 'pdf':
				self.SetItemImage(j, 4)
			else:
				self.SetItemImage(j, 0)

			if (j % 2) == 0:
				self.SetItemBackgroundColour(j, '#e6f1f5')
			j = j + 1
	def update(self):
		global pathL
		global pathR
		filesDef = os.listdir('.')
		filesL = os.listdir(str(pathL))
		#(filesL)
		#print("filesL^")
		filesR = os.listdir(str(pathR))
		files = filesDef
		##print("FILES =")
		##print(dir(files))
		##print(files)
		if self.Id == 6969:
			#print('right updateZ')
			os.chdir(pathR)
			files = filesR
		if self.Id == 4646:
			#print('left updateZ')
			os.chdir(pathL)
			files = filesL
		#files = os.listdir('.')

		j=1
		#self.InsertStringItem(0,'..')
		self.InsertItem(0,'..')
		#print('hey update')
		#print(self)
		#print(dir(self))
		#print(os.getcwd())
		#self.SetLabel(os.getcwd())
		#print(self.GetLabel())
		for i in files:
			(name, ext) = os.path.splitext(i)
			ex = ext[1:]
			size = os.path.getsize(i)
			sec = os.path.getmtime(i)
			#self.InsertStringItem(j, i)
			self.InsertItem(j,i)
			#self.SetStringItem(j,1,ex)
			self.SetItem(j,1,ex)
			#self.SetStringItem(j,2,str(size) + ' B')
			self.SetItem(j,2,str(size) + ' B')
			#self.SetStringItem(j,3,time.strftime('%Y-%m-%d %H:%M', time.localtime(sec)))
			self.SetItem(j,3,time.strftime('%Y-%m-%d %H:%M', time.localtime(sec)))
			if os.path.isdir(i):
				self.SetItemImage(j, 1)
			elif ex == 'py':
				self.SetItemImage(j, 2)
			elif ex == 'jpg':
				self.SetItemImage(j, 3)
			elif ex == 'pdf':
				self.SetItemImage(j, 4)
			else:
				self.SetItemImage(j, 0)
			if (j % 2) == 0:
				self.SetItemBackgroundColour(j, '#e6f1f5')
			j = j + 1
		#filething.sb.SetStatusText(os.getcwd())
		filething.sb.SetStatusText(pathL + "   - - - -   " + pathR)
	def update2(self):
		print("oops")
	def prockey(self,event):
		keycode = event.GetKeyCode()
		if keycode == wx.WXK_BACK:
			#print("oh shit")
			#copying the entire OnClick code here and modifying it lol
			#pathq = os.getcwd() + '\\' + event.GetText()
			#pathb = event.GetText()
			pathb = ".."
			#print('event ingested into OnClick')
			#print(event)
			#print(dir(event))
			#print(event.Text)
			#print(event.Id) #4646 left 6969 right
			#print(event.Item)
			#print(dir(event.Item))
			#print(event.Item.Text)
			##event text is the text that we clicked on which was the literal filename
			
			#print event.GetItem()
			
			#print event.GetColumn()
			##-1
			global pathL
			global pathR
			if event.Id == 4646:
				#print('left verified: pathL = ' + pathL)
				pathLprev = pathL
				fixedLprev = fixString(pathLprev)
				if pathb == '..':
					pathL = upDir(fixedLprev)
					#print('go up dir')
					#print(pathLprev.split('\\'))
				else:
					#pathL = pathLprev + '\\' + event.GetText()
					pathL = fixedLprev + '\\' + event.GetText()
					pathL = pathL.replace('\\\\','\\').replace("'[","").replace("]'","")
				#print('left new: pathL = ' + pathL)
				if os.path.isdir(pathL):
					pass
				else:
					pathL = pathLprev
					os.chdir(pathL)
					os.system('"' + pathb + '"')
			if event.Id == 6969:
				#print('right verified: pathR = ' + pathR)
				pathRprev = pathR
				fixedRprev = fixString(pathRprev)
				if pathb == '..':
					pathR = upDir(fixedRprev)
				else:
					pathR = fixedRprev + '\\' + event.GetText()
					pathR = pathR.replace('\\\\','\\').replace("'[","").replace("]'","")
				#print('right new: pathR = ' + pathR)
				if os.path.isdir(pathR):
					pass
				else:
					pathR = pathRprev
					os.chdir(pathR)
					os.system('"' + pathb + '"')
			pp = event.GetEventObject()
			pp.DeleteAllItems()
			pp.update()

class FileMgr1(wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self,parent,569,title,(50,50),(900,900))
		
		#button1 = wx.Button(self, ID_BUTTON + 1, "F3 View")
        #button2 = wx.Button(self, ID_BUTTON + 2, "F4 Edit")
        #button3 = wx.Button(self, ID_BUTTON + 3, "F5 Copy")
        #button4 = wx.Button(self, ID_BUTTON + 4, "F6 Move")
        #button5 = wx.Button(self, ID_BUTTON + 5, "F7 Mkdir")
        #button6 = wx.Button(self, ID_BUTTON + 6, "F8 Delete")
        #button7 = wx.Button(self, ID_BUTTON + 7, "F9 Rename")
        #button8 = wx.Button(self, ID_EXIT, "F10 Quit")
        
        #self.sizer2.Add(button1, 1, wx.EXPAND)
        #self.sizer2.Add(button2, 1, wx.EXPAND)
        #self.sizer2.Add(button3, 1, wx.EXPAND)
        #self.sizer2.Add(button4, 1, wx.EXPAND)
        #self.sizer2.Add(button5, 1, wx.EXPAND)
        #self.sizer2.Add(button6, 1, wx.EXPAND)
        #self.sizer2.Add(button7, 1, wx.EXPAND)
        #self.sizer2.Add(button8, 1, wx.EXPAND)
        #self.Bind(wx.EVT_BUTTON,self.OnExit,id=ID_EXIT)
        
        #self.sizer=wx.BoxSizer(wx.VERTICAL)
        #self.sizer.Add(self.splitter,1,wx.EXPAND)
        #self.sizer.Add(self.sizer2,0,wx.EXPAND)
        #self.SetSizer(self.sizer)
        #size = wx.DisplaySize()
        #self.SetSize(size)
		self.sb = self.CreateStatusBar()
		#self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnClick, self.list
		
	def OnExit(self,e):
		self.Close(True)
	def OnSize(self,event):
		size = self.GetSize()
		self.splitter.SetSashPosition(size.x/2)
		self.sb.SetStatusText(os.getcwd())
		event.Skip()
	def onFuncL(self,event):
		print("Left Pane Path is :")
		global pathL
		print(pathL)
		
	def onFuncR(self,event):
		print("Right Pane Path is :")
		global pathR
		print(pathR)
	def DirL(self,event):
		#print("dirL")
		dlg = wx.TextEntryDialog(self,'Goto Path:','?')
		global pathL
		dlg.SetValue(pathL)
		if dlg.ShowModal() == wx.ID_OK:
			itext = dlg.GetValue()
			itext2 = addSlash(itext)
		dlg.Destroy()
		pathL = itext2
		p1.update()
		
	def DirR(self,event):
		#print("dirR")
		dlg = wx.TextEntryDialog(self,'Goto Path:','?')
		global pathR
		dlg.SetValue(pathR)
		if dlg.ShowModal() == wx.ID_OK:
			itext = dlg.GetValue()
			itext2 = addSlash(itext)
		dlg.Destroy()
		pathR = itext2
		p2.update()
		
	def OnDoubleClick(self,event):
		size = self.GetSize()
		self.splitter.SetSashPosition(size.x/2)
	def OnClick(self, event):
		#print event.GetText()
		#print event.GetText()
		#os.chdir(os.getcwd() + '\\\\' + event.GetText())
		pathq = os.getcwd() + '\\' + event.GetText()
		pathb = event.GetText()
		#print('event ingested into OnClick')
		#print(event)
		#print(dir(event))
		#print(event.Text)
		#print(event.Id) #4646 left 6969 right
		#print(event.Item)
		#print(dir(event.Item))
		#print(event.Item.Text)
		##event text is the text that we clicked on which was the literal filename
		
		#print event.GetItem()
		
		#print event.GetColumn()
		##-1
		global pathL
		global pathR
		if event.Id == 4646:
			#print('left verified: pathL = ' + pathL)
			pathLprev = pathL
			fixedLprev = fixString(pathLprev)
			if event.GetText() == '..':
				pathL = upDir(fixedLprev)
				#print('go up dir')
				#print(pathLprev.split('\\'))
			else:
				#pathL = pathLprev + '\\' + event.GetText()
				pathL = fixedLprev + '\\' + event.GetText()
				pathL = pathL.replace('\\\\','\\').replace("'[","").replace("]'","")
			#print('left new: pathL = ' + pathL)
			if os.path.isdir(pathL):
				pass
			else:
				pathL = pathLprev
				os.chdir(pathL)
				os.system('"' + pathb + '"')
		if event.Id == 6969:
			#print('right verified: pathR = ' + pathR)
			pathRprev = pathR
			fixedRprev = fixString(pathRprev)
			if event.GetText() == '..':
				pathR = upDir(fixedRprev)
			else:
				pathR = fixedRprev + '\\' + event.GetText()
				pathR = pathR.replace('\\\\','\\').replace("'[","").replace("]'","")
			#print('right new: pathR = ' + pathR)
			if os.path.isdir(pathR):
				pass
			else:
				pathR = pathRprev
				os.chdir(pathR)
				os.system('"' + pathb + '"')
			
			'''
		if os.path.isdir(pathq):
			os.chdir(os.getcwd() + '\\' + event.GetText())
		else:
			#print(pathq)
			os.system('"' + pathb + '"')
			'''
		#print(os.getcwd())
		#print(os.listdir('.'))
		
		##print(event.GetEventObject())
		pp = event.GetEventObject()
		pp.DeleteAllItems()
		pp.update()
	def startTask(self, event):
		taskFrame = TaskFrame(self)
		taskFrame.Show()
	def startText(self,event):
		textFrame = TextFrame(self)
		textFrame.Show()
		#brb
	def startG(self,event):
		gFrame = GFrame(self)
		gFrame.Show()

class TaskListCtrl(wx.ListCtrl):
		def __init__(self, parent, id):
			wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT)
			self.InsertColumn(0, 'PID')
			self.InsertColumn(1, 'Exe')
			self.InsertColumn(2, 'HWND')
			self.InsertColumn(3, 'Misc')
			self.InsertColumn(4,'PATH')
			#self.InsertItem(1,"yo","c:\\","135","lol")
			##self.InsertItem(1,"yo")
			##self.SetItem(0,2,"c:\\")
			self.InsertItem(1,"..")
			self.getpids()
			self.addpids()
			print(self.pids)
			
		def getpids(self):
			self.pids = psutil.pids()
		def addpids(self):
			print('length')
			print(len(self.pids))
			print(self.pids[1])
			for i in range(len(self.pids)):
				self.InsertItem(1,str(self.pids[i]))
				try:
					p = psutil.Process(self.pids[i])
					str1 = p.exe()
					str2 = str1.split('\\')
					strexe = str2[len(str2)-1]
					#print(str2[len(str2)-1])
					#self.SetItem(1,1,str(p.exe()))
					self.SetItem(1,1,strexe)
					hwnds = []
					hwnds = get_hwnds_for_pid(int(self.pids[i]))
					if len(hwnds) > 1:
						self.SetItem(1,3,"multi")
						#for ix in range(len(hwnds)):
							#print("wow")
							#print(dir(parent))
							#global passt2
							#passt2.InsertItem(1,str(hwnds[ix]))
							#passt2.SetItem(1,2,str(self.pids[i]))
							#parent.t2.InsertItem(1,str(hwnds[ix]))
							#parent.t2.SetItem(1,2,str(self.pids[i]))
					self.SetItem(1,2,str(hwnds[0]))
					self.SetItem(1,4,str(str1))
				except:
					pass
				
class RightListCtrl(wx.ListCtrl):
	def __init__(self,parent,id):
		wx.ListCtrl.__init__(self,parent,id,style=wx.LC_REPORT)
		self.InsertColumn(0,'HWND')
		self.InsertColumn(1,"PID")
		self.InsertColumn(2,"Title")
		self.SetColumnWidth(2,250)
		
class TaskFrame(wx.Frame):
	def __init__(self, parent):
		#wx.Frame.__init__(self, parent, -1, size = (800, 700), style = wx.CAPTION | wx.SYSTEM_MENU | wx.CLOSE_BOX)
		wx.Frame.__init__(self, parent, -1, size = (800, 700))
		self.SetIcon(wx.Icon("icon.png"))
		self.SetTitle("Process Manager")
		self.splitter = wx.SplitterWindow(self, ID_SPLITTER,style=wx.SP_BORDER)
		self.splitter.SetMinimumPaneSize(50)
		self.tbtask = self.CreateToolBar(wx.TB_HORIZONTAL | wx.TB_FLAT)
		self.btn1 = self.tbtask.AddTool(721,"L",wx.Bitmap("folder.png"))
		self.btn2 = self.tbtask.AddTool(722,"T",wx.Bitmap("timer.png"))
		self.tbtask.Realize()
		self.timer = wx.Timer(self)
		self.timertgt = "" #will contain the HWND to check
		self.Bind(wx.EVT_TIMER,self.Tick,self.timer)
		self.t1 = TaskListCtrl(self.splitter,11)
		self.t2 = RightListCtrl(self.splitter,12)
		#global passt2
		#passt2 = self.t2
		self.splitter.SplitVertically(self.t1,self.t2)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.splitter,135,wx.EXPAND)
		self.SetSizer(self.sizer)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.OnClick,self.t1)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.RightSideClick,self.t2)
		self.Bind(wx.EVT_TOOL,self.dobtn,self.btn1)
		self.Bind(wx.EVT_TOOL,self.dobtn2,self.btn2)
	def OnClick(self,event):
		#print event.Id
		#print event.GetText()
		hwnds = []
		hwnds = get_hwnds_for_pid(int(event.GetText()))
		print(hwnds)
		if len(hwnds)>=0:
			for i in range(len(hwnds)):
				self.t2.InsertItem(0,str(hwnds[i]))
				self.t2.SetItem(0,1,event.GetText())
				#add window title
				self.t2.SetItem(0,2,win32gui.GetWindowText(hwnds[i]))
		#print(dir(self.splitter))
	def RightSideClick(self,event):
		print(event.GetText())
		time.sleep(0.2)
		#win32gui.SetForegroundWindow(int(event.GetText()))
		win32gui.ShowWindow(int(event.GetText()),1)
	def dobtn(self,event):
		#print(dir(self.t1))
		#print(help(self.t1.GetItem))
		#print(self.t1.GetItemCount())
		itemct = int(self.t1.GetItemCount())
		#print('self.t1.GetItem(1).GetData() >>')
		#print(self.t1.GetItem(1).GetData())
		#pdb.set_trace()
		txt = self.t1.GetItem(1).Text
		#txt = pid
		for ict in range(itemct):
			txt = self.t1.GetItem(ict).Text
			txtHwnd = self.t1.GetItem(ict,2).Text
			hwnds = []
			if txtHwnd != "":
				hwnds = get_hwnds_for_pid(int(txt))
				#pdb.set_trace()
				for ixy in range(len(hwnds)):
					self.t2.InsertItem(0,str(hwnds[ixy]))
					self.t2.SetItem(0,1,txt)
					self.t2.SetItem(0,2,win32gui.GetWindowText(hwnds[ixy]))
				pass
	def dobtn2(self,event):
		dlg = wx.TextEntryDialog(self,'Monitor title of which HWND?:','?')
		#dlg.SetValue(pathL)
		if dlg.ShowModal() == wx.ID_OK:
			itext = dlg.GetValue()
			#itext2 = addSlash(itext)
		dlg.Destroy()
		self.timertgt = itext
		print(itext)
		dlg2 = wx.TextEntryDialog(self,'ms interval?:','?')
		if dlg2.ShowModal() == wx.ID_OK:
			interval = dlg2.GetValue()
		dlg2.Destroy()
		dlg3 = wx.TextEntryDialog(self,'filename eg history.txt?:','?')
		if dlg3.ShowModal() == wx.ID_OK:
			global filetgt
			filetgt = dlg3.GetValue()
		dlg3.Destroy()
		self.timer.Start(int(interval)) #timer gets started with the given interval
	def Tick(self,event):
		print(self.timertgt)
		checkTgt(self.timertgt)

'''
class GFrame(PygameDisplay):
	def __init__(self,parent,id):
		PygameDisplay.__init__(self,parent,id)
		#wx.Window.__init__(self, parent, 9996, size = (900,660))
'''

class FileMgr(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self,parent,569,title,(50,50),(800,300))
        self.sb = self.CreateStatusBar()
        tb = self.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)
        bt1 = tb.AddTool(701,"Rec",wx.Bitmap("icon.png"))
        bt2 = tb.AddTool(702,"PDB",wx.Bitmap("icon.png"))
        bt3 = tb.AddTool(703,"DBG",wx.Bitmap("icon.png"))
        self.Bind(wx.EVT_TOOL,gorecordA,bt1)
        self.Bind(wx.EVT_TOOL,gorecordA,bt2)
        self.Bind(wx.EVT_TOOL,mytest2,bt3)
        tb.Realize()
        
        self.topsplitter = wx.SplitterWindow(self,808,pos=wx.Point(0,0),size=wx.Size(400,400),style=wx.SP_BORDER,name="TopSplitter")
        self.AudioChecker = AudioCheckList(self.topsplitter, 777)
        self.recdevct = self.AudioChecker.Count
        #self.MonitorChoice = MonitorChoice(self.topsplitter, 888)
        self.rightside = MonitorPanel(self.topsplitter,999,self.recdevct)
        #self.splitter = wx.SplitterWindow(self.topsplitter, ID_SPLITTER,pos=wx.Point(0,0),size=wx.Size(400,400),style=wx.SP_BORDER,name="Splitter")
        self.topsplitter.SplitVertically(self.AudioChecker,self.rightside)
    def OnExit(self,e):
        self.Close(True)
        
class AudioCheckList(wx.CheckListBox):
    def __init__(self, parent, id):
        devicecount = NAudio.Wave.WaveIn.DeviceCount
        devicelist = []
        for n in range(devicecount):
            devicelist.append(NAudio.Wave.WaveIn.GetCapabilities(n).ProductName)
        wx.CheckListBox.__init__(self, parent, id,(0,0),(50,50),devicelist)
        #https://docs.wxpython.org/gallery.html shows most widgets

#class ASIOChoice(wx.Choice):
#lol
class ASIOChoice(wx.CheckListBox):
    def __init__(self, parent, id, pos, size):
        global availables
        availables = NAudio.Wave.AsioOut.GetDriverNames()
        #global asiolist
        global asiolist
        asiolist = []
        for n in range(10):
            try:
                asiolist.append(availables.Get(n))
            except:
                pass
        print('asiolist?')
        print(asiolist)
        wx.CheckListBox.__init__(self, parent, id, pos,size, asiolist)

class MonitorChoice(wx.Choice):
    #def __init__(self,parent,id):
    def __init__(self,parent,id,pos,size):
        devicecount = NAudio.Wave.WaveOut.DeviceCount
        devicelist = []
        for n in range(devicecount):
            devicelist.append(NAudio.Wave.WaveOut.GetCapabilities(n).ProductName)
        #wx.Choice.__init__(self, parent, id, (0,0), (50,50), devicelist)
        wx.Choice.__init__(self, parent, id, pos, size, devicelist)
        
class MonitorPanel(wx.Panel):
    def __init__(self,parent,id, countt):
        wx.Panel.__init__(self,parent,id, (0,0), (50,50), 0, "Monitor-Panel")
        for xx in range(countt):
            globals()["mon" + str(xx)] = MonitorChoice(self, 1200 + xx, (0+(xx*5),0+(xx*23)), (120,23))
        for xx in range(countt):
            globals()["monbt" + str(xx)] = wx.CheckBox(self,1400 + xx, "mon"+str(xx), (127+(xx*5),0+(xx*23)), (70,23))
        
        global asiochoice
        asiochoice = ASIOChoice(self, 5678,(220,0),(200,200))
########
def gorecordA(anevent):
    devicecount = NAudio.Wave.WaveIn.DeviceCount
    devicelist = []
    for n in range(devicecount):
        devicelist.append(NAudio.Wave.WaveIn.GetCapabilities(n).ProductName)
    print(devicelist)
    
    traceyesno = 0
    if traceyesno == 0:
        pass
    elif traceyesno == 1:
        pdb.set_trace()
    
    #checkedlist = recordbox.AudioChecker.GetChecked()
    checkedlist = recordbox.AudioChecker.GetChecked()
    print(checkedlist)
    #pdb.set_trace()
    #filething.rightside.
    
    #for xx in range(devicecount):
        #global globals()["waveIn" + str(xx)] 
        
    ## replacing range devicecount with for xx in checkedlist:
    for xx in checkedlist:
        globals()["waveIn" +  str(xx)] = NAudio.Wave.WaveIn()
    for xx in checkedlist:
        globals()["waveIn" + str(xx)].DeviceNumber = xx
    for xx in checkedlist:
        globals()["waveIn" + str(xx) + "capz"] = NAudio.Wave.WaveIn.GetCapabilities(xx)
        #globals()["waveIn" + str(xx) + "capz_a"] = globals()["waveIn" + str(xx) + "capz"].SupportsWaveFormat(NAudio.Wave.SupportedWaveFormat.WAVE_FORMAT_44S16)
        globals()["waveIn" + str(xx) + "capz_a"] = globals()["waveIn" + str(xx) + "capz"].SupportsWaveFormat(NAudio.Wave.SupportedWaveFormat.WAVE_FORMAT_96S16)
        print(globals()["waveIn" + str(xx) + "capz_a"])
        
        
        #globals()["waveIn" + str(xx) + "capz"] = globals()["waveIn" +  str(xx)].GetCapabilities()
    #__1__#pdb.set_trace()
    ##global waveIn
    ##global waveIn2
    ##global waveIn3
    ###waveIn = NAudio.Wave.WaveIn()
    ###waveIn2 = NAudio.Wave.WaveIn()
    ###waveIn3 = NAudio.Wave.WaveIn()
    ####waveIn.DeviceNumber = 0
    ####waveIn2.DeviceNumber = 1
    ####waveIn3.DeviceNumber = 2
    fourfour = 44100
    foureight = 48000
    channels = 2
    for xx in checkedlist:
        globals()["waveIn" + str(xx)].WaveFormat = NAudio.Wave.WaveFormat(fourfour,channels)
        print("waveIn" + str(xx) + ": " + str(globals()["waveIn" + str(xx)].WaveFormat.bitsPerSample))
        #24-bit recording can't be done haha
        #globals()["waveIn" + str(xx)].WaveFormat.bitsPerSample = 24
        #print("waveIn" + str(xx) + ": " + str(globals()["waveIn" + str(xx)].WaveFormat.bitsPerSample))
    #####waveIn.WaveFormat = NAudio.Wave.WaveFormat(fourfour,channels)
    #####waveIn2.WaveFormat = NAudio.Wave.WaveFormat(fourfour,channels)
    #####waveIn3.WaveFormat = NAudio.Wave.WaveFormat(fourfour,channels)
    import datetime
    timestampz = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    for xx in checkedlist:
        globals()["writer" + str(xx)] = NAudio.Wave.WaveFileWriter(timestampz + "." + str(xx) + '.wav', globals()["waveIn" + str(xx)].WaveFormat)
    
    ##writer1 = NAudio.Wave.WaveFileWriter(timestampz + ".1.wav", waveIn.WaveFormat)
    ##writer2 = NAudio.Wave.WaveFileWriter(timestampz + ".2.wav", waveIn2.WaveFormat)
    ##writer3 = NAudio.Wave.WaveFileWriter(timestampz + ".3.wav", waveIn3.WaveFormat)
    
    def wave0write(sender, e):
        if 1 == 1:
            writer0.WriteData(e.Buffer,0,e.BytesRecorded)
            writer0.Flush()
    def wave1write(sender, e):
        if 1 == 1:
            writer1.WriteData(e.Buffer,0,e.BytesRecorded)
            writer1.Flush()
    def wave2write(sender, e):
        if 1 == 1:
            writer2.WriteData(e.Buffer,0,e.BytesRecorded)
            writer2.Flush()
    def wave3write(sender, e):
        if 1 == 1:
            writer3.WriteData(e.Buffer,0,e.BytesRecorded)
            writer3.Flush()
    def wave4write(sender, e):
        if 1 == 1:
            writer4.WriteData(e.Buffer,0,e.BytesRecorded)
            writer4.Flush()
    def wave5write(sender, e):
        if 1 == 1:
            writer5.WriteData(e.Buffer,0,e.BytesRecorded)
            writer5.Flush()
    def wave6write(sender, e):
        if 1 == 1:
            writer6.WriteData(e.Buffer,0,e.BytesRecorded)
            writer6.Flush()
    def wave7write(sender, e):
        if 1 == 1:
            writer7.WriteData(e.Buffer,0,e.BytesRecorded)
            writer7.Flush()
    def wave8write(sender, e):
        if 1 == 1:
            writer8.WriteData(e.Buffer,0,e.BytesRecorded)
            writer8.Flush()
    def wave9write(sender, e):
        if 1 == 1:
            writer9.WriteData(e.Buffer,0,e.BytesRecorded)
            writer9.Flush()
    def wave10write(sender, e):
        if 1 == 1:
            writer10.WriteData(e.Buffer,0,e.BytesRecorded)
            writer10.Flush()
    

    
    #for xx in range(devicecount):
        #globals()["waveIn" + str(xx)].DataAvailable += locals()["wave"+str(xx)+"write"]
    ##for xx in range(devicecount):
    '''
    if 'waveIn0' in globals():
        waveIn0.DataAvailable += wave0write
        waveIn0.StartRecording()
    '''
        
    if 0 in checkedlist:
        waveIn0.DataAvailable += wave0write
        waveIn0.StartRecording()
    if 1 in checkedlist:
        waveIn1.DataAvailable += wave1write
        waveIn1.StartRecording()
    if 2 in checkedlist:
        waveIn2.DataAvailable += wave2write
        waveIn2.StartRecording()
    if 3 in checkedlist:
        waveIn3.DataAvailable += wave3write
        waveIn3.StartRecording()
    if 4 in checkedlist:
        waveIn4.DataAvailable += wave4write
        waveIn4.StartRecording()
    if 5 in checkedlist:
        waveIn5.DataAvailable += wave5write
        waveIn5.StartRecording()
    if 6 in checkedlist:
        waveIn6.DataAvailable += wave6write
        waveIn6.StartRecording()
    if 7 in checkedlist:
        waveIn7.DataAvailable += wave7write
        waveIn7.StartRecording()
    if 8 in checkedlist:
        waveIn8.DataAvailable += wave8write
        waveIn8.StartRecording()
    if 9 in checkedlist:
        waveIn9.DataAvailable += wave9write
        waveIn9.StartRecording()
    if 10 in checkedlist:
        waveIn10.DataAvailable += wave10write
        waveIn10.StartRecording()
    #waveIn.DataAvailable += wave1write
    #waveIn2.DataAvailable += wave2write
    #waveIn3.DataAvailable += wave3write

    #waveIn.StartRecording()
    #waveIn2.StartRecording()
    #waveIn3.StartRecording()
    recordbox.sb.SetStatusText("recording started")
'''
def gorecord(shelf): #unused. for reference.
    devicecount = NAudio.Wave.WaveIn.DeviceCount
    devicelist = []
    for n in range(devicecount):
        devicelist.append(NAudio.Wave.WaveIn.GetCapabilities(n).ProductName)
    print(devicelist)

    waveIn = NAudio.Wave.WaveIn()
    waveIn2 = NAudio.Wave.WaveIn()
    waveIn3 = NAudio.Wave.WaveIn()

    waveIn.DeviceNumber = 0
    waveIn2.DeviceNumber = 1
    waveIn3.DeviceNumber = 2

    fourfour = 44100
    foureight = 48000
    channels = 2
    waveIn.WaveFormat = NAudio.Wave.WaveFormat(fourfour,channels)
    waveIn2.WaveFormat = NAudio.Wave.WaveFormat(fourfour,channels)
    waveIn3.WaveFormat = NAudio.Wave.WaveFormat(fourfour,channels)

    import datetime
    timestampz = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

    writer1 = NAudio.Wave.WaveFileWriter(timestampz + ".1.wav", waveIn.WaveFormat)
    writer2 = NAudio.Wave.WaveFileWriter(timestampz + ".2.wav", waveIn2.WaveFormat)
    writer3 = NAudio.Wave.WaveFileWriter(timestampz + ".3.wav", waveIn3.WaveFormat)

    def wave1write(sender, e):
        if 1 == 1:
            #print('ifone')
            ##print(e.Buffer)
            ##print(e.BytesRecorded)
            writer1.WriteData(e.Buffer,0,e.BytesRecorded)
            writer1.Flush()
    def wave2write(sender, e):
        #print('okay2')
        if 1 == 1:
            writer2.WriteData(e.Buffer,0,e.BytesRecorded)
            writer2.Flush()
    def wave3write(sender, e):
        #print('okay3')
        if 1 == 1:
            writer3.WriteData(e.Buffer,0,e.BytesRecorded)
            writer3.Flush()
    
    waveIn.DataAvailable += wave1write
    waveIn2.DataAvailable += wave2write
    waveIn3.DataAvailable += wave3write

    waveIn.StartRecording()
    waveIn2.StartRecording()
    waveIn3.StartRecording()
'''    
def debog(shelf):
    pdb.set_trace()
#https://markheath.net/category/naudio   
def mytest(shelf):
    filething.sb.SetStatusText(str(filething.AudioChecker.GetCheckedItems()))
def asio1write(sender, e):
    samples = e.GetAsInterleavedSamples()
    asio1writer.WriteSamples(samples,0,samples.Length)
    asio1writer.Flush()
def mytest2(shelf):
    filething.sb.SetStatusText(str(asiochoice.GetCheckedStrings() ) )
    global asiodev
    asiodev = NAudio.Wave.AsioOut(asiochoice.GetCheckedStrings()[0])
    #stathreadattribute needed > https://github.com/pythonnet/pythonnet/issues/108
    asiodev_channelcount = asiodev.DriverInputChannelCount #6 for Zoom H6
    #https://github.com/naudio/NAudio/blob/master/Docs/AsioRecording.md
    asiodev.InitRecordAndPlayback(None, asiodev_channelcount, 44100)
    import datetime
    timestampz = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    #asiowaveformat = NAudio.Wave.WaveFormat(44100,24,asiodev_channelcount)
    asiowaveformat = NAudio.Wave.WaveFormat(44100,16,asiodev_channelcount)
    global asio1writer
    asio1writer = NAudio.Wave.WaveFileWriter(timestampz + "." + 'poly' + '.wav', asiowaveformat)
    asiodev.AudioAvailable += asio1write
    asiodev.Play()
    #pdb.set_trace()


class GFrame(wx.Frame):
	def __init__(self,parent):
		wx.Frame.__init__(self,parent,9996,size=(900,600))
		#GFrame contains a PygameDisplay called .display. this GFrame is called gFrame. created by startG in the filething .tb
		self.display = PygameDisplay(self,9999)
		self.tbg = self.CreateToolBar(wx.TB_HORIZONTAL | wx.TB_FLAT)
		self.btn1 = self.tbg.AddTool(9901,"L",wx.Bitmap("folder.png"))
		self.btn2 = self.tbg.AddTool(9902,"S",wx.Bitmap("floopy16x16.png"))
		self.btn3 = self.tbg.AddTool(9903,"S",wx.Bitmap("dead.png"))
		self.btn4 = self.tbg.AddTool(9904,"S",wx.Bitmap("dnarr.png"))
		self.btn5 = self.tbg.AddTool(9905,"S",wx.Bitmap("uparr.png"))
		self.btn6 = self.tbg.AddTool(9906,"R",wx.Bitmap("icon.png"))
		self.btn7 = self.tbg.AddTool(9907,"R",wx.Bitmap("icon.png"))
		self.btn8 = self.tbg.AddTool(9908,"R",wx.Bitmap("icon-pause.gif"))
		self.btn9 = self.tbg.AddTool(9909,"R",wx.Bitmap("icon-play.gif"))
		self.tbg.Realize()
		self.Bind(wx.EVT_TOOL,self.b1proc,self.btn1)
		self.Bind(wx.EVT_TOOL,self.b2proc,self.btn2)
		self.Bind(wx.EVT_TOOL,self.b3proc,self.btn3)
		self.Bind(wx.EVT_TOOL,self.b4proc,self.btn4)
		self.Bind(wx.EVT_TOOL,self.b5proc,self.btn5)
		self.Bind(wx.EVT_TOOL,self.PLAYBUTTON,self.btn6)
		self.Bind(wx.EVT_TOOL,self.SPAWNRECORDER,self.btn7)
		self.Bind(wx.EVT_TOOL,self.PANBUTTON,self.btn8)
		self.Bind(wx.EVT_TOOL,self.PANBUTTON2,self.btn9)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		#try:
			#import clr
			#clr.AddReference('NAudio') #ildasm used on NAudio.dll showed this was the namespace
			#import NAudio as NAudio
			#print("import clr succeeded, NAudio imported")
		#except:
			#print("import clr failed")
		
	def Kill(self,event):
		self.display.Kill(event)
		self.Destroy()
	def b1proc(self, event):
		dlg = wx.TextEntryDialog(self,'Filepath:','?')
		if dlg.ShowModal() == wx.ID_OK:
			filename_0 = dlg.GetValue()
		dlg.Destroy()
		#self.display.File(filename_0)
		self.display.File2(filename_0)
		#self.scite1.SaveFile(filename_0)
	def b2proc(self, event):
		dlg = wx.TextEntryDialog(self,'Save image:','?')
		if dlg.ShowModal() == wx.ID_OK:
			filename_0 = dlg.GetValue()
		dlg.Destroy()
		pygame.image.save(self.display.getSURF(),filename_0)
		os.system(filename_0)
	def b3proc(self,event):
		self.display.BLANK()
	def b4proc(self,event):
		self.display.PICKL()
	def b5proc(self,event):
		self.display.UNPICKL()
	#def disposer():
	def PLAYBUTTON(self,event): #b6proc
		global musicplaya
		global waveout1
		#waveout1 = NAudio.Wave.WaveOut
		#pdb.set_trace()
		#global waveoutevent
		global audiofile
		global waveoutevent
		waveoutevent = NAudio.Wave.WaveOutEvent()
		audiofile = NAudio.Wave.AudioFileReader("08-deepforest.wav")
		#audiofile = NAudio.Wave.WaveStream("08-deepforest.wav")
		#audiofile = NAudio.Wave.WaveStream.__init__("08-deepforest.wav")
		#audiofile = NAudio.Wave.WaveStream("08-deepforest.wav")
		#waveoutevent.PlaybackStopped += disposer
		waveoutevent.Init(audiofile)
		waveoutevent.Play()
	def VSTBUTTON(self,event):
		pass
		
	def PANBUTTON(self,event):
		global waveoutevent
		waveoutevent.Pause()
	def PANBUTTON2(self,event):
		global waveoutevent
		waveoutevent.Play()
	def SPAWNRECORDER(self,event):
		global recordbox
		recordbox = FileMgr(self, 9999,"simultaneous recorder")
		recordbox.Show()
	def OnClose(self,event):
		#pygame.quit()
		print("Don't close this window.")
		#self.Destroy()
		#self.Quit()

class PygameDisplay(wx.Window):
	def __init__(self, parent, ID):
		wx.Window.__init__(self, parent, ID)
		self.parent = parent
		self.hwnd = self.GetHandle()

		self.size = self.GetSize()
		#print(self.size)
		self.size_dirty = True

		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_TIMER, self.Update, self.timer)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		
		#
		self.Bind(wx.EVT_LEFT_DOWN, self.CLICKH)
		self.Bind(wx.EVT_RIGHT_DOWN, self.CLICKR)
		self.Bind(wx.EVT_LEFT_UP, self.CLICKUP)
		self.Bind(wx.EVT_RIGHT_UP, self.CLICKUPR)
		self.Bind(wx.EVT_MOTION, self.MOTION)
		#self.Bind(wx.EVT_CLOSE, self.OnClose)

		self.fps = 60.0
		self.timespacing = 1000.0 / self.fps
		self.timer.Start(self.timespacing, False)

		self.linespacing = 5
		
		self.FILELIST = []
		self.LOADLIST = []
		self.mHELD = 0
		self.mHELDr = 0
		self.xLAST = 0
		self.yLAST = 0
		
		#self.COLORA = pygame.Color(0,128,256,a=100)
		#self.COLORA = pygame.Color(256,256,256)
		self.COLORA = (0,128,256,100)
		self.COLORA = (0,128,256)
		#print("self.screen is " + self.screen)
		pygame.init() #needed for font to work
		self.screen = pygame.Surface((500,500))
		
		self.font1 = pygame.font.SysFont("agencyfb",12,False,False)
		global hippie
		hippie = pygame.font.Font('magipsx.TTF',12)
		
	def getSURF(self):
		return self.screen
	def PICKL(self):
		#need to save the objects for self.FILELIST, self.LOADLIST, and globals()["img"+str(i)]
		#as well as globals()["img"+str(i)+"x"] and globals()["img"+str(i)+"y"]
		file1 = open("filelist.p","wb")
		file2= open("loadlist.p","wb")
		#pickle.dump(self.FILELIST,open("filelist.p","wb"))
		self.FILELIST_2 = []
		for i in range(len(self.FILELIST)):
			self.FILELIST_2.append([self.FILELIST[i][0],self.FILELIST[i][1],0,self.FILELIST[i][3],self.FILELIST[i][4],self.FILELIST[i][5] ])
		#pickle.dump(self.FILELIST,file1)
		pickle.dump(self.FILELIST_2,file1)
		#pickle.dump(self.LOADLIST,open("loadlist.p","wb"))
		pickle.dump(self.LOADLIST,file2)
		file1.close()
		file2.close()
		#for i in range(len(self.FILELIST)):
			#pass
		
	def UNPICKL(self):
		file1 = open("filelist.p","rb")
		file2 = open("loadlist.p","rb")
		#self.FILELIST = pickle.load(open("filelist.p","rb"))
		self.FILELIST = pickle.load(file1)
		#self.LOADLIST = pickle.load(open("loadlist.p","rb"))
		self.LOADLIST = pickle.load(file2)
		file1.close()
		file2.close()
	def CLICKH(self,event):
		self.mHELD = 1
		#print(event)
		#print(dir(event))
		print("click init: " + str(event.X) + " " + str(event.Y))
		#print(event.Y)
		
		##pygame.draw.aaline(self.screen,(256,128,256),(self.xLAST,self.yLAST),(event.X,event.Y))
		self.xLAST = event.X
		self.yLAST = event.Y
		#pygame.draw.aaline(self.screen,(255,255,255),(0,0),(event.X,event.Y))
		
	def CLICKUP(self,event):
		self.mHELD = 0
		pass
	def CLICKR(self,event):
		self.mHELDr = 1
		self.xLAST = event.X
		self.yLAST = event.Y
		
	def CLICKUPR(self,event):
		self.mHELDr = 0
		if wx.GetKeyState(wx.WXK_CONTROL):
			for i in range(len(self.FILELIST)):
				###if (event.X >= globals()["img"+str(i)+"x"]) and (event.X <= (40 + globals()["img"+str(i)+"x"])):
				if (event.X >= self.FILELIST[i][3]) and (event.X <= (40 + self.FILELIST[i][3])):
					###if (event.Y >= globals()["img"+str(i)+"y"]) and (event.Y <= (40 + globals()["img"+str(i)+"y"])):
					if (event.Y >= self.FILELIST[i][4]) and (event.Y <= (40 + self.FILELIST[i][4])):
						if os.path.isfile(self.FILELIST[i][0]):
							os.system('"' + self.FILELIST[i][0] + '"')
						if os.path.isdir(self.FILELIST[i][0]):
							os.system("cmd /c explorer " + '"' + self.FILELIST[i][0] + '"')
	def MOTION(self,event):
		if self.mHELD == 1:
			if self.size_dirty:
				self.screen = pygame.Surface(self.size, 0, 32)
				self.size_dirty = False
			cur = 0
		#self.screen.fill((0,0,0))
			w, h = self.screen.get_size()
			print("x" + str(event.X) + " y" + str(event.Y))
			pygame.draw.aaline(self.screen,(0,128,255,128),(self.xLAST,self.yLAST),(event.X,event.Y))
			self.xLAST = event.X
			self.yLAST = event.Y
		pass
		if self.mHELDr == 1:
			for i in range(len(self.FILELIST)):
				###if (event.X >= globals()["img"+str(i)+"x"]) and (event.X <= (40 + globals()["img"+str(i)+"x"])):
				if (event.X >= self.FILELIST[i][3]) and (event.X <= (40 + self.FILELIST[i][3])):
					###if (event.Y >= globals()["img"+str(i)+"y"]) and (event.Y <= (40 + globals()["img"+str(i)+"y"])):
					if (event.Y >= self.FILELIST[i][4]) and (event.Y <= (40 + self.FILELIST[i][4])):
						###globals()["img"+str(i)+"x"] = globals()["img"+str(i)+"x"] + (event.X - self.xLAST)
						self.FILELIST[i][3] = self.FILELIST[i][3] + (event.X - self.xLAST)
						###globals()["img"+str(i)+"y"] = globals()["img"+str(i)+"y"] + (event.Y - self.yLAST)
						self.FILELIST[i][4] = self.FILELIST[i][4] + (event.Y - self.yLAST)
			#move song bar?
			global s1pos
			global s1posy
			if (event.X >= s1pos) and (event.X <= s1pos + 400):
				if (event.Y >= s1posy) and (event.Y <= s1posy + 40):
					s1pos = s1pos + event.X - self.xLAST
					s1posy = s1posy + event.Y - self.yLAST
			self.xLAST = event.X
			self.yLAST = event.Y
			#check collision somehow
		
	def UI1(self):
		#print('ui1 thread')
		self.screen2 = self.screen
		self.screen.blit(self.screen2,(0,0))
	def UI2(self):
		self.screen.blit(self.newsurf,(0,0))
	def CELL1(self):
		self.newsurf = pygame.Surface((800,300))
		self.newsurfx = 0
		self.newsurfy = 0
		self.newsurfxv = 0
		self.newsurfyv = 0
		self.newsurf.set_at((0,0),(255,0,0))
		self.newsurf.set_at((2,0),(0,255,0))
		self.newsurf.set_at((1,1),(0,0,255))
		self.newsurf.set_at((2,2),(255,0,0))
		self.newsurf.set_at((0,2),(255,0,0))
		
		#print(dir(self.newsurf))
		#pdb.set_trace()
		#self.CELL1frame = pygame.Surface.fill(pygame.Surface((500,500),pygame.Color(255,255,255,0)))
	def CELL1update(self):
		self.newsurfx = self.newsurfx + self.newsurfxv
		self.newsurfy = self.newsurfy + self.newsurfyv
	def SONG1PROGRESS(self):
		self.song1surf = pygame.Surface((400,40))
		if not ('s1pos' in globals()):
			global s1pos
			s1pos = 0
			global s1posy
			s1posy = 0
		try:
			locala = waveoutevent.GetPosition() / 2000
		except:
			locala = 5
		self.song1surf.fill((0,64,128),pygame.Rect(0,0,locala-400,2))
		self.song1surf.fill((5,34,98),pygame.Rect(0,2,locala-800,2))
		self.song1surf.fill((10,34,98),pygame.Rect(0,4,locala-1200,2))
		self.song1surf.fill((15,34,98),pygame.Rect(0,6,locala-1600,2))
		self.song1surf.fill((20,34,98),pygame.Rect(0,8,locala-2000,2))
		self.song1surf.fill((25,34,98),pygame.Rect(0,10,locala-2400,2))
		self.song1surf.fill((30,34,98),pygame.Rect(0,12,locala-2800,2))
		self.song1surf.fill((35,34,98),pygame.Rect(0,14,locala-3200,2))
		self.song1surf.fill((40,34,98),pygame.Rect(0,16,locala-3600,2))
		self.song1surf.fill((35,34,98),pygame.Rect(0,18,locala-4000,2))
		self.song1surf.fill((30,34,98),pygame.Rect(0,20,locala-4400,2))
		self.song1surf.fill((25,34,98),pygame.Rect(0,22,locala-4800,2))
		self.song1surf.fill((20,34,98),pygame.Rect(0,24,locala-5200,2))
		self.song1surf.fill((16,34,98),pygame.Rect(0,26,locala-5600,2))
		self.song1surf.fill((10,34,98),pygame.Rect(0,28,locala-6000,2))
		self.song1surf.fill((5,34,98),pygame.Rect(0,30,locala-6400,2))
		self.song1surf.fill((4,34,98),pygame.Rect(0,32,locala-6800,2))
		self.song1surf.fill((0,34,98),pygame.Rect(0,34,locala-7200,2))
		self.song1surf.fill((0,34,98),pygame.Rect(0,36,locala-7600,2))
		self.song1surf.fill((0,34,98),pygame.Rect(0,38,locala-8000,2))
		
		#self.song1surf.fill((0,75,139),(400,20))
		self.screen.blit(self.song1surf,(s1pos,s1posy))
		#self.screen.blit(self.song1surf,(s1pos,s1posy))
	def SONG1PROGRESST(self):
		self.song1surft = pygame.Surface((400,40))
		try:
			locala = str(waveoutevent.GetPosition() / 1000)
		except:
			locala = str(5)
		hippietext = hippie.render(locala, True, (128,128,255),None)
		#self.screen.blit(hippietext,(0,0))
		self.screen.blit(hippietext,(s1pos,s1posy))

	def Update(self, event):
# Any update tasks would go here (moving sprites, advancing animation frames etc.)
		self.Redraw()
		
		#self.CELL1()
		#self.CELL1update()
		#self.UI1()
		#self.UI2()
		self.SONG1PROGRESS()
		self.SONG1PROGRESST()

	def File(self, filenamein):
		#large, small = win32gui.ExtractIconEx(filenamein,0)
		filenamein = filenamein.replace('"',"")
		filenameout = "save_icon\\" + justfile(filenamein) + ".bmp"
		#save_icon(filenamein,"save_icon\\" + filenamein + ".bmp")
		self.save_icon(filenamein,filenameout)
		self.FILELIST.append([filenamein,filenameout,0,0,0,0])
		self.LOADLIST.append(0)
		print(self.FILELIST)
		for i in range(len(self.FILELIST)):
			print(self.FILELIST[i])
			
	def File2(self, filenamein):
		#modify File to work with directories
		filenamein = filenamein.replace('"',"")
		if os.path.isdir(filenamein):
			self.LOADLIST.append(0)
			foldericon = "folder40x40b.png"
			self.FILELIST.append([filenamein,foldericon,0,0,0,0])
		if os.path.isfile(filenamein):
			filenameout = "save_icon\\" + justfile(filenamein) + ".bmp"
		#save_icon(filenamein,"save_icon\\" + filenamein + ".bmp")
			self.save_icon(filenamein,filenameout)
			self.FILELIST.append([filenamein,filenameout,0,0,0,0])
			self.LOADLIST.append(0)
			#print(self.FILELIST)
			#for i in range(len(self.FILELIST)):
				#print(self.FILELIST[i])
		
	def save_iconfallback(self,exe_file,out_file):
		someint, exename = win32api.FindExecutable(exe_file)
		print(exename)
		#pdb.set_trace()
		self.save_icon(exename,out_file)
		
	def save_icon(self, exe_file, out_file):
		ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
		ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)

		#
		try:
			large, small = win32gui.ExtractIconEx(exe_file, 0)
			win32gui.DestroyIcon(large[0])
		except:
			print("icon wasnt exe")
			self.save_iconfallback(exe_file,out_file)
			return None

		hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
		hbmp = win32ui.CreateBitmap()
		hbmp.CreateCompatibleBitmap( hdc, ico_x, ico_y )
		hdc = hdc.CreateCompatibleDC()

		hdc.SelectObject( hbmp )
		hdc.DrawIcon( (0,0), small[0] )
		hbmp.SaveBitmapFile( hdc, out_file )
		
	def LOADFILES(self):
		for i in range(len(self.FILELIST)):
			if self.LOADLIST[i] != 1:
				self.FILELIST[i][2] = pygame.image.load(self.FILELIST[i][1])
				#globals()["img"+str(i)] = pygame.image.load(self.FILELIST[i][1])
				#222
				self.FILELIST[i][3] = 100 #3 = x
				self.FILELIST[i][4] = 100 #4 = y
				self.FILELIST[i][5] = 1 #loadlist replacement is 5 in filelist
				#globals()["img"+str(i)+"x"] = 100
				#globals()["img"+str(i)+"y"] = 100
				self.LOADLIST[i] = 1
			if self.FILELIST[i][2] == 0:
				self.FILELIST[i][2] = pygame.image.load(self.FILELIST[i][1])
		
	def DRAWFILES(self):
		for i in range(len(self.FILELIST)):
			#self.screen.blit(globals()["img"+i],(100,100))
			
			#self.screen.blit(globals()["img"+str(i)],(100,100))
			#222 ^
			###self.screen.blit(globals()["img"+str(i)],(globals()["img"+str(i)+"x"],globals()["img"+str(i)+"y"]) )
			self.screen.blit(self.FILELIST[i][2],(self.FILELIST[i][3],self.FILELIST[i][4]) )
			#ftemp = pygame.font.Font.render(self.FILELIST[0])
			text1 = self.font1.render(self.FILELIST[i][0],True,(255,255,255))
			self.screen.blit(text1,(self.FILELIST[i][3],self.FILELIST[i][4]+40))
			#self.screen.blit(ftemp,(self.FILELIST[i][3],self.FILELIST[i][4]+40))
			
		#for i in range(len(self.FILELIST)):
			#img = pygame.image.load(self.FILELIST[i][1])
			#self.screen.blit(img,(100,100))
	def BLANK(self):
		self.screen.fill((0,0,0))
	def Redraw(self):
		if self.size_dirty:
			self.screen = pygame.Surface(self.size, 0, 32)
			self.size_dirty = False
		cur = 0
		#self.screen.fill((0,0,0))
		w, h = self.screen.get_size()
		'''
		while cur <= h:
			pygame.draw.aaline(self.screen, (255, 255, 255), (0, h - cur), (cur, 0))

			cur += self.linespacing
			
		'''
		#pygame.draw.circle(self.screen,(255,255,255),(400,400),50)
		self.LOADFILES()
		self.DRAWFILES()

		s = pygame.image.tostring(self.screen, 'RGB')  # Convert the surface to an RGB string
		img = wx.Image(self.size[0], self.size[1], s)  # Load this string into a wx image
		bmp = wx.Bitmap(img)  # Get the image in bitmap form
		dc = wx.ClientDC(self)  # Device context for drawing the bitmap
		dc.DrawBitmap(bmp, 0, 0, False)  # Blit the bitmap image to the display
		del dc

	def OnPaint(self, event):
		self.Redraw()
		event.Skip()  # Make sure the parent frame gets told to redraw as well

	def OnSize(self, event):
		self.size = self.GetSize()
		self.size_dirty = True

	def Kill(self, event):
		self.Unbind(event = wx.EVT_PAINT, handler = self.OnPaint)
		self.Unbind(event = wx.EVT_TIMER, handler = self.Update, source = self.timer)
		
	def OnClose(self, event):
		if event.CanVeto() and self.fileNotSaved:
			if wx.MessageBox("The file has not been saved... continue closing?", "Please confirm", wx.ICON_QUESTION | wx.YES_NO) != wx.YES:
				event.Veto()
				return
		print("onclose")
		pygame.quit()
		self.Destroy()
# Make sure Pygame can't be asked to redraw /before/ quitting by unbinding all methods which
# call the Redraw() method
# (Otherwise wx seems to call Draw between quitting Pygame and destroying the frame)
# This may or may not be necessary now that Pygame is just drawing to surfaces

class SciteBox(wx.stc.StyledTextCtrl):
	def __init__(self, parent, id):
		wx.stc.StyledTextCtrl.__init__(self, parent, id)

class SciteBoxRight(wx.stc.StyledTextCtrl):
	def __init__(self, parent, id):
		wx.stc.StyledTextCtrl.__init__(self, parent, id)

class TextFrame(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__(self, parent, 8008, size = (800, 700))
		self.SetTitle("Textr")
		self.topsplitter = wx.SplitterWindow(self,ID_SPLITTER,pos=wx.Point(0,0),size=wx.Size(400,400),style=wx.SP_BORDER,name="TopSplitter")
		self.splitter = wx.SplitterWindow(self.topsplitter, ID_SPLITTER,pos=wx.Point(0,0),size=wx.Size(400,400),style=wx.SP_BORDER,name="Splitter")
		self.scite1 = SciteBox(self.splitter,8200)
		self.scite2 = SciteBoxRight(self.splitter,8250)
		self.scite3 = SciteBox(self.topsplitter, 8251)
		self.splitter.SplitVertically(self.scite1,self.scite2)
		self.topsplitter.SplitHorizontally(self.splitter,self.scite3)
		self.tbtext = self.CreateToolBar(wx.TB_HORIZONTAL | wx.TB_FLAT)
		self.btn1 = self.tbtext.AddTool(8401,"L",wx.Bitmap("folder.png"))
		self.btn2 = self.tbtext.AddTool(8402,"T",wx.Bitmap("timer.png"))
		self.btn3 = self.tbtext.AddTool(8403,"S",wx.Bitmap("floopy16x16.png"))
		self.btn4 = self.tbtext.AddTool(8404,"U",wx.Bitmap("uparr.png"))
		self.btn5 = self.tbtext.AddTool(8405,"D",wx.Bitmap("dnarr.png"))
		#second set of arrows doesn't exclude chr(10)
		self.btn6 = self.tbtext.AddTool(8406,"U",wx.Bitmap("uparr.png"))
		self.btn7 = self.tbtext.AddTool(8407,"D",wx.Bitmap("dnarr.png"))
		self.btn8 = self.tbtext.AddTool(8408,"S",wx.Bitmap("spiral1.png"))
		self.btn9 = self.tbtext.AddTool(8409,"S",wx.Bitmap("spiral2.png"))
		self.btn10 = self.tbtext.AddTool(8410,"S",wx.Bitmap("spiral3.png"))
		self.btn11 = self.tbtext.AddTool(8411,"S",wx.Bitmap("n64.png"))
		self.btn12 = self.tbtext.AddTool(8412,"S",wx.Bitmap("n64i.png"))
		self.btn13 = self.tbtext.AddTool(8413,"S",wx.Bitmap("globalcortex.png"))
		self.tbtext.Realize()
		self.Bind(wx.EVT_TOOL,self.b1proc,self.btn1)
		self.Bind(wx.EVT_TOOL,self.b2proc,self.btn2)
		self.Bind(wx.EVT_TOOL,self.b3proc,self.btn3)
		self.Bind(wx.EVT_TOOL,self.b4proc,self.btn4)
		self.Bind(wx.EVT_TOOL,self.b5proc,self.btn5)
		self.Bind(wx.EVT_TOOL,self.b6proc,self.btn6)
		self.Bind(wx.EVT_TOOL,self.b7proc,self.btn7)
		self.Bind(wx.EVT_TOOL,self.b8proc,self.btn8)
		self.Bind(wx.EVT_TOOL,self.b9proc,self.btn9)
		self.Bind(wx.EVT_TOOL,self.b10proc,self.btn10)
		self.Bind(wx.EVT_TOOL,self.b11proc,self.btn11)
		self.Bind(wx.EVT_TOOL,self.b12proc,self.btn12)
		self.Bind(wx.EVT_TOOL,self.b13proc,self.btn13)
		#pdb.set_trace()
		self.textL = ""
		self.textMod = ""
	def b1proc(self, event):
		print("hello my future girlfriend")
	def b2proc(self, event):
		#self.scite1.SelectAll()
		#self.scite1.Copy()
		self.textL = self.scite1.GetText()
		print(self.textL)
		self.scite2.Text = self.textL
	def b3proc(self, event):
		dlg = wx.TextEntryDialog(self,'Save File To Path:','?')
		if dlg.ShowModal() == wx.ID_OK:
			filename_0 = dlg.GetValue()
		dlg.Destroy()
		self.scite1.SaveFile(filename_0)
	def b4proc(self, event):
		self.textMod = self.scite2.Text
		self.textMod2 = ""
		for i in range(len(self.textMod)):
			if ord(self.textMod[i]) != 10:
				calcbox = chr(ord(self.textMod[i]) + 1)
				self.textMod2 = self.textMod2 + calcbox
			else:
				self.textMod2 = self.textMod2 + self.textMod[i]
		#print(self.textMod2)
		self.scite2.Text = self.textMod2
	def b5proc(self, event):
		self.textMod = self.scite2.Text
		self.textMod2 = ""
		for i in range(len(self.textMod)):
			if ord(self.textMod[i]) != 10:
				calcbox = chr(ord(self.textMod[i]) + -1)
				self.textMod2 = self.textMod2 + calcbox
			else:
				self.textMod2 = self.textMod2 + self.textMod[i]
		#print(self.textMod2)
		self.scite2.Text = self.textMod2
	def b6proc(self,event):
		#same as b4proc original
		self.textMod = self.scite2.Text
		self.textMod2 = ""
		for i in range(len(self.textMod)):
			calcbox = chr(ord(self.textMod[i]) + 1)
			self.textMod2 = self.textMod2 + calcbox
		self.scite2.Text = self.textMod2
	def b7proc(self,event):
		self.textMod = self.scite2.Text
		self.textMod2 = ""
		for i in range(len(self.textMod)):
			calcbox = chr(ord(self.textMod[i]) + -1)
			self.textMod2 = self.textMod2 + calcbox
		self.scite2.Text = self.textMod2
	def b8proc(self,event):
		pass #numbers separated by space in scite2 to chrs in scite3
		self.textMod = self.scite2.Text
		self.textMod2 = ""
		templist = self.textMod.split(" ")
		for i in range(len(templist)):
			try:
				self.textMod2 = self.textMod2 + chr(int(templist[i]))
			except:
				pass
		self.scite3.Text = self.textMod2
	def b9proc(self,event):
		pass #scite2.Text to scite3.Text with the transformation of just Chr()
		#actually... reverse above, chrs to numbers separated by space
		self.textMod = self.scite3.Text
		self.textMod2 = ""
		templist = []
		for i in range(len(self.textMod)):
			self.textMod2 = self.textMod2 + str(ord(self.textMod[i])) + " "
		self.scite2.Text = self.textMod2
		
	def b10proc(self,event):
		pass #lets take selection in scite2 and interpret it as an int, increment it by one, and put " " + _it_ at the end
		self.textMod = self.scite2.GetSelectedText()
		try:
			self.textMod2 = str(int(self.textMod) + 1)
			print(self.textMod2)
			self.scite2.CharRight()
			self.scite2.CharRight()
			self.scite2.WriteText(" " + self.textMod2)
		except:
			self.scite2.WordLeftExtend()
			self.textMod = self.scite2.GetSelectedText()
			self.textMod2 = str(int(self.textMod) + 1)
			self.scite2.CharRight()
			self.scite2.CharRight()
			self.scite2.WriteText(" " + self.textMod2)
	def b11proc(self,event):
		self.textMod = self.scite1.Text
		self.textMod = base64.b64decode(self.textMod)
		self.scite2.Text = self.textMod
	def b12proc(self,event):
		self.textMod = self.scite2.Text
		self.textMod = base64.b64encode(bytes(self.textMod,'utf-8'))
		self.scite1.Text = self.textMod
	def b13proc(self,event):
		self.textMod = self.scite2.Text
		self.textLST = self.textMod.split(' ')
		self.procLST = []
		for i in range(len(self.textLST)):
			self.procLST.append(hex(int(self.textLST[i])))
		self.scite1.Text = (' ').join(self.procLST)
	def b14proc(self,event):
		pass
		#idea: convert to decimal, add 00, convert back to unicode letters
		#◤♈⚬✐
		#yo waddup > ⽄⭜ಀ⹼◤✐✐ⶴ⯀
		#9700 9800 9900 10000
		
		#print(dir(event))
		#theevent = event
		#pdb.set_trace()
		#theevent.GetClassName() => wxCommandEvent
		#https://docs.wxpython.org/wx.stc.StyledTextCtrl.html
	#https://wiki.wxwidgets.org/WxStyledTextCtrl#Deriving_from_ScintillaWX
	

hideConsole()
app=wx.App(0)
filething = FileMgr1(None,-1,'File Mgr')
filething.SetIcon(wx.Icon("icon.png"))
filething.splitter = wx.SplitterWindow(filething, ID_SPLITTER,style=wx.SP_BORDER)
filething.splitter.SetMinimumPaneSize(50)
p1 = MyListCtrl(filething.splitter,4646)
p2 = MyListCtrl(filething.splitter,6969)
filething.splitter.SplitVertically(p1,p2)
filething.Bind(wx.EVT_SIZE,filething.OnSize)
filething.Bind(wx.EVT_SPLITTER_DCLICK,filething.OnDoubleClick,id=ID_SPLITTER)
filemenu=wx.Menu()
filemenu.Append(ID_EXIT,"E&xit","Terminate the program")
editmenu = wx.Menu()
netmenu = wx.Menu()
showmenu = wx.Menu()
#would like to add
#showmenu1 = wx.MenuItem(showmenu, wx.ID_ANY, "Explorer L")
showmenu1 = wx.MenuItem(showmenu, 5050, "Explorer L")
showmenu2 = wx.MenuItem(showmenu, 5056, "Explorer R")
showmenu0 = wx.MenuItem(showmenu, 5075, "Task Manager")
showmenu4 = wx.MenuItem(showmenu, 5076, "Text")
id1 = wx.ID_ANY
showmenu.Append(showmenu0)
showmenu.Append(showmenu1)
showmenu.Append(showmenu2)
#https://www.tutorialspoint.com/wxpython/wxpython_menus.htm
#changes end here
configmenu = wx.Menu()
helpmenu = wx.Menu()

menuBar = wx.MenuBar()
menuBar.Append(filemenu,"&File")
menuBar.Append(editmenu,"&Edit")
menuBar.Append(netmenu,"&Net")
menuBar.Append(showmenu,"&Show")
menuBar.Append(configmenu,"&Config")
menuBar.Append(helpmenu,"&Help")
filething.SetMenuBar(menuBar)
filething.Bind(wx.EVT_MENU,filething.OnExit,id=ID_EXIT)

filething.Bind(wx.EVT_MENU,filething.onFuncL,id=5050)
filething.Bind(wx.EVT_MENU,filething.onFuncR,id=5056)
filething.Bind(wx.EVT_MENU,filething.startTask,id=5075)
filething.Bind(wx.EVT_MENU,filething.startText,id=5076)
#https://wiki.wxpython.org/self.Bind%20vs.%20self.button.Bind

filething.Bind(wx.EVT_LIST_ITEM_ACTIVATED, filething.OnClick, p1)
filething.Bind(wx.EVT_LIST_ITEM_ACTIVATED, filething.OnClick, p2)
		
tb=filething.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)
#buttonL = wx.Button(tb, 701, "LDir")
#buttonR = wx.Button(tb, 702, "RDir")
bt1 = tb.AddTool(701,"DirL",wx.Bitmap("folder.png"))
bt2 = tb.AddTool(702,"DirR",wx.Bitmap("folder.png"))
bt3 = tb.AddTool(703,"TaskMgr",wx.Bitmap("up16.png"))
bt4 = tb.AddTool(704, "Text",wx.Bitmap("up16.png"))
bt5 = tb.AddTool(705, "Grafx",wx.Bitmap("up16.png"))
filething.Bind(wx.EVT_TOOL,filething.DirL,bt1)
filething.Bind(wx.EVT_TOOL,filething.DirR,bt2)
filething.Bind(wx.EVT_TOOL,filething.startTask,bt3)
filething.Bind(wx.EVT_TOOL,filething.startText,bt4)
filething.Bind(wx.EVT_TOOL,filething.startG,bt5)
#print(dir(tb))
#tb.AddChild(button2)
tb.Realize()
filething.sizer2=wx.BoxSizer(wx.HORIZONTAL)
#filething.sb=filething.CreateStatusBar()
filething.sb.SetStatusText(os.getcwd())
filething.Center()
filething.Show(True)

#print(wx.version())
#4.0.7.post2 msw (phoenix) wxWidgets 3.0.5
#import sys
#print(sys.version_info)
#sys.version_info(major=2, minor=7, micro=17, releaselevel='final', serial=0)
app.MainLoop()
	
#https://www.pygame.org/project-Pygame+embedded+in+wxPython-1580-.html
#https://www.semicolonworld.com/question/59548/embedding-a-pygame-window-into-a-tkinter-or-wxpython-frame
#to do
	
