""" Hello worker. """

from jubilee import Worker

class Hello_Worker(Worker):
	""" Hello worker class. """

	def __init__(self, app_queue, worker_queue, config_manager=True):
		super().__init__('Hello_Worker', app_queue, worker_queue, config_manager)

	def process(self):
		""" Regular (high-frequency) worker processing. """
		super().process()

	def process_periodic(self):
		""" Periodic (low-frequency) worker processing. """
		super().process_periodic()

	def process_message(self, message):
		""" Process a message from app. """

		action = message.get('action', None)
		if action == 'custom action':
			pass
		else:
			super().process_message(message)
