""" Modes Jubilee app. """

import sys
from jubilee import App
from jubilee.base_classes import Button, Mode
from jubilee.misc import Log

class Modes_App(App):
	""" Modes app. """

	def __init__(self):
		super().__init__()
		self.add_mode(Mode_Main(app=self))
		self.add_mode(Mode_Submode(app=self))

	def process_message(self, message):
		""" Process message from worker. """

		action = message.get('action')
		if action == 'custom action':		# process message
			pass
		else:
			super().process_message(message)

class Mode_Main(Mode):
	""" Main mode. """

	def __init__(self, app):
		super().__init__(app, name='Main')
		x = app.screen_center-50; y = app.screen_middle-30; w=100; h=60
		self.add_control(Button(app, x, y, w, h, 'Submode', target_mode='Submode'))

	def draw(self):
		""" Draw method for Main mode. """

		super().draw()
		x = self.app.screen_center; y = self.app.screen_middle-50
		self.app.draw_text('Main Mode', x, y, alignment='center')

class Mode_Submode(Mode):
	""" Submode mode. """

	def __init__(self, app):
		super().__init__(app, name='Submode')
		x = app.screen_center-50; y = app.screen_middle-50; w=100; h=60
		self.add_control(Button(app, x, y, w, h, 'Main Mode', target_mode='Main'))

	def draw(self):
		""" Draw method for Submode mode. """

		super().draw()
		x = self.app.screen_center; y = self.app.screen_middle+30
		self.app.draw_text('Submode', x, y, alignment='center')

if __name__ == '__main__':
	Modes_App().run()
