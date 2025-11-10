""" Jubilee Worker class. """

import json, multiprocessing, os, queue, sys, time
import __main__
from .misc import Config, Log

class Worker:
	""" Worker class. """

	def __init__(self, name: str, app_queue, worker_queue, config_manager=False):
		self.name = name or 'Worker'
		self.app_queue = app_queue
		self.worker_queue = worker_queue
		self.config_manager = config_manager
		self.worker_process = None
		self.base_path = os.path.dirname(os.path.realpath(__main__.__file__))
		self.config_filename = os.path.join(self.base_path, 'config.txt')
		self.config = Config.load(self.config_filename)
		self.config_date = os.path.getmtime(self.config_filename)
		self.last_periodic = None

	def start(self) -> multiprocessing.Process:
		""" Starts the process and returns process object. Note: This is in
				a separate method (instead of just being added to __init__)
				so that subclasses can extend __init__ with additional code
				to run during init, *after* the init stuff above, and before
				duplicating this class instance for the child process. """

		process = multiprocessing.Process(target=self.run)
		process.daemon = True
		process.start()
		return process

	def run(self):
		""" Worker run loop. """

		try:
			Log.info('Worker', 'run', 'Starting')
			self.init_worker()

			while True:
				loop_start = time.time()
				self.receive_messages()
				self.process()
				loop_time = time.time() - loop_start
				delay = 1 / max(1, int(self.config.get('worker_process_fps', 10))) - loop_time
				if delay > 0:
					time.sleep(delay)

		except Exception as e:
			Log.error('Worker', 'run', str(e))

	def init_worker(self):
		""" Initializes worker at start of run loop. """

	def process(self):
		""" Regular (high-frequency) worker processing. """

		process_periodic_fps = self.config.get('worker_process_periodic_fps', 1)
		if process_periodic_fps is None:
			return
		if self.last_periodic is not None:
			elapsed = time.time() - self.last_periodic
			if elapsed < 1 / process_periodic_fps:
				return
		self.last_periodic = time.time()
		self.process_periodic()

	def process_periodic(self):
		""" Periodic (low-frequency) worker processing. """

		if self.config_manager is False:
			return
		if os.path.isfile(self.config_filename) is False:
			Log.error('Worker', 'process_periodic', f'{self.config_filename} does not exist')
			self.exit(code = 1)
		config_date = os.path.getmtime(self.config_filename)
		if config_date != self.config_date:
			Log.info('Worker', 'process_periodic', f'Loading config ({self.config_date} != {config_date})')
			self.config_date = config_date
			self.config = Config.load(self.config_filename)
			self.send_updated_config()

	def exit(self, code=0):
		sys.exit(code)

	# messaging with app

	def send_message(self, message: str|dict):
		""" Send a message to the app. """

		if isinstance(message, str):
			message = {'action': message}
		self.worker_queue.put(json.dumps(message))

	def receive_messages(self):
		""" Receive messages from app. """

		try:
			while True:
				message = self.app_queue.get_nowait()
				self.process_message(json.loads(message))
		except queue.Empty:
			return
		except Exception as e:
			Log.error('Worker', 'receive_messages', str(e))
			return

	def process_message(self, message: dict):
		""" Process a message from app. This method can be extended in subclass. """

		action = message.get('action')
		if action == 'update config':
			key = message.get('key')
			value = message.get('value')
			self.update_config(key, value)
		elif action == 'updated config':
			self.config = message.get('config', {})
		elif action == 'exit':
			self.exit()
		else:
			Log.warning('Worker', 'process_message', f'Received unknown message: {message}')

	def update_config(self, key, value):
		self.config[key] = value
		self.write_config()

	def write_config(self):
		Config.save(self.config, self.config_filename)
		self.config_date = os.path.getmtime(self.config_filename)
		self.send_updated_config()

	def send_updated_config(self):
		message = {'action': 'config updated', 'config': self.config}
		self.send_message(message)
