""" Hello Jubilee app. """

from jubilee import App
from jubilee.base_classes import Button, Mode
from hello_worker import Hello_Worker

class Hello_App(App):
	""" Hello app. """

	def __init__(self):
		super().__init__(worker_classes=Hello_Worker)
		self.add_mode(Mode_Hello(app=self))
		self.set_mode('Hello')								# note: first mode is selected by default

	def process_message(self, message):
		""" Process message from worker. """

		action = message.get('action')
		if action == 'custom action':		# process message
			pass
		else:
			super().process_message(message)

class Mode_Hello(Mode):
	""" Hello mode. """

	def __init__(self, app):
		super().__init__(app, name='Hello')

		self.click_count = 0
		x = app.screen_center - 50; y = app.screen_middle - 30
		self.add_control(Button(app, x, y, 100, 60, 'Hello, World!', click_handler=self.clicked_hello))

	def clicked_hello(self):
		""" Click handler for Hello button. """
		self.click_count += 1

	def enter(self, parameters: dict=None):
		""" Enter method for Hello mode. """
		super().enter(parameters)

	def set_submode(self, name: str=None, parameters: dict=None):
		""" Set_submode method for Hello mode. """
		super().set_submode(name, parameters)

	def click_handler(self, x: int|float, y: int|float):
		""" Click event handler for Hello mode. """
		super().click_handler(x, y)							# this can be skipped to override control input

	def process(self):
		""" Process method for Hello mode. """
		super().process()												# this can be deleted if not using submodes

	def draw(self):
		""" Draw method for Hello mode. """
		super().draw()

		# draw text in default font to show click count
		text = f'Click Count: {self.click_count}'
		self.app.draw_text_center(text, self.app.screen_middle + 50)

if __name__ == '__main__':
	Hello_App().run()
