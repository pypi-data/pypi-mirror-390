""" Jubilee Shut Down mode class. """

from .base_classes import Button, Mode
from .misc import Log

class Mode_Shut_Down(Mode):
	""" Shutdown mode class. """

	def __init__(self, app, return_mode: str|Mode=None):

		super().__init__(app, 'Shut Down')
		self.return_mode = return_mode

		# create controls for log mode
		button_width = 150
		self.add_control(Button(app, app.button_margin, app.screen_height - 60, button_width, 60, 'Yes', click_handler = lambda app: app.shut_down()))
		self.add_control(Button(app, app.screen_width - app.button_margin - button_width, app.screen_height - 60, button_width, 60, 'Cancel', click_handler = self.cancel_shutdown))

		# add this to create a button to switch back from Log to another screen
		# self.add_control(Button(app, app.screen_width - 77 - app.button_margin, app.screen_height - 60, 77, 60, 'Back', target_mode = 'Target Mode'))

	def draw(self):
		""" Shut Down mode draw method. """

		self.app.fill_screen('black')
		self.app.draw_text('Confirm Shutdown', int(self.app.screen_width / 2), int(self.app.screen_height) / 2, alignment = 'center')

	def cancel_shutdown(self):
		""" Cancel shutdown and return to previous mode. """

		if self.return_mode is None:
			Log.error('Mode_Shut_Down', 'shut_down', 'self.return_mode is None')
		else:
			self.app.set_mode(self.return_mode)
