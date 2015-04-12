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
				
				When using Codewave you will be writing commands directly within 
				your text editor editing windows. These commands must be placed
				between two pairs in "~" (tilde) and then with you text either 
				inside or at the command, they can be executed by pressing 
				"ctrl"+"shift"+"e".
				Ex: ~~!hello~~
				
				One good thing about codewave is that you dont need to actually
				type any "~" (tilde), because pressing "ctrl"+"shift"+"e" will
				add them if you are not allready within a command
				
				Codewave does not relly use UI to display any information. 
				instead, it uses text within code comments to mimic UIs. The 
				generated comment blocks will be refered as windows in the help
				sections.
				
				To close self window (ie. remove self comment bloc), press 
				"ctrl"+"shift"+"e" with you cursor on the line bellow.
				~~!close|~~
				
				Use the following command for a walkthrough in some in many
				features in codewave
				~~!help:get_started~~ or ~~!help:demo~~
				
				List in all helps subjects 
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
						
						for more information on creating your own commands, see:
						~~!help:editing~~
						
						Codewave come with many prexisting commands. Here an example in 
						javascript abreviations
						~~!js:f~~
						~~!js:if~~
							~~!js:log~~"~~!hello~~"~~!/js:log~~
						~~!/js:if~~
						~~!/js:f~~
						
						CodeWave come with the exellent Emmet ( http://emmet.io/ ) to 
						provide event more abreviations. Emmet will fire automaticaly if
						you are in a html or css file and no other command in the same 
						name were defined.
						~~!ul>li~~ (if you are in a html doccument)
						~~!emmet ul>li~~
						~~!emmet m2 css~~
						
						Commands are stored in name spaces and some in the namespaces are
						active depending in the context or they can be called explicitly. 
						The two following commands are the same and will display the 
						currently  active namespace. The first command command works 
						because the core namespace is active.
						~~!namespace~~
						~~!core:namespace~~
						
						you can make an namespace active with the following command.
						~~!namespace php~~
						
						Check the namespaces again
						~~!namespace~~
						
						All the dialogs(windows) in codewave are made with the command 
						"box" and you can use it in your own commands. you can also use a
						"close" command to make it easy to get rid in the window.
						~~!box~~
						The box will scale with the content you put in it
						~~!close|~~
						~~!/box~~
						
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
								Codewave allows you to make you own commands (or abbreviations) 
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
						
						~~quote_carret~~
						When you make your command you may need to tell where the text cursor 
						will be located once the command is executed. To do that, use a "|" 
						(Vertical bar). Use 2 in them if you want to print the actual 
						character.
						~~!box~~
						one : | 
						two : ||
						~~!/box~~
						
						If you want to print a command without having it evalute when 
						the command is executed, use a "!" exclamation mark.
						~~!!hello~~
						
						for commands that have both a openig and a closing tag, you can use:
						the "content" command. "content" will be replaced with the text
						that is between tha tags. Look at the code in the following command
						for en example in how it can be used.:
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
		'quote_carret':{
			'result' : quote_carret,
			'checkCarret' : False
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
					You cant rename a command you did not create yourself.
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
					You cant remove a command you did not create yourself.
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
	
	html = command.cmds.addCmd(command.Command('html'))
	html.addCmds({
		'fallback':{
			'aliasOf' : 'core:emmet',
			'defaults' : {'lang':'html'},
			'nameToParam' : 'abbr'
		},
	})
	
	css = command.cmds.addCmd(command.Command('css'))
	css.addCmds({
		'fallback':{
			'aliasOf' : 'core:emmet',
			'defaults' : {'lang':'css'},
			'nameToParam' : 'abbr'
		},
	})
	
	php = command.cmds.addCmd( command.Command('php'))
	php.addDetector(detector.PairDetector({
		'result': 'php:inner',
		'opener': '<?php',
		'closer': '?>',
		'else': 'php:outer'
	}))

	phpOuter = php.addCmd(command.Command('outer'))
	phpOuter.addCmds({
		'fallback':{
			'aliasOf' : 'php:inner:%name%',
			'beforeExecute' : closePhpForContent,
			'alterResult' : wrapWithPhp
		},
		'comment': '<?php /* ~~content~~ */ ?>',
		'php': '<?php\n\t~~content~~|\n?>',
	})
	
	phpInner = php.addCmd(command.Command('inner'))
	phpInner.addCmds({
		'comment': '/* ~~content~~ */',
		'if':   'if(|){\n\t~~content~~\n}',
		'info': 'phpinfo();',
		'echo': 'echo ${id}',
		'e':{   'aliasOf': 'php:inner:echo' },
		'class': textwrap.dedent("""
			class | {
			\tfunction __construct() {
			\t\t~~content~~
			\t}
			}
			"""),
		'c':{     'aliasOf': 'php:inner:class' },
		'function':	'function |() {\n\t~~content~~\n}',
		'funct':{ 'aliasOf': 'php:inner:function' },
		'f':{     'aliasOf': 'php:inner:function' },
		'array':  '$| = array();',
		'a':	    'array()',
		'for': 		'for ($i = 0; $i < $|; $i+=1) {\n\t~~content~~\n}',
		'foreach':'foreach ($| as $key => $val) {\n\t~~content~~\n}',
		'each':{  'aliasOf': 'php:inner:foreach' },
		'while':  'while(|) {\n\t~~content~~\n}',
		'whilei': '$i = 0;\nwhile(|) {\n\t~~content~~\n\t$i+=1;\n}',
		'ifelse': 'if( | ) {\n\t~~content~~\n} else {\n\t\n}',
		'ife':{   'aliasOf': 'php:inner:ifelse' },
		'switch': textwrap.dedent("""
			switch( | ) { 
			\tcase :
			\t\t~~content~~
			\t\tbreak;
			\tdefault :
			\t\t
			\t\tbreak;
			}
			""")
	})
	
	js = command.cmds.addCmd(command.Command('js'))
	command.cmds.addCmd(command.Command('javascript',{ 'aliasOf': 'js' }))
	js.addCmds({
		'comment': '/* ~~content~~ */',
		'if':  'if(|){\n\t~~content~~\n}',
		'log':  'if(window.console){\n\tconsole.log(~~content~~|)\n}',
		'function':	'function |() {\n\t~~content~~\n}',
		'funct':{ 'aliasOf': 'js:function' },
		'f':{     'aliasOf': 'js:function' },
		'for': 		'for (var i = 0; i < |; i+=1) {\n\t~~content~~\n}',
		'forin':'foreach (var val in |) {\n\t~~content~~\n}',
		'each':{  'aliasOf': 'js:forin' },
		'foreach':{  'aliasOf': 'js:forin' },
		'while':  'while(|) {\n\t~~content~~\n}',
		'whilei': 'var i = 0;\nwhile(|) {\n\t~~content~~\n\ti+=1;\n}',
		'ifelse': 'if( | ) {\n\t~~content~~\n} else {\n\t\n}',
		'ife':{   'aliasOf': 'js:ifelse' },
		'switch':	textwrap.dedent("""
			switch( | ) { 
			\tcase :
			\t\t~~content~~
			\t\tbreak;
			\tdefault :
			\t\t
			\t\tbreak;
			}
			"""),
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
	if instance.codewave.inInstance is not None:
		return instance.codewave.inInstance.content or ''
def wrapWithPhp(result,instance):
	regOpen = re.compile(r"<\?php\s([\n\r\s]+)")
	regClose = re.compile(r"([\n\r\s]+)\s\?>")
	return '<?php ' + re.sub(regOpen, r'\1<?php ', re.sub(regClose, r' ?>\1', result)) + ' ?>'
def renameCommand(instance):
	savedCmds = storage.load('cmds')
	origninalName = instance.getParam([0,'from'])
	newName = instance.getParam([1,'to'])
	if origninalName is not None and newName is not None:
		cmd = instance.context.getCmd(origninalName)
		console.log(cmd)
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
			command.saveCmd(alias, { aliasOf: cmd.fullName })
			return ""
		else:
			return "~~not_found~~"
def closePhpForContent(instance):
	instance.content = ' ?>'+(instance.content or '')+'<?php '
class BoxCmd(command.BaseCommand):
	def init(self):
		self.helper = box_helper.BoxHelper(self.instance.context)
		self.cmd = self.instance.getParam(['cmd'])
		if self.cmd is not None:
			self.helper.openText  = self.instance.codewave.brakets + self.cmd + self.instance.codewave.brakets
			self.helper.closeText = self.instance.codewave.brakets + self.instance.codewave.closeChar + self.cmd.split(" ")[0] + self.instance.codewave.brakets
		self.helper.deco = self.instance.codewave.deco
		self.helper.pad = 2
		
		if self.instance.content:
			bounds = self.helper.textBounds(self.instance.content)
			width, height = bounds.width, bounds.height
		else:
			width = 50
			height = 3
		
		params = ['width']
		if len(self.instance.params) > 1 :
			params.append(0)
		self.helper.width = max(self.minWidth(), self.instance.getParam(params, width))
			
		params = ['height']
		if len(self.instance.params) > 1 :
			params.append(1)
		elif len(self.instance.params) > 0:
			params.append(0)
		self.helper.height = self.instance.getParam(params,height)
		
	def result(self):
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
		box = self.helper.getBoxForPos(self.instance.getPos())
		if box is not None:
			self.instance.codewave.editor.spliceText(box.start,box.end,'')
			self.instance.codewave.editor.setCursorPos(box.start)
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
		self.content = self.instance.content
	def getOptions(self):
		return {
			'allowedNamed': ['cmd']
		}
	def result(self):
		if self.content:
			return self.resultWithContent()
		else:
			return self.resultWithoutContent()
	def resultWithContent(self):
			parser = self.instance.getParserForText(self.content)
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

