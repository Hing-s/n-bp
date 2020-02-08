import random
import urllib3
import json
import time
import threading
import sys
from utils import utils

API_URL = 'https://api.vk.com/method/'

class MethExecutor:
	def __init__(self, meth, bot):
		self._meth = meth
		self._bot = bot
	
	def __call__(self, type='POST', **params):
		return self._bot.method(self._meth, **params, type=type)

class MethWrapper(object):
	def __init__(self, bot, method = ''):
		self._bot = bot
		self._method = method
	
	def __getattribute__(self, key):
		if '_' in key:
			return super().__getattribute__(key)
		
		if not self._method:
			return MethWrapper(self._bot, key)
		else:
			return MethExecutor('{}.{}'.format(self._method, key), self._bot)

class Event:
	def __init__(self, bot, updates):        
		self.userid = None
		self.peer_id = None
		self.id = None
		self.text = ''
		self.type = None
		self.wrap = MethWrapper(bot)
		
		if isinstance(updates, dict):
			self._group_event(updates)
		else:
			self._page_event(updates)
		
		self.bot = bot
		self.updates = updates
		self.utils = utils
		self.bot.message_send = self.message_send
		
		del updates, bot
	
	def _group_event(self, updates):
		self.type = 'MSG' if updates['type'] == 'message_new' else updates['type']
		
		if self.type == 'MSG':
			self.userid = updates['object']['from_id']
			self.peer_id = updates['object']['peer_id']
			self.id = updates['object']['id']
			self.text = updates['object']['text']
		
		
	def _page_event(self, updates):
		self.type = 'MSG' if updates[0] == 4 else updates[0]
		
		if self.type == 'MSG':
			self.id = updates[1]
			self.text = updates[5]
			self.peer_id = updates[3]
			
			if self.peer_id > 2000000000:
				self.userid = int(updates[6]['from'])
			else:
				self.userid = self.peer_id
		
	def _upload(self, files):
		import os.path
	
		servers = {'photo': None, 'doc': None}
		photo = [file for file in files if files[file]['type'] == 'photo']
		doc = [file for file in files if files[file]['type'] == 'doc']
		
		files['photo'] = photo
		files['doc'] = doc
		
		del photo, doc
		
		attachments = ''
		
		forms = {}
		
		for type in ['photo', 'doc']:
			for file in files[type]:
				content = {}
				if not servers[type]:
					
					if type == 'photo':
						servers[type] = self.bot.method('photos.getMessagesUploadServer', type='POST')
					else:
						servers[type] = self.bot.method('docs.getMessagesUploadServer', peer_id=self.peer_id)
					
					if 'error' in servers[type]:
						print(servers[type]['error']['error_msg'])
						break
						
				content['content'] = 'image' if type == 'photo' else 'files'
				content['field'] = 'file1' if type == 'photo' else 'file'
				
				if 'path' in files[file]:
					with open(files[file]['path'], 'rb') as f:
						content['data'] = {content['field']: (os.path.basename(files[file]['path']), f.read(), '{}/{}'.format(content, os.path.basename(files[file]['path']).split('.')[1]))}
				else:
					content['data'] = {content['field']: (os.path.basename(files[file]['path']), f.read(), '{}/{}'.format(content, os.path.basename(files[file]['path']).split('.')[1]))}
				
				response = self.bot.request(servers[type]['response']['upload_url'], 'POST', **content['data'])
				
				if type == 'photo':
					response = self.bot.method('photos.saveMessagesPhoto', **{'album_id': -3, 'server': response['server'], 'photo': response['photo'], 'hash': response['hash']})
				else:
					response = self.bot.method('docs.save', file=response['file'])
				
				if 'error' in response:
					print(response['error']['error_msg'])
					continue
				
				attachments+='{}{}_{},'.format(type, response['response'][0]['owner_id'], response['response'][0]['id'])
		
		del servers, files, type, file, response, content
		return attachments

	def message_send(self, text, peer_id=None, from_group=1, **fields):
		if not peer_id:
			peer_id = self.peer_id
		
		fields['message'] = text
		fields['peer_id'] = peer_id
		
		if float(self.bot.version) >= 5.90 and 'random_id' not in fields:
			fields['random_id'] = 0
		
		if 'files' in fields:
			attachment = self._upload(fields.pop('files'))
			
			if 'attachment' in fields:
				fields['attachment']+=attachment
			else:
				fields['attachment'] = attachment
		
		return self.bot.method('messages.send', **fields)
			

class Bot:
   # __slots__ = ('token', 'type', 'id', 'data', 'version', '_pm', '_url', 'updates', '_bots', '_count')
	
	def __init__(self, bot, cmds={}):
		self._pm = urllib3.PoolManager() 
		self._bots = None
		self._count = 0
		
		self.token = bot['token']
		self.type = bot['type']
		self.version = bot['version']
		self.id = None
		self.data = None
		self.updates = []
		self.utils = utils
		
		self.utils.OnEvent('launch', self)
		
	def request(self, url, type, **params):
		if self._count >= 10:
			self._pm.clear()
			self._count = 0
			
		self._count += 1
		
		return json.loads(self._pm.request(type.upper(), url, fields=params).data.decode())
		
	def method(self, method, type='POST', **params):
		if self._count >= 10:
			self._pm.clear()
			self._count = 0
			
		self._count += 1
		
		return json.loads(self._pm.request(type.upper(), '{}{}?access_token={}&v={}'.format(API_URL, method, self.token, self.version), fields=params, timeout=10).data.decode())
		
	def getBot(self, type, index=0):
		if type != 'all':
			return [bot for bot in self._bots if bot.type == type][index]
		else:
			return self._bots
		
	def setBots(self, bots):
		self._bots = bots
		
	def index(self, all=True):
		if all:
			return self._bots.index(self)
		else:
			return [bot for bot in self._bots if bot.type == self.type].index(self)
			
class CLongPoll:
	def __init__(self, bots, cmds={}, version='5.81'):
		if not isinstance(bots, list):
			raise ValueError('bots must be list')
			
		self._pm = urllib3.PoolManager()
		
		self._bots = [Bot(bot, cmds) for bot in bots]
		self._count = 0
		
		for bot in self._bots:
			if not self._isPage(bot):
				bot.id = self._check(self.request('https://api.vk.com/method/groups.getById', params={'access_token': bot.token, 'v': bot.version}))
			else:
				bot.id = self._check(self.request('https://api.vk.com/method/users.get', params={'access_token': bot.token, 'v': bot.version}))
			
			if bot.id:
				bot.id = bot.id['response'][0]['id']
				threading.Thread(target=self._get, args=(bot,)).start()
			else:
				self._bots[self._bots.index(bot)] = None
		
		self._setBots()
	
	def _setBots(self):
		self._bots = list(filter(lambda x: x is not None, self._bots))
		
		if not self._bots:
			sys.exit('No bots was launched successfully')
		
		for bot in self._bots:
			bot.setBots(self._bots)
		
	def request(self, url, params={}, type='POST', timeout=90):
		if self._count >= 200:
			self._pm.clear()
			self._count = 0
		
		self._count += 1
		
		return json.loads(self._pm.request(type, url, fields=params, timeout=timeout).data.decode())
	
	
	def _isPage(self, bot):
		return bot.type == 'page'
		
	def _update(self, bot):
		while True:
			time.sleep(0.15)
			try:
				updates = self.request('{}{server}?act=a_check&key={key}&ts={ts}&wait=30&mode=2&version=3'.format('https://' if self._isPage(bot) else '', server=bot.data['server'], key=bot.data['key'], ts=bot.data['ts']), timeout=40)
				bot.data['ts'] = updates['ts']
				bot.updates.append([Event(bot, upd) for upd in updates['updates']])
				
				del updates
			except Exception as e:
				print(e)
				time.sleep(random.randint(4, 8))
				self._get(bot)
		
	def _get(self, bot):
		time.sleep(0.1)
		while True:
			try:
				if not self._isPage(bot):
					lp = self.request('https://api.vk.com/method/groups.getLongPollServer?access_token={}&v={}&lp_version=3&group_id={}'.format(bot.token, bot.version, bot.id), timeout=30)
				else:
					lp = self.request('https://api.vk.com/method/messages.getLongPollServer?access_token={}&v={}&lp_version=3'.format(bot.token, bot.version), timeout=30)
				
				if 'error' in lp:
					time.sleep(6.5)
				else:
					print('Лонгполл {} получен!'.format(bot.id if self._isPage(bot) else -bot.id))
					break
			except Exception as e:
				print('LP {}: {}'.format(bot.id if self._isPage(bot) else -bot.id, e))

		bot.data = lp['response']
		
	def updates(self):
		for bot in self._bots:
			time.sleep(2.5)
			if bot.data:
				threading.Thread(target=self._update, args=(bot,)).start()
		
		while True:
			try:
				time.sleep(0.05)   
				for bot in self._bots:
					if bot.updates:
						updates = bot.updates[0]
						bot.updates.remove(updates)
						yield updates
			except:
				pass
			
	def _check(self, data):
		if "error" in data:
			return print(data["error"])
		
		return data
