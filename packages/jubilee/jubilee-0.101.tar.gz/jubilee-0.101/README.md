Jubilee readme.txt
==================

=== Introduction ===

Raspberry Pi devices and other single-board computers (SBCs) provide an exciting platform for small-scale computing for hobbyist projects.

A common problem with such projects is the gap between a freshly configured device, such as new install of Raspberry Pi OS, and a component that is ready to be configured for a project. That gap routinely involves questions like:

* How do I render text and use fonts?

* How do I render basic graphics and images?

* How do I render UI elements like buttons that and detect and respond to user input?

* How do I create a UI with various modes and maintain an application state?

* How do I create a scripted UI that automatically traverses a set of modes and submodes?

* How do I separate UI rendering and processing event handling from background processing?

* How do I get the UI-rendering process to communicate with background processes?

* How do I enforce specific framerates for the UI and background processing?

* How do I load assets into usable libraries?

* How do I render sprites with animation sequences?

* How do I implement visual effects like popover messages and fade transitions?

* How do I play and manage sounds and music?

* How do I receive and handle keyboard input?

* How do I handle application configuration and logging?

* How do I design an application for testing on a workstation with mouse input, and for deployment on a device with touch input?

Many of these features are supported by libraries like pygame, but the features of such libraries are typically too low-level for the sophisticated functionality of many applications. As a result, developers often need to spent time on infrastructure code - time which would be more effectively (and enjoyably) spent writing code for the project.

Jubilee is a lightweight app engine built on pygame. The purpose of Jubilee is to enable the rapid development of applications that typically have a main GUI process and a back-end worker process, with support for graphics, GUI elements, and interprocess messaging.

=== Quick Start ===

The Examples folder contains a variety of example projects that run right out of the box:

* Hello 			A Hello, World! project with an App class and a Worker (background) class.
* No Display	A "headless" project with no display. (Can still play sound and music.)
* Pointer			A project that demonstrates pointer input (and simple graphics).
* Images			A project that demonstrates images and sprite animations.
* Sound				A project that demonstrates sound and music.
* Modes				A project that demonstrates two modes, packaged into two Mode classes.
* Submodes		A project that demonstrates submodes.
* Script			A project that demonstrates mode scripting.

All of these projects can serve as study guides, as sandboxes to experiment with the
features, or as templates for new projects with similar features.

=== Overview of Architecture and Features ===

Jubilee includes two base classes: App and Worker. Each class can be subclassed to extend the methods with app-specific functionality. The App runs process() and draw() cycles to draw to a screen (unless App is declared as headless). The Worker runs process() and process_periodic() cycles in a separate process. An App can have multiple Workers that run as different processes. App communicates with each Worker via a dedicated pair of messaging queues, with the expectation that every message is a JSON object is automatically serialized (json.dumps) and deserialized (json.loads). App provides a function hook for process (intended for brief application-level tasks). Worker provides function hools for process and process_periodic (for evaluating less frequent tasks, such as once per second).

Some operating features of Jubilee are declared in config.txt, which App and Worker load during initialization. The first Worker monitors the modification date of config.txt during runtime and pushes updated configs to App via messaging queue. When Jubilee wants to change its configuration, it sends a message to Worker, which updates the config and sends the updated config (in its entirety) back to Jubilee. (Two reasons for this: first, to prevent both App and every Worker from having to monitor config.txt for updates; second, to prevent race conditions.)

* Modes: Jubilee includes a Mode class with a variety of function hooks: enter (when the mode begins), process, draw, and exit. The Mode class also includes a .controls array, and new Button instances can be added to an instance for the mode. Jubilee automatically handles conrol rendering and click detection by invoking a click_handler method, with properties for automatically switching the app to a target mode, or application exit.

* Modalities: Jubilee can run in a modal context, where each app process loop invokes the process function for the current mode, or a modeless context, where each app process loop invokes the process function for *every* mode. Jubilee also supports a headless mode. that runs without calling any graphics or mouse / touch functions, but with the usual process functions and even keyboard input checking.

* Submodes: Jubilee enables any mode to include a number of submodes. When a submode is set, the rocess and draw functions for the mode will automatically call the process_{submode} and draw_{submode} functions if they have been declared.

* Mode Script: For applications that require a particular sequence of states and substates, Jubilee supports the definition of a script. The script defines a set of numbered scenes, each of which indicates a mode and a set of parameters, optionally including a submode. The app or any mode can call app.advance_scene() to advance to the next scene in the script, or to jump to a particular scene. The state of the script can be saved and loaded.

* Resource Libraries: Jubilee looks for folders called images and sounds in the main app folder and uatomatically loads them into app-level resources libraries. For each mode, Jubilee also looks for a subfolder of the same name, looks for further images and sounds subfolders for the mode, and automatically loads mode-level resource libraries. Image blit and play_sound commands commands can then specify resources by filenames. Jubilee will look first in the library for the current mode, then in the application library.

* Animations and Sprites: Each images folder can contain a subfolder for an animation as a set of images corresponding to animation frames. Each subfolder is loaded into an Animation as a set of frames. For each mode, a set of Sprites can be generated, each having an Animation object, x/y coordinates, and a frame number. The sprites can be rendered during the draw cycle for the mode. Sprites can also animate on demand or automatically at a certain rate. Further, if some frames for an Animation are named consistently and numbered - e.g.: walk_left_1.jpg, walk_left_2.jpg, etc. - the Animation will store a Sequence indexed by the shared name (walk_left) and containing the frame numbers for the sequence. A Sprite can be set to a specific Sequence in a given Animation, and will animate (automatically and on-demand) over the frames of the Sequence.

* Input: On Linux, Jubilee will handle touch input if the config parameter touch_input is True. On MacOS, Jubilee automatically handles mouse events. Jubilee also provides functions for processing keyboard input, either on a key basis (held_keys and new_keys) and as a keyboard buffer. In both cases, by default, Jubilee receives and processes keyboard events.

=== Example Custom App Class ===

class Example_App(App):
	""" App-specific class. """

	def __init__(self):
		super().__init__(worker_classes=Example_Worker)

	def process(self):
		""" Main app process method. """
		super().process()
	
			Jubilee invokes this function at config['process_fps'] FPS. However,
			any significant processing here will delay draw functions and input reception,
			so should be kept minimal. The base method invokes mode-specific process method;
			this function can add functionality before or after that method. 

	def process_message(self, message):
		""" Process a message from worker. """
		action = message.get('action')
		if action == 'custom action':
			pass		# app-specific message handling
		else:			# handle default messages (e.g., 'update config' or 'exit')
			super().process_message(message)

App values:
	base_path																	# application base path
	config																		# application configuration
	headless																	# headless mode (defaults to False)
	screen_width															# screen width
	screen_height															# screen height
	screen_center															# screen center
	screen_middle															# screen middle
	margin = 5																# margin between content and screen edge (px)
	button_margin = 3													# margin between buttons (px)
	button_border = 1													# width of button border (px)
	underscore_position = 7										# pixels under text for underscores
	popover_message = None										# current popover message
	popover_duration = 2000										# duration of popover message
	fonts = {'freeserif': ... }								# array of fonts by name in default size
	default_font 															# default font name
	default_font_sizes = {6: ... }						# default font in various sizes (6-36)
	touch_input																# check for touch input

General methods:
	set_mode(mode)														# mode can be a name or a Mode object
	send_message(message)											# can be a string (action) or a JSON object
	update_config(key, value)									# message worker to update config
	exit(code = 0)														# exit function - can also be extended

Input:
	pointer																		# interface to pointer object (mouse or touch)
	pointer.x, pointer.y											# current coordinates
	pointer.down															# whether mouse button or touch is active
	on_click(x, y)														# runs click handler function with coordinate
	keys_down																	# array of keys that are newly pressed
	keys_pressed															# array of all keys that are currently down
	clear_keyboard_buffer()										# clear keyboard buffer for new text input
	keyboard_buffer														# string of text input since last clear
	keyboard_buffer_chars											# array of text input keys since last clear

Drawing:
	fill_screen(color = 'white')							# fill screen with specified color
	draw_text(text, x, y, color = None, font = None, alignment = 'left')
			# font can be either a pygame.font.SysFont, a font name, or None for default font
	get_text_size(text, font)									# returns (width, height)
	draw_pixel(x, y, color = 'white')
	draw_line(x1, y1, x2, y2, width = 1, color = 'white')
	draw_circle(x, y, radius = 1, color = 'white')
	draw_rect(left, top, width, height, line_width = 1, color = 'white')
	fill_rect(left, top, width, height, color = 'white')
	fill_screen(color = 'white')
	load_image(filename)
	scale_image(image, scale)									# specify scale as (width, height)
	shift_image_hue(image, delta)							# delta = value from 0 to 360
	blit(image, x, y, scale = None)						# specify scale as (width, height)
	set_popover(message, duration = None)			# default duration of 2.0 seconds
	change_font()															# choose next font in font list as default font
	redraw()																	# forces redraw after next process loop

Sound and music methods:
	set_sound_retainer(enable = True)					# play a very quiet noise loop to keep sound on
	set_volume(volume, sound_volume = None)		# specify volume(s) in range of 0-100
	play_music(filename, volume = None)				# play specified music via pygame mixer
	load_sound(sound)													# load sound from filename or buffer
	play_sound(sound, loops = None, volume = None)
	play_sound_on_channel(sound, loops = None, volume = None)
			# plays sound on dedicated channel; returns channel for .stop(), .get_busy(), etc.	

=== Example Custom Mode ===

class Mode_Custom(Mode):
	""" Custom mode class. """
	
	def __init__(self, app):
		super().__init__(app)
		self.name = 'Custom'

	def enter(self, app, parameters = None):
		""" Mode entry method. parameters may be from app or another mode. """

	def exit(self, app, parameters = None):
		""" Mode exit method. parameters may be from app or another mode. """

	def input(self, app, x, y):
		""" Input method for custom mode. """

	def process(self, app):
		""" Process method for custom mode. """

	def draw(self, app):
		""" Draw method for custom mode. """

Adding mode to app in Example_App.__init__():
	self.add_mode(Mode_Custom(app=self))

General methods:

	add_button(x, y, width, height, caption, target_mode = None, click_handler = None, app_exit = False, font = None, color = 'white', parameters = None)
		# specify click_handler_function(self, app), a name of a target mode, or app_exit=True.

	exit(code = 0)														# exit function - can be extended

	shut_down()																# shut down device - can be extended

Keyboard input: App provides keyboard input in three ways:
	1) app.keys_down: array of keys that were newly pressed as of last app.process()
	2) app.keys_pressed: array of all keys that are currently being held down
	3) app.keyboard_buffer: string containing a buffer for text input
				app.clear_keyboard_buffer() resets buffer.

=== Example Worker Class ===

class Example_Worker(Worker):
	""" App-specific worker class. """

	def __init__(self, app_queue, worker_queue, config_manager):
		super().__init__(app_queue, worker_queue, config_manager)

	def process(self):
		""" Regular (high-frequency) worker processing. """
		super().process()

	def process_periodic(self):
		""" Periodic (low-frequency) worker processing. """
		super().process_periodic()

	def process_message(self, message):
		""" Process a message from app. """
		action = message.get('action')
		if action == 'custom action':
			pass		# app-specific message handling
		else:			# handle default messages (e.g., 'update config' or 'exit')
			super().process_message(message)

General methods:
	send_message(message)													# can be a string (action) or a JSON object
	send_updated_config()													# sends config to app
	write_config()																# writes config and sends to app
	update_config(key, value)											# updates config; writes config; sends to app
	change_font(font_name)												# changes font; writes config; sends to app

Values:
	config																				# app configuration
	base_path																			# application base path

=== config.txt fields ===

"screen_resolution": [320, 240],								# screen resolution for drawing
"pointer_input": true,													# receive pointer (mouse or touch) events
"keyboard_input": false,												# receive keyboard events 
"screen_scale": [[0, 319, -1], [0, 239, 1]],		# screen range/direction for pointer input
"app_process_fps": 20,													# fps for app processing
"modal": false,																	# app_process => current mode or all modes
"app_draw_fps": 10,															# fps for draw_mode() 
"worker_process_fps": 20,												# fps for worker processing
"worker_process_periodic_fps": 1,								# fps for worker low-frequency processing
"font": "freeserif",														# default font name
"font_size": 14																	# default font size

===
