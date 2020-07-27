import sublime
import sublime_plugin
import http.client
import json
import os

class MmdvLogoutCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if 'MEMDEV_ACCESS' in os.environ:
			del os.environ['MEMDEV_ACCESS']

class MmdvCommand(sublime_plugin.TextCommand):
	def __init__(self, view):
		super().__init__(view)
		self.BASE_URL = 'localhost:3000'
		self.connection = 'http'
		self.__title = ''
		self.__content = ''

	def __api(self, uri, params, method = 'POST'):
		if self.connection == 'http':
			conn = http.client.HTTPConnection(self.BASE_URL)
		else:
			conn = http.client.HTTPSConnection(self.BASE_URL)
		headers = {
			'Content-type': 'application/json'
		}

		if 'MEMDEV_ACCESS' in os.environ:
			headers['Authorization'] = os.environ.get('MEMDEV_ACCESS')

		json_data = json.dumps(params)

		conn.request('POST', uri, json_data, headers)
		response = conn.getresponse()
		return json.loads(response.read().decode())

	def on_token_input_done(self, input_val):
		params = {'id': input_val}
		response_json = self.__api('/api/v2/authorize/ext_auth', params)

		if response_json['token']:
			os.environ['MEMDEV_ACCESS'] = str(response_json['token'])

		self.send_snippet()

	def send_snippet(self):
		syntax = self.view.settings().get("syntax")

		if 'Plain text' not in syntax:
			syntax = syntax[syntax.rfind('/') + 1:syntax.index('sublime-syntax') - 1].lower()
		else:
			syntax = 'plain'
		
		params = {
			'content': self.__content, 
			'title': self.__title, 
			'syntax': syntax,
			'topic': self.__topic
		}

		response_json = self.__api('/api/v2/snippets', params)

		window = self.view
		window.show_popup('Your snippet has been saved!')

	def on_topic_input_done(self, val):
		window = self.view.window()
		self.__topic = val
		if val:
			window.show_input_panel("I just learned how to...", "", self.on_title_input_done, None, None)


	def on_title_input_done(self, input_string):
		self.__title = input_string
		window = self.view.window()

		if 'MEMDEV_ACCESS' not in os.environ:
			window.show_input_panel("Enter your auth token", "", self.on_token_input_done, None, None)
			return

	def run(self, edit):
		window = self.view.window()
		view = self.view
		sel = view.sel()

		region1 = sel[0]
		self.__content = view.substr(region1)

		window.show_input_panel("This snippet is about...", "", self.on_topic_input_done, None, None)