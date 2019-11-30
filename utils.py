from common import config, cmds, json
import sys, os.path

class Utils:
	def __init__(self):
		self.base_type = config.base_type
		#self.cmds = cmds
			
	def set(self, attr, value):
		setattr(self, attr, value)
	   
	def OnEvent(self, func, *args):
		result = -1
		
		for i in range(len(self.cmds['sorted'])):
			if self.cmds[self.cmds['sorted'][i]][func]:
				try:
					result = self.cmds[self.cmds['sorted'][i]][func](*args)
					if result == 1:
						break
				except Exception as e:
					print("{}: {}".format(self.cmds[self.cmds['sorted'][i]][func].__name__, e))
				
		del args, func, i
		
		return result

	def log(self, text):
		print(text)
		
	def OnError(self, addr, error, event):
		import sys
		import traceback
		
		frame = traceback.extract_tb(addr)[-1]
		fname, line, fn, text = frame
		
		text = "Error {} on {} line in {}".format(error, line, fname)

		print(text)
		
		if event:
			event.message_send("Ошибка {} на {} строчке в {}".format(error, line, fname), event.peer_id)
			
		del sys, traceback


	def OnCmd(self, answ, event):
		try:
			event.argue = event.text[len(answ[0]+answ[1])+2:]
			self.log('id{}[{}]: {} {}'.format(event.userid, event.peer_id, answ[1], event.argue))
			
			self.OnEvent('precmd', self.cmds[answ[1]], event)
			self.cmds[answ[1]]['cmd'](answ[1], event)
			
			self.OnEvent('postcmd', self.cmds[answ[1]], event)
		except Exception as e:
			self.OnError(sys.exc_info()[2], e, event)
		
		del answ, event
		
	def _getUser_access(self, uid):
		if os.path.exists('users/{}'.format(uid)):
			with open('users/{}'.format(uid)) as f:
				return int(f.read())
		else:
			with open('users/{}'.format(uid), 'w') as f:
				f.write('0' if uid not in config.admins else '2')
			
			return 0 if uid not in config.admins else 2
		
	def check_access(self, answ, event):
		if len(answ) < self.cmds[answ[1]]['args']:
			event.message_send('Недостаточно аргументов')
			return False
		
		access = self._getUser_access(event.userid)
		
		if access < self.cmds[answ[1]]['access']:
			event.message_send('Недостаточно привелегий')
			return False
			
		return True
		
	def get_cmd(self, cmd):
		cmd = list(filter(lambda x: cmd in x.split(','), list(self.cmds)))
		
		if cmd:
			return self.cmds[cmd[0]]
		else:
			return None 

utils = Utils()

