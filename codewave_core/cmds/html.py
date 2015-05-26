import re
import textwrap
import codewave_core.command as command
import codewave_core.util as util
import codewave_core.logger as logger
import codewave_core.detector as detector
import codewave_core.box_helper as box_helper
import codewave_core.edit_cmd_prop as edit_cmd_prop


def initCmds():
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
	
command.cmdInitialisers.add(initCmds)
