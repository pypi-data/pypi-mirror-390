""" Jubilee Log mode class. """

import math, platform, time
import psutil
from pygame.font import Font
from .base_classes import Button, Mode
from .misc import Log

class Mode_Log(Mode):
	""" Log mode class. """

	def __init__(self, app, max_log_size: int=100, button_font: str|Font=None, target_mode: str|Mode=None, target_mode_parameters: dict=None):

		super().__init__(app, 'Log')

		# log paramters
		self.last_process = None
		self.log_date = None
		self.max_log_size = max_log_size
		self.log_text = []
		self.log_line_height = 13
		self.log_lines_per_page = int((app.screen_height - 180) / self.log_line_height)
		self.log_page = 0
		self.previous_mode = None
		self.return_mode_parameters = target_mode_parameters

		# CPU temp parameters
		self.cpu_load = []
		self.cpu_temp = []

		# create controls for log mode
		button_width = 77
		self.add_control(Button(app, app.button_margin, app.screen_height - 60, button_width,
			60, 'Font', font=button_font, click_handler=self.change_font))
		self.add_control(Button(app, button_width + app.button_margin * 2,
			app.screen_height - 60, button_width, 60, 'Up', font=button_font,
			click_handler=self.log_page_up))
		self.add_control(Button(app, button_width * 2 + app.button_margin * 3,
			app.screen_height - 60, button_width, 60, 'Down', font=button_font,
			click_handler=self.log_page_down))

		# create Back button
		self.back_button = Button(app, app.screen_width - 77 - app.button_margin,
			app.screen_height - 60, 77, 60, 'Back', font=button_font,
			target_mode=target_mode, target_mode_parameters=target_mode_parameters,
			click_handler=self.back_click_handler)
		self.add_control(self.back_button)

		# By default, the Back button causes the app to return to the mode from which it
		# was called. The target mode can be set statically in this initializer, or
		# dynamically using this code:
		# 	self.app.modes['Log'].back_button.target_mode = target_mode
		# 	self.add_control(Button(app, app.screen_width - 77 - app.button_margin,
		# 		app.screen_height - 60, 77, 60, 'Log', target_mode='Log',
		#   	return_mode_parameters={}))

	def enter(self, parameters: dict=None):
		""" Log mode enter method. """

		super().enter(parameters)
		parameters = parameters or {}
		self.previous_mode = parameters.get('previous_mode', None)
		return_mode_parameters = parameters.get('return_mode_parameters', None)
		if return_mode_parameters is not None:
			self.return_mode_parameters = return_mode_parameters

	def back_click_handler(self):
		""" Handles Back button click. """

		mode = self.back_button.target_mode or self.previous_mode
		if mode is None:
			Log.error('Mode_Log', 'back_click_handler', 'No mode to switch back to')
		else:
			self.app.set_mode(mode, new_mode_parameters = self.return_mode_parameters)

	def process(self):
		""" Log mode process method. Runs at 1 Hz. """

		now = time.time()
		if self.last_process is not None and now - self.last_process < 1:
			return
		self.last_process = now
		self.check_log()
		self.record_cpu_temperatures()

	def check_log(self):
		""" Check status of log and reload if changed. """

		modification_date = Log.get_modification_date()
		if modification_date == self.log_date:
			return
		self.log_date = modification_date
		log_lines = Log.read()[-self.max_log_size:]
		self.log_text = list(reversed(log_lines))

	def record_cpu_temperatures(self):
		""" Record CPU temperatures. """

		max_graph_points = self.app.screen_width - 180
		self.cpu_load.append(int(psutil.cpu_percent()))
		if len(self.cpu_load) > max_graph_points:
			self.cpu_load = self.cpu_load[-max_graph_points:]
		temperature = None
		if platform.uname().system == 'Darwin':
			temperature = 0			# no way to do this easily
		else:
			temperature_metrics = psutil.sensors_temperatures()
			temperature = temperature_metrics.get('cpu-thermal', None)
			if temperature is None:
				temperature = temperature_metrics.get('cpu_thermal', None)
				temperature = int(temperature[0].current)
		if temperature is not None:
			self.cpu_temp.append(temperature)
			if len(self.cpu_temp) > max_graph_points:
				self.cpu_temp = self.cpu_temp[-max_graph_points:]

	def draw(self):
		""" Log mode draw method. """

		self.app.fill_screen('black')

		# draw CPU load
		graph_x = 90
		if len(self.cpu_load) > 0:
			self.app.draw_text(f'CPU: {self.cpu_load[-1]}%', self.app.margin, 20)
			self.app.draw_line(graph_x, 10, graph_x, 49)
			self.app.draw_line(graph_x, 49, self.app.screen_width - 20, 49)
			for i in range(1, len(self.cpu_load)):
				cpu = 48 - int(self.cpu_load[i] / 100.0 * 38.0)
				self.app.draw_pixel(graph_x + i + 1, cpu)

		# draw CPU temp
		if len(self.cpu_temp) > 0:
			self.app.draw_text(f'Temp: {self.cpu_temp[-1]} C', self.app.margin, 70)
			self.app.draw_line(graph_x, 60, graph_x, 99)
			self.app.draw_line(graph_x, 99, self.app.screen_width - 20, 99)
			for i, temp in enumerate(self.cpu_temp):
				cpu = 98 - int(temp / 100.0 * 38.0)
				self.app.draw_pixel(graph_x + i + 1, cpu)

		# check page_down and ensure that it has not gone past end of log
		if self.log_lines_per_page < 1:
			Log.debug('Mode_Log', 'draw', f'log_lines_per_page = {self.log_lines_per_page}')
			return
		num_pages = math.ceil(len(self.log_text) / self.log_lines_per_page)
		self.log_page = max(0, min(self.log_page, num_pages - 1))

		# draw log
		y = 95 + self.log_line_height
		self.app.draw_text('Log', self.app.margin, y)
		y += self.app.underscore_position
		self.app.draw_line(self.app.margin, y, self.app.screen_width - self.app.margin, y)
		for i in range(self.log_lines_per_page):
			line_number = self.log_page * self.log_lines_per_page + i
			if line_number >= len(self.log_text):
				break
			y += self.log_line_height
			self.app.draw_text(self.log_text[line_number], self.app.margin, y, font = self.app.standard_font_sizes[14])

	def change_font(self):
		""" Changes font. """

		self.app.change_font()
		self.app.set_popover(f'Changed font to {self.app.standard_font}')

	def log_page_up(self):
		""" Scrolls log up one page. """

		self.log_page = max(self.log_page - 1, 0)

	def log_page_down(self):
		""" Scrolls log down one page. """

		self.log_page = self.log_page + 1
