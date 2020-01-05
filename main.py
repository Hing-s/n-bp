from api import CLongPoll, threading
from loader import load, os
from utils import *


bots = [{
	'token': config.token,
	'type': 'page',
	'version': '5.90'
	},{
	'token': config.group_token,
	'type': 'group',
	'version': '5.90'
}]

cmds.update(load(cmds))

if __name__ == '__main__':
	LP = CLongPoll(bots, cmds)

	for updates in LP.updates():
		for event in updates:
			if event.type == "MSG":
				event.bot.utils.OnEvent('message', event)
				answ = event.text.lower().split()
				
				if len(answ) > 1:
					if answ[0] in config.names:
						if event.bot.utils.get_cmd(answ[1]) and event.bot.type == cmds[answ[1]]['executor']:
							if not event.utils.check_access(answ, event):
								continue
								
							if not cmds[answ[1]]['threading']:
								event.bot.utils.OnCmd(answ, event)
							else:
								threading.Thread(target=event.bot.utils.OnCmd, args=(answ, event,)).start()
						else:
							if answ[1] in cmds and event.bot.type != cmds[answ[1]]['executor'] or answ[0] not in cmds and event.bot.type != event.utils.base_type:
								continue
							
							if event.bot.utils.OnEvent('notcmd', cmds, event) == -1:
								event.message_send('Команда не найдена')
			else:
				event.bot.utils.OnEvent('other', event)
			   
