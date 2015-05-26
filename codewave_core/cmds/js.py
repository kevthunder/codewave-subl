import re
import textwrap
import codewave_core.command as command
import codewave_core.util as util
import codewave_core.logger as logger
import codewave_core.detector as detector
import codewave_core.box_helper as box_helper
import codewave_core.edit_cmd_prop as edit_cmd_prop


def initCmds():
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

