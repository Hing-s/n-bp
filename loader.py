import sys
import os
import os.path
from common import config

ACCESSES = {
	'admin': 2,
	'vip': 1,
	'default': 0
}

def load(cmds):
	import importlib
	from utils import utils
	
	if not os.path.exists('access'):
		os.mkdir('access')
	
	cmds.clear()
	accesses = [f for f in os.listdir('plugins') if os.path.isdir('plugins/{}'.format(f)) and '__' not in f]
	
	for access in accesses:
		sys.path.append('plugins/{}'.format(access))
		
		for plug in [f.replace('.py', '') for f in os.listdir('plugins/{}'.format(access))]:
			try:
				if os.path.isfile('plugins/{}/{}.py'.format(access, plug)):
					plugin = importlib.reload(__import__(plug))
					cmd = plug.split(':')[0]
					
					if not os.path.exists('access/{}'.format(access)):
						os.mkdir('access/{}'.format(access))
					
					cmds[cmd] = {}
					cmds[cmd]['access'] = access
					cmds[cmd]['executor'] = config.base_type if len(plug.split(':')) == 1 else plug.split(':')[1]
					
					cmds[cmd]['cmd'] = None
					cmds[cmd]['launch'] = None
					cmds[cmd]['message'] = None
					cmds[cmd]['other'] = None
					cmds[cmd]['precmd'] = None
					cmds[cmd]['postcmd'] = None
					cmds[cmd]['notcmd'] = None
					cmds[cmd]['threading'] = False
					cmds[cmd]['args'] = 0
					cmds[cmd]['priority'] = 0
					
					for f in ['cmd', 'launch', 'message', 'precmd', 'postcmd', 'notcmd', 'threading', 'args', 'priority', 'other']:
						if hasattr(plugin, f):
							attr = getattr(plugin, f)
							
							if callable(attr) and cmds[cmd][f] is not None:
								cmds[cmd][f] = attr()
							else:
								cmds[cmd][f] = attr
					
					cmds[cmd]['access'] = ACCESSES[cmds[cmd]['access']]
					
					del plugin, f, plug, cmd
			except Exception as e:
				print('{} dont loaded: {}'.format(plug, e))
		
		sys.path.remove('plugins/{}'.format(access))
	
	cmds['sorted'] = tuple(sorted(cmds, key=lambda x: cmds[x]['priority']))
	cmds['acs'] = sorted(ACCESSES, key=lambda x: ACCESSES[x], reverse=True)
	
	utils.set('cmds', cmds)
	
	del importlib
	return cmds
