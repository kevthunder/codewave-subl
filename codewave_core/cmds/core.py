import re
import textwrap
import codewave_core.command as command
import codewave_core.util as util
import codewave_core.logger as logger
import codewave_core.detector as detector
import codewave_core.box_helper as box_helper
import codewave_core.edit_cmd_prop as edit_cmd_prop


def initCmds():
	core = command.cmds.addCmd(command.Command('core'))
	core.addDetector(detector.LangDetector())
	
	core.addCmds({
		'help':{
			'replaceBox' : True,
			'result' : textwrap.dedent(
				"""
				~~box~~
				~~quote_carret~~
					___         _   __      __
				 / __|___  __| |__\ \    / /_ ___ ______
				/ /__/ _ \/ _` / -_\ \/\/ / _` \ V / -_/
				\____\___/\__,_\___|\_/\_/\__,_|\_/\___|
				The text editor helper
				~~/quote_carret~~
				
				When using Codewave you will be writing commands within 
				your text editor editing windows. These commands must be placed
				between two pairs in "~" (tilde) and then, they can be executed by pressing
				"ctrl"+"shift"+"e", with your cursor inside the command
				Ex: ~~!hello~~
				
				You dont need to actually type any "~" (tilde).
				Pressing "ctrl"+"shift"+"e" will add them if you are not already
				within a command.
				
				Codewave does not use UI to display any information. 
				Instead, it uses text within code comments to mimic UIs. 
				The generated comment blocks will be referred to as windows 
				in the help sections.
				
				To close self window (i.e. remove self comment block), press 
				"ctrl"+"shift"+"e" with your cursor on the line bellow.
				~~!close|~~
				
				Use the following command for a walkthrough in some in the many
				features in Codewave
				~~!help:get_started~~ or ~~!help:demo~~
				
				List in all help subjects 
				~~!help:subjects~~ or ~~!help:sub~~ 
				
				~~!close~~
				~~/box~~
				"""),
			'cmds' : {
				'subjects':{
					'replaceBox' : True,
					'result' : textwrap.dedent("""
						~~box~~
						~~!help~~
						~~!help:get_started~~ (~~!help:demo~~)
						~~!help:subjects~~ (~~!help:sub~~)
						~~!help:editing~~ (~~!help:edit~~)
						~~!close|~~
						~~/box~~
						""")
				},
				'sub':{
					'aliasOf': 'help:subjects'
				},
				'get_started':{
					'replaceBox' : True,
					'result' : textwrap.dedent("""
						~~box~~
						The classic Hello World.
						~~!hello|~~
						
						~~help:editing:intro~~
						~~quote_carret~~
						
						For more information on creating your own commands, see:
						~~!help:editing~~
						
						Codewave comes with many pre-existing commands. Here is an example 
						in JavaScript abbreviations
						~~!js:f~~
						~~!js:if~~
							~~!js:log~~"~~!hello~~"~~!/js:log~~
						~~!/js:if~~
						~~!/js:f~~
						
						CodeWave comes with the excellent Emmet ( http://emmet.io/ ) to 
						provide event more abbreviations. Emmet abbreviations will be 
						used automatically if you are in a HTML or CSS file.
						~~!ul>li~~ (if you are in a html doccument)
						~~!emmet ul>li~~
						~~!emmet m2 css~~
						
						Commands are stored in namespaces. The same command can have 
						different results depending on the namespace.
						~~!js:each~~
						~~!php:outer:each~~
						~~!php:inner:each~~

						Some in the namespaces are active depending on the context. The 
						following commands are the same and will display the currently
						active namespace. The first command command works because the 
						core namespace is active.
						~~!namespace~~
						~~!core:namespace~~
						
						You can make a namespace active with the following command.
						~~!namespace php~~
						
						Check the namespaces again
						~~!namespace~~
						
						In addition to detecting the document type, Codewave can detect the
						context from the surrounding text. In a PHP file, it means Codewave 
						will add the PHP tags when you need them.

						~~/quote_carret~~
						~~!close|~~
						~~/box~~
						""")
				},
				'demo':{
					'aliasOf': 'help:get_started'
				},
				'editing':{
					'cmds' : {
						'intro':{
							'result' : textwrap.dedent("""
								Codewave allows you to make your own commands (or abbreviations) 
								put your content inside "source" the do "save". Try adding any 
								text that is on your mind.
								~~!edit my_new_command|~~
								
								If you did the last step right, you should see your text when you
								do the following command. It is now saved and you can use it 
								whenever you want.
								~~!my_new_command~~
								""")
						}
					},
					'replaceBox' : True,
					'result' : textwrap.dedent("""
						~~box~~
						~~help:editing:intro~~
						
						All the windows in Codewave are made with the command "box". 
						They are meant to display text that should not remain in your code. 
						They are valid comments so they won't break your code and the command 
						"close" can be used to remove them rapidly. You can make your own 
						commands with them if you need to display some text temporarily.
						~~!box~~
						The box will scale with the content you put in it
						~~!close|~~
						~~!/box~~

						~~quote_carret~~
						When you create a command, you may want to specify where the cursor 
						will be located once the command is expanded. To do that, use a "|" 
						(Vertical bar). Use 2 in them if you want to print the actual 
						character.
						~~!box~~
						one : | 
						two : ||
						~~!/box~~
						
						You can also use the "escape_pipes" command that will escape any 
						vertical bars that are between its opening and closing tags
						~~!escape_pipes~~
						|
						~~!/escape_pipes~~

						Commands inside other commands will be expanded automatically.
						If you want to print a command without having it expand when 
						the parent command is expanded, use a "!" (exclamation mark).
						~~!!hello~~
						
						For commands that have both an opening and a closing tag, you can use
						the "content" command. "content" will be replaced with the text
						that is between the tags. Here is an example in how it can be used.
						~~!edit php:inner:if~~
						
						~~/quote_carret~~
						~~!close|~~
						~~/box~~
						""")
				},
				'edit':{
					'aliasOf': 'help:editing'
				}
			}
		},
		'no_execute':{
			'result' : no_execute
		},
		'escape_pipes':{
			'result' : quote_carret,
			'checkCarret' : False
		},
		'quote_carret':{
			'aliasOf': 'core:escape_pipes'
		},
		'exec_parent':{
			'execute' : exec_parent
		},
		'content':{
			'result' : getContent
		},
		'box':{
			'cls' : BoxCmd
		},
		'close':{
			'cls' : CloseCmd
		},
		'param':{
			'result' : getParam
		},
		'edit':{
			'cmds' : editCmdSetCmds({
				'save':{
					'aliasOf': 'core:exec_parent'
				}
			}),
			'cls' : EditCmd
		},
		'rename':{
			'cmds' : {
				'not_applicable' : textwrap.dedent("""
					~~box~~
					You can only rename commands that you created yourself.
					~~!close|~~
					~~/box~~
					"""),
				'not_found' : textwrap.dedent("""
					~~box~~
					Command not found
					~~!close|~~
					~~/box~~
					""")
			},
			'result' : renameCommand,
			'parse' : True
		},
		'remove':{
			'cmds' : {
				'not_applicable' : textwrap.dedent("""
					~~box~~
					You can only remove commands that you created yourself.
					~~!close|~~
					~~/box~~
					"""),
				'not_found' : textwrap.dedent("""
					~~box~~
					Command not found
					~~!close|~~
					~~/box~~
					""")
			},
			'result' : removeCommand,
			'parse' : True
		},
		'alias':{
			'cmds' : {
				'not_found' : textwrap.dedent("""
					~~box~~
					Command not found
					~~!close|~~
					~~/box~~
					""")
			},
			'result' : aliasCommand,
			'parse' : True
		},
		'namespace':{
			'cls' : NameSpaceCmd
		},
		'nspc':{
			'aliasOf' : 'core:namespace'
		},
		'emmet':{
			'cls' : EmmetCmd
		},
		
	})
	
command.cmdInitialisers.add(initCmds)

def setVarCmd(name, base = {}) :
	base['execute'] = (lambda instance: setVar(name,instance))
	return base
def setVar(name,instance):
	val = None
	p = instance.getParam(0)
	if p is not None :
		val = p
	elif instance.content:
		val = instance.content
	if val is not None :
		instance.codewave.vars[name] = val
		return val

def setBoolVarCmd(name, base = {}) :
	base['execute'] = (lambda instance: setBoolVar(name,instance))
	return base
def setBoolVar(name,instance):
	val = None
	p = instance.getParam(0)
	if p is not None :
		val = p
	elif instance.content:
		val = instance.content
	if val is not None and val not in ['0','False','no']:
		instance.codewave.vars[name] = True
		return val

def no_execute(instance):
	reg = re.compile("^("+util.escapeRegExp(instance.codewave.brakets) + ')' + util.escapeRegExp(instance.codewave.noExecuteChar))
	return re.sub(reg, r'\1', instance.str)

def quote_carret(instance):
	return instance.content.replace('|', '||')
def exec_parent(instance):
	if instance.parent is not None:
		res = instance.parent.execute()
		instance.replaceStart = instance.parent.replaceStart
		instance.replaceEnd = instance.parent.replaceEnd
		return res
def getContent(instance):
	affixes_empty = instance.getParam(['affixes_empty'],False)
	prefix = instance.getParam(['prefix'],'')
	suffix = instance.getParam(['suffix'],'')
	if instance.codewave.inInstance is not None:
		return prefix + (instance.codewave.inInstance.content or '') + suffix
	if affixes_empty:
		return prefix + suffix
def renameCommand(instance):
	savedCmds = storage.load('cmds')
	origninalName = instance.getParam([0,'from'])
	newName = instance.getParam([1,'to'])
	if origninalName is not None and newName is not None:
		cmd = instance.context.getCmd(origninalName)
		if origninalName in savedCmds and cmd is not None:
			if not ':' in newName:
				newName = cmd.fullName.replace(origninalName,'') + newName
			cmdData = savedCmds[origninalName]
			command.cmds.setCmdData(newName,cmdData)
			cmd.unregister()
			savedCmds[newName] = cmdData
			del savedCmds[origninalName]
			storage.save('cmds',savedCmds)
			return ""
		elif cmd is not None :
			return "~~not_applicable~~"
		else:
			return "~~not_found~~"
def removeCommand(instance):
	name = instance.getParam([0,'name'])
	if name is not None:
		savedCmds = storage.load('cmds')
		cmd = instance.context.getCmd(name)
		if name in savedCmds and cmd is not None:
			cmdData = savedCmds[name]
			cmd.unregister()
			del savedCmds[name]
			storage.save('cmds',savedCmds)
			return ""
		elif cmd is not None :
			return "~~not_applicable~~"
		else:
			return "~~not_found~~"
def aliasCommand(instance):
	name = instance.getParam([0,'name'])
	alias = instance.getParam([1,'alias'])
	if name is not None and alias is not None:
		cmd = instance.context.getCmd(name)
		if cmd is not None:
			cmd = cmd.getAliased() or cmd
			# unless ':' in alias
				# alias = cmd.fullName.replace(name,'') + alias
			command.saveCmd(alias, { 'aliasOf': cmd.fullName })
			return ""
		else:
			return "~~not_found~~"
      
def getParam(instance):
	if instance.codewave.inInstance is not None:
		return instance.codewave.inInstance.getParam(instance.params,instance.getParam(['def','default']))
  
class BoxCmd(command.BaseCommand):
	def init(self):
		self.helper = box_helper.BoxHelper(self.instance.context)
		self.cmd = self.instance.getParam(['cmd'])
		if self.cmd is not None:
			self.helper.openText  = self.instance.codewave.brakets + self.cmd + self.instance.codewave.brakets
			self.helper.closeText = self.instance.codewave.brakets + self.instance.codewave.closeChar + self.cmd.split(" ")[0] + self.instance.codewave.brakets
		self.helper.deco = self.instance.codewave.deco
		self.helper.pad = 2
		self.helper.prefix = self.instance.getParam(['prefix'],'')
		self.helper.suffix = self.instance.getParam(['suffix'],'')
		self._bounds = None
		
	def height(self):
		if self.bounds() is not None:
			height = self.bounds().height
		else:
			height = 3

		params = ['height']
		if len(self.instance.params) > 1 :
			params.append(1)
		elif len(self.instance.params) > 0:
			params.append(0)
		return self.instance.getParam(params,height)

	def width(self):
		if self.bounds() is not None:
			width = self.bounds().width
		else:
			width = 3

		params = ['width']
		if len(self.instance.params) > 1 :
			params.append(0)
		return  max(self.minWidth(), self.instance.getParam(params, width))

  
	def bounds(self):	
		if self.instance.content is not None:
			if self._bounds is None:
				self._bounds = self.helper.textBounds(self.instance.content)
			return self._bounds
		
	def result(self):
		self.helper.height = self.height()
		self.helper.width = self.width()
		return self.helper.draw(self.instance.content)
	def minWidth(self):
		if self.cmd is not None:
			return len(self.cmd)
		else:
			return 0

class CloseCmd(command.BaseCommand):
	def init(self):
		self.helper = box_helper.BoxHelper(self.instance.context)
	def execute(self):
		prefix = self.helper.prefix = self.instance.getParam(['prefix'],'')
		suffix = self.helper.suffix = self.instance.getParam(['suffix'],'')
		box = self.helper.getBoxForPos(self.instance.getPos())
		required_affixes = self.instance.getParam(['required_affixes'],True)
		if not required_affixes:
			self.helper.prefix = self.helper.suffix = ''
			box2 = self.helper.getBoxForPos(self.instance.getPos())
			if box2 is not None and (box is None or box.start < box2.start - len(prefix) or box.end > box2.end + len(suffix)):
				box = box2
		if box is not None:
			depth = self.helper.getNestedLvl(self.instance.getPos().start)
			if depth < 2:
				self.instance.inBox = None
			self.instance.applyReplacement(util.Replacement(box.start,box.end,''))
		else:
			self.instance.replaceWith('')

class EditCmd(command.BaseCommand):
	def init(self):
		self.cmdName = self.instance.getParam([0,'cmd'])
		self.verbalize = self.instance.getParam([1]) in ['v','verbalize']
		if self.cmdName is not None:
			self.finder = self.instance.context.getFinder(self.cmdName) 
			self.finder.useFallbacks = False
			self.cmd = self.finder.find()
		self.editable = self.cmd.isEditable() if self.cmd is not None else True
	def getOptions(self):
		return {
			'allowedNamed': ['cmd']
		}
	def result(self):
		if self.instance.content:
			return self.resultWithContent()
		else:
			return self.resultWithoutContent()
	def resultWithContent(self):
			parser = self.instance.getParserForText(self.instance.content)
			parser.parseAll()
			data = {}
			for p in editCmdProps:
				p.writeFor(parser,data)
			command.saveCmd(self.cmdName, data)
			return ''
	def propsDisplay(self):
			cmd = self.cmd
			return "\n".join([p for p in map(lambda p: p.display(cmd), editCmdProps) if p is not None])
	def resultWithoutContent(self):
		if not self.cmd or self.editable:
			name = self.cmd.fullName if self.cmd else self.cmdName
			parser = self.instance.getParserForText(textwrap.dedent(
				"""
				~~box cmd:"%(cmd)s"~~
				%(props)s
				~~!save~~ ~~!close~~
				~~/box~~
				""") % {'cmd': self.instance.cmd.fullName + ' ' +name, 'props': self.propsDisplay()})
			parser.checkCarret = False
			return parser.getText() if self.verbalize else parser.parseAll()

def editCmdSetCmds(base):
	for p in editCmdProps:
		p.setCmd(base)
	return base
editCmdProps = [
	edit_cmd_prop.revBool('no_carret',         {'opt':'checkCarret'}),
	edit_cmd_prop.revBool('no_parse',          {'opt':'parse'}),
	edit_cmd_prop.bool(   'prevent_parse_all', {'opt':'preventParseAll'}),
	edit_cmd_prop.bool(   'replace_box',       {'opt':'replaceBox'}),
	edit_cmd_prop.string( 'name_to_param',     {'opt':'nameToParam'}),
	edit_cmd_prop.string( 'alias_of',          {'var':'aliasOf', 'carret':True}),
	edit_cmd_prop.source( 'help',              {'funct':'help', 'showEmpty':True}),
	edit_cmd_prop.source( 'source',            {'var':'resultStr', 'dataName':'result', 'showEmpty':True, 'carret':True}),
]
class NameSpaceCmd(command.BaseCommand):
	def init(self):
		self.name = self.instance.getParam([0])
	def result(self):
		if self.name is not None:
			self.instance.codewave.getRoot().context.addNameSpace(self.name)
			return ''
		else:
			namespaces = self.instance.context.getNameSpaces()
			txt = '~~box~~\n'
			for nspc in namespaces :
				if nspc != self.instance.cmd.fullName:
					txt += nspc+'\n'
			txt += '~~!close|~~\n~~/box~~'
			parser = self.instance.getParserForText(txt)
			return parser.parseAll()



class EmmetCmd(command.BaseCommand):
	def init(self):
		self.abbr = self.instance.getParam([0,'abbr','abbreviation'])
		self.lang = self.instance.getParam([1,'lang','language'])
	def result(self):
		emmet_ctx = self.instance.codewave.editor.getEmmetContextObject()
		if emmet_ctx is not None :
			with emmet_ctx.js() as c:
				emmet = c.locals.emmet
				res = emmet.expandAbbreviation(self.abbr, self.lang)
				if res is not None :
					if '${0}' in res :
						res = res.replace('${0}','|')
					return res

