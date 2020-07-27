import sublime
import sublime_plugin
import http.client
import json
import os

class MmdvCommand(sublime_plugin.TextCommand):
	def __init__(self, view):
		super().__init__(view)
		self.BASE_URL = 'localhost:3000'
		self.__title = ''
		self.__source = ''
		self.__content = ''

	def __api(self, uri, params, method = 'POST'):
		conn = http.client.HTTPConnection(self.BASE_URL)
		headers = {
			'Content-type': 'application/json'
		}

		if 'MEMDEV_ACCESS' in os.environ:
			headers['Authorization'] = os.environ.get('MEMDEV_ACCESS')

		json_data = json.dumps(params)

		conn.request('POST', uri, json_data, headers)
		response = conn.getresponse()
		return json.loads(response.read().decode())

	def __show_source_panel(self):
		window = self.view.window()

		window.show_input_panel("Source", "", self.on_source_input_done, None, None)

	def on_token_input_done(self, input_val):
		params = {'id': input_val}
		response_json = self.__api('/api/v2/authorize/ext_auth', params)

		if response_json['token']:
			os.environ['MEMDEV_ACCESS'] = str(response_json['token'])

		self.__show_source_panel()

	def on_source_input_done(self, input_val):
		self.__source = input_val
		syntax = self.view.settings().get("syntax")

		if 'Plain text' not in syntax:
			syntax = syntax[syntax.rfind('/') + 1:syntax.index('sublime-syntax') - 1].lower()
		else:
			syntax = 'plain'
		
		params = {
			'content': self.__content, 
			'title': self.__title, 
			'source': input_val,
			'syntax': syntax,
			'topic': syntax
		}

		response_json = self.__api('/api/v2/snippets', params)

		window = self.view
		window.show_popup('Your snippet has been saved!')

	def on_title_input_done(self, input_string):
		self.__title = input_string
		window = self.view.window()

		if 'MEMDEV_ACCESS' not in os.environ:
			window.show_input_panel("Enter your auth token", "", self.on_token_input_done, None, None)
			return

		self.__show_source_panel()

	def run(self, edit):
		window = self.view.window()
		view = self.view
		sel = view.sel()

		region1 = sel[0]
		self.__content = view.substr(region1)

		window.show_input_panel("I just learned how to...", "", self.on_title_input_done, None, None)
