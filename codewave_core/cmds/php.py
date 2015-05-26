import re
import textwrap
import codewave_core.command as command
import codewave_core.util as util
import codewave_core.logger as logger
import codewave_core.detector as detector
import codewave_core.box_helper as box_helper
import codewave_core.edit_cmd_prop as edit_cmd_prop


def initCmds():
	php = command.cmds.addCmd( command.Command('php'))
	php.addDetector(detector.PairDetector({
		'result': 'php:inner',
		'opener': '<?php',
		'closer': '?>',
		'optionnal_end': True,
		'else': 'php:outer'
	}))

	phpOuter = php.addCmd(command.Command('outer'))
	phpOuter.addCmds({
		'fallback':{
			'cmds' : {
				'any_content': { 
					'aliasOf': 'core:content',
					'defaults': {
						'prefix': ' ?>\n',
						'suffix': '\n<?php ',
						'affixes_empty': True
					}
				},
			},
			'aliasOf' : 'php:inner:%name%',
			'alterResult' : wrapWithPhp
		},
		'box': { 
			'aliasOf': 'core:box',
			'defaults': {
				'prefix': '<?php\n',
				'suffix': '\n?>'
			}
		},
		'comment': '/* ~~content~~ */',
		'php': '<?php\n\t~~content~~|\n?>',
	})
	
	phpInner = php.addCmd(command.Command('inner'))
	phpInner.addCmds({
			'any_content': { 'aliasOf': 'core:content' },
		'comment': '/* ~~content~~ */',
		'if':   'if(|){\n\t~~any_content~~\n}',
		'info': 'phpinfo();',
		'echo': 'echo |',
		'e':{   'aliasOf': 'php:inner:echo' },
		'class': {
			'result' : textwrap.dedent("""
				class ~~param 0 class def:|~~ {
				\tfunction __construct() {
				\t\t~~content~~
				\t}
				}
				"""),
			'defaults': {
				'inline': False
			}
		},
		'c':{     'aliasOf': 'php:inner:class' },
		'function':	{
			'result' : 'function |() {\n\t~~content~~\n}',
			'defaults': {
				'inline': False
			}
		},
		'funct':{ 'aliasOf': 'php:inner:function' },
		'f':{     'aliasOf': 'php:inner:function' },
		'array':  '$| = array();',
		'a':	    'array()',
		'for': 		'for ($i = 0; $i < $|; $i+=1) {\n\t~~any_content~~\n}',
		'foreach':'foreach ($| as $key => $val) {\n\t~~any_content~~\n}',
		'each':{  'aliasOf': 'php:inner:foreach' },
		'while':  'while(|) {\n\t~~any_content~~\n}',
		'whilei': {
			'result' : '$i = 0;\nwhile(|) {\n\t~~any_content~~\n\t$i+=1;\n}',
			'defaults': {
				'inline': False
			}
		},
		'ifelse': 'if( | ) {\n\t~~any_content~~\n} else {\n\t\n}',
		'ife':{   'aliasOf': 'php:inner:ifelse' },
		'switch': 	{
			'result' : textwrap.dedent("""
				switch( | ) { 
				\tcase :
				\t\t~~content~~
				\t\tbreak;
				\tdefault :
				\t\t
				\t\tbreak;
				}
				"""),
			'defaults': {
				'inline': False
			}
		},
		'close': { 
			'aliasOf': 'core:close',
			'defaults': {
				'prefix': '<?php\n',
				'suffix': '\n?>',
				'required_affixes': False
			}
		},
	})
	
	
command.cmdInitialisers.add(initCmds)


def wrapWithPhp(result,instance):
	inline = instance.getParam(['php_inline','inline'],True)
	if inline:
		regOpen = re.compile(r"<\?php\s([\n\r\s]+)")
		regClose = re.compile(r"([\n\r\s]+)\s\?>")
		return '<?php ' + re.sub(regOpen, r'\1<?php ', re.sub(regClose, r' ?>\1', result)) + ' ?>'
	else:
		return '<?php\n' + util.indent(result) + '\n?>'
