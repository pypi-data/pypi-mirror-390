""" Sound Jubilee app. Demonstrates sound and music. """

import os, sys
from jubilee import App
from jubilee.base_classes import Button, Mode

class Sound_Music_App(App):
	""" Sound_Music app. """

	def __init__(self):
		super().__init__()
		self.add_mode(Mode_Sound_Music(app=self))
		self.set_mode('Sound_Music')								# note: first mode is selected by default

class Mode_Sound_Music(Mode):
	""" Sound_Music mode. """

	def __init__(self, app):
		super().__init__(app, name='Sound_Music')

		# load music filenames
		music_folder = os.path.join(self.app.base_path, 'music')
		self.music = list(f for f in os.listdir(music_folder) if os.path.splitext(f)[1].lower() == '.mp3')

		self.music_index = 0
		self.add_control(Button(app, 100, 50, 40, 40, 'Next', click_handler=self.next_music))
		self.add_control(Button(app, 150, 50, 40, 40, 'Play', click_handler=self.play_music))
		self.add_control(Button(app, 200, 50, 40, 40, 'Stop', click_handler=self.stop_music))

		self.sound_index = 0
		self.add_control(Button(app, 100, 130, 40, 40, 'Next', click_handler=self.next_sound))
		self.add_control(Button(app, 150, 130, 40, 40, 'Play', click_handler=self.play_sound))

	def next_music(self):
		""" Click handler for Next Music button. """

		self.music_index = (self.music_index + 1) % len(self.music)

	def play_music(self):
		""" Click handler for Play Music button. """

		self.app.play_music(self.music[self.music_index])

	def stop_music(self):
		""" Click handler for Stop Music button. """

		self.app.stop_music()

	def next_sound(self):
		""" Click handler for Next Sound button. """

		self.sound_index = (self.sound_index + 1) % len(self.app.sounds)

	def play_sound(self):
		""" Click handler for Play Sound button. """

		sounds = list(self.app.sounds.keys())
		self.app.play_sound(sounds[self.sound_index])

	def draw(self):
		""" Draw method for Sound_Music mode. """

		super().draw()
		self.app.draw_text(f'Music: {self.music[self.music_index]}', 10, 10, alignment='Left')
		status = 'Playing' if self.app.is_music_playing() else 'Stopped'
		self.app.draw_text(f'Status: {status}', 10, 30, alignment='Left')
		sounds = list(self.app.sounds.keys())
		self.app.draw_text(f'Sound: {sounds[self.sound_index]}', 10, 120, alignment='Left')

if __name__ == '__main__':
	Sound_Music_App().run()
