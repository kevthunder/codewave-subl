import codewave_core.logger as logger

import codewave_core.util as util

import codewave_core.cmd_instance as cmd_instance
import codewave_core.positioned_cmd_instance as positioned_cmd_instance
import codewave_core.cmd_finder as cmd_finder
import codewave_core.text_parser as text_parser
import codewave_core.closing_promp as closing_promp
import codewave_core.command as command
import codewave_core.context as context
import codewave_core.process as process


class Codewave():
	def __init__(self,editor, **options):
		self.editor = editor
		self.closingPromp = self.context = None
		self.marker = '[[[[codewave_marquer]]]]'
		self.vars = {}
		
		defaults = {
			'brakets' : '~~',
			'deco' : '~',
			'closeChar' : '/',
			'noExecuteChar' : '!',
			'carretChar' : '|',
			'checkCarret' : True,
			'inInstance' : None
		}
		self.parent = options['parent'] if 'parent' in options else None
		
		for key, val in defaults.items():
			if key in options:
				setattr(self,key,options[key])
			elif self.parent is not None and key != 'parent':
				setattr(self,key,getattr(self.parent,key))
			else:
				setattr(self,key,val)
		if self.editor is not None :
			self.editor.bindedTo(self) 

		self.context = context.Context(self)
		if self.inInstance is not None:
			self.context.parent = self.inInstance.context
	def onActivationKey(self):
		self.process = process.Process()
		logger.log('activation key')
		self.runAtCursorPos()
		self.process = None
	def runAtCursorPos(self):
		cmd = self.commandOnCursorPos()
		if cmd is not None :
			cmd.init()
			logger.log(cmd)
			cmd.execute()
		else:
			cpos = self.editor.getCursorPos()
			if cpos['start'] == cpos['end']:
				self.addBrakets(cpos['start'],cpos['end'])
			else:
				self.promptClosingCmd(cpos['start'],cpos['end'])
	def commandOnCursorPos(self):
		cpos = self.editor.getCursorPos()
		return self.commandOnPos(cpos['end'])
	def commandOnPos(self,pos):
		if self.precededByBrakets(pos) and self.followedByBrakets(pos) and self.countPrevBraket(pos) % 2 == 1 :
			prev = pos-len(self.brakets)
			next = pos
		else:
			if self.precededByBrakets(pos) and self.countPrevBraket(pos) % 2 == 0:
				pos -= len(self.brakets)
			prev = self.findPrevBraket(pos)
			if prev is None:
				return None 
			next = self.findNextBraket(pos-1)
			if next is None or self.countPrevBraket(prev) % 2 != 0 :
				return None
		return positioned_cmd_instance.PositionedCmdInstance(self,prev,self.editor.textSubstr(prev,next+len(self.brakets)))
	def nextCmd(self,start = 0):
		pos = start
		beginning = None
		while True:
			f = self.findAnyNext(pos ,[self.brakets,"\n"])
			if f is None:
				break
			pos = f.pos + len(f.str)
			if f.str == self.brakets:
				if beginning is not None:
					return positioned_cmd_instance.PositionedCmdInstance(self, beginning, self.editor.textSubstr(beginning, f.pos+len(self.brakets)))
				else:
					beginning = f.pos
			else:
				beginning = None
		None
	def getEnclosingCmd(self,pos = 0):
		cpos = pos
		closingPrefix = self.brakets + self.closeChar
		while True:
			p = self.findNext(cpos,closingPrefix)
			if p is None:
				return None
			cmd = self.commandOnPos(p+len(closingPrefix))
			if cmd is not None:
				cpos = cmd.getEndPos()
				if cmd.pos < pos:
					return cmd
			else:
				cpos = p+len(closingPrefix)
	def precededByBrakets(self,pos):
		return self.editor.textSubstr(pos-len(self.brakets),pos) == self.brakets
	def followedByBrakets(self,pos):
		return self.editor.textSubstr(pos,pos+len(self.brakets)) == self.brakets
	def countPrevBraket(self,start):
		i = 0
		start = self.findPrevBraket(start)
		while start is not None :
			start = self.findPrevBraket(start)
			i += 1
		return i
	def isEndLine(self,pos):
		return self.editor.textSubstr(pos,pos+1) == "\n" or pos + 1 >= self.editor.textLen()
	def findLineStart(self,pos):
		p = self.findAnyNext(pos ,["\n"], -1)
		return p.pos+1 if p is not None else 0

	def findLineEnd(self,pos): 
		p = self.findAnyNext(pos ,["\n","\r"])
		return p.pos if p is not None else self.editor.textLen()
	def findPrevBraket(self,start):
		return self.findNextBraket(start,-1)
	def findNextBraket(self,start,direction = 1):
		f = self.findAnyNext(start ,[self.brakets,"\n"], direction)
		if f is not None and f.str == self.brakets :
			return f.pos
	def findPrev(self,start,string):
		return self.findNext(start,string,-1)
	def findNext(self,start,string,direction = 1):
		f = self.findAnyNext(start ,[string], direction)
		if f is not None:
			return f.pos 
	def findAnyNext(self,start,strings,direction = 1):
		if direction > 0:
			text = self.editor.textSubstr(start,self.editor.textLen())
		else:
			text = self.editor.textSubstr(0,start)
		bestPos = bestStr = None
		for stri in strings:
			pos = text.find(stri) if direction > 0  else text.rfind(stri)
			if pos != -1:
				if not bestPos is not None or bestPos*direction > pos*direction:
					bestPos = pos
					bestStr = stri
		if bestStr is not None:
			return util.StrPos((bestPos + start if direction > 0 else bestPos),bestStr)
		return None
	def findMatchingPair(self,startPos,opening,closing,direction = 1):
		pos = startPos
		nested = 0
		while True:
			f = self.findAnyNext(pos,[closing,opening],direction)
			if f is None:
				break
			pos = f.pos + (len(f.str) if direction > 0 else 0)
			if f.str == (closing if direction > 0 else opening):
				if nested > 0:
					nested-=1
				else:
					return f
			else:
				nested+=1
		return None
	def addBrakets(self,start, end):
		if start == end:
			self.editor.insertTextAt(self.brakets+self.brakets,start)
		else:
			self.editor.insertTextAt(self.brakets,end)
			self.editor.insertTextAt(self.brakets,start)
		self.editor.setCursorPos(end+len(self.brakets))
	def promptClosingCmd(self,start, end):
		if self.closingPromp is not None:
			self.closingPromp.stop()
		self.closingPromp = closing_promp.ClosingPromp(self,start, end).begin()
	def parseAll(self,recursive = True):
		pos = 0
		while True:
			cmd = self.nextCmd(pos)
			if cmd is None:
				break
			pos = cmd.getEndPos()
			self.editor.setCursorPos(pos)
			cmd.init()
			if recursive and cmd.content is not None and (cmd.getCmd() is None or not cmd.getOption('preventParseAll')):
				parser = Codewave(text_parser.TextParser(cmd.content), parent=self)
				cmd.content = parser.parseAll()
			if cmd.execute() is not None:
				if cmd.replaceEnd is not None:
					pos = cmd.replaceEnd
				else:
					pos = self.editor.getCursorPos().end
		return self.getText()
	def getText(self):
		return self.editor.text
	def isRoot(self):
		return self.parent is None and (self.inInstance is None or self.inInstance.finder is None)
	def getRoot(self):
		if self.isRoot:
			return self
		elif self.parent is not None:
			return self.parent.getRoot()
		elif self.inInstance is not None:
			return self.inInstance.codewave.getRoot()
	def removeCarret(self,txt):
		return txt.replace(self.carretChar+self.carretChar, '[[[[quoted_carret]]]]') \
							.replace(self.carretChar, '') \
							.replace('[[[[quoted_carret]]]]', self.carretChar)
	def getCarretPos(self,txt):
		txt = txt.replace(self.carretChar+self.carretChar, ' ')
		if self.carretChar in txt :
			return txt.index(self.carretChar)
	
	def regMarker(self,flags=0):
		return re.compile(util.escapeRegExp(self.marker), flags)
	def removeMarkers(self,text):
		return text.replace(self.marker,'')

def init():
	command.initCmds()
	command.loadCmds()