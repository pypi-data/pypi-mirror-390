from .game_objects import GameObject
from .helper import Color, vector3d, Light, Camera, Renderer
from pygame.time import Clock
import time

class Functions:
    def __init__(self):
        self.draw_cube = lambda pos=vector3d.zero, size=vector3d(3), color=Color.light_blue: None
        self.draw_sphere = lambda pos=vector3d.zero, radius=2, color=Color.light_red, segments=32, rings=16: None
        self.draw_cylinder = lambda pos=vector3d.zero, length=2, radius=.5, color=Color.light_yellow, segments=32: None
        self.add_light = lambda light: None
        self.add_object = lambda obj: None
        self.is_colliding_pos = lambda name, pos: None
        self.is_colliding = lambda name1, name2: None
        self.get_game_object = lambda name: None
        self.remove_object = lambda name: None
        self.remove_light = lambda name: None

class Delay:
    def __init__(self, delay_time, callback):
        self.start_time = time.perf_counter()
        self.delay_time = delay_time
        self.callback = callback
        self.finished = False

    def update(self):
        if time.perf_counter() - self.start_time >= self.delay_time:
            self.callback()
            self.finished = True

class DelayVar:
    def __init__(self, delay, obj, attr, value):
        self.start_time = time.perf_counter()
        self.delay = delay
        self.obj = obj
        self.attr = attr
        self.value = value
        self.finished = False

    def update(self):
        if time.perf_counter() - self.start_time >= self.delay:
            setattr(self.obj, self.attr, self.value)
            self.finished = True

class KeyCallback:
    def __init__(self, key, event_type, callback, args=None, dt=False):
        self.callback = callback
        self.key = key
        self.event_type = event_type
        self.dt = dt
        if not args:
            args = []
        self.args = args

    def update(self, pressed_keys, held_keys, released_keys, dt):
        if self.event_type == "pressed":
            if self.key in pressed_keys:
                if self.dt:
                    self.callback(dt, *self.args)
                else:
                    self.callback(*self.args)

        elif self.event_type == "held":
            if self.key in held_keys:
                if self.dt:
                    self.callback(dt, *self.args)
                else:
                    self.callback(*self.args)

        elif self.event_type == "released":
            if self.key in released_keys:
                if self.dt:
                    self.callback(dt, *self.args)
                else:
                    self.callback(*self.args)

class KeyCallbackVar:
    def __init__(self, key, event_type, obj, attr, value):
        self.key = key
        self.event_type = event_type
        self.obj = obj
        self.attr = attr
        self.value = value

    def update(self, pressed_keys, held_keys, releaed_keys):
        if self.event_type == "pressed":
            if self.key in pressed_keys:
                setattr(self.obj, self.attr, self.value)

        elif self.event_type == "held":
            if self.key in held_keys:
                setattr(self.obj, self.attr, self.value)

        elif self.event_type == "released":
            if self.key in releaed_keys:
                setattr(self.obj, self.attr, self.value)

class ScheduledCaller:
    def __init__(self, n_times, callback, delay, caller_id):
        self.n_times = n_times
        self.callback = callback
        self.delay = delay
        self.caller_id = caller_id
        self.finished = False
        self.delay_obj = Delay(self.delay, self.callback)

    def update(self):
        self.delay_obj.update()
        if self.delay_obj.finished:
            self.n_times -= 1
            self.delay_obj = Delay(self.delay, self.callback)

        self.finished = self.n_times < 0

class Context:
    def __init__(self):
        self.functions: Functions = Functions()
        self.ambient_light: float = .2
        self.lights: list[Light] = []
        self.game_objects: list[GameObject] = []
        self.mouse_sensitivity: float = 0.3
        self.pan_sensitivity: float  = 0.005
        self.fps: int | float = 0
        self.engine = None
        self.camera: Camera | None = None
        self.clock: Clock | None = None
        self.renderer: Renderer | None = None
        self.keys_held: list[str] = []
        self.keys_pressed: list[str] = []
        self.keys_released: list[str] = []
        self.key_callbacks: list[KeyCallback] = []
        self.key_callback_vars: list[KeyCallbackVar] = []
        self.delays: list[Delay] = []
        self.delay_vars: list[DelayVar] = []
        self.scheduled_callers: list[ScheduledCaller] = []
        self.exit = False

    def on_key_press(self, key, callback, args=None, dt=False):
        if args is None:
            args = []
        self.key_callbacks.append(KeyCallback(key, "pressed", callback, args, dt))

    def on_key_held(self, key, callback, args=None, dt=False):
        if args is None:
            args = []
        self.key_callbacks.append(KeyCallback(key, "held", callback, args, dt))

    def on_key_released(self, key, callback, args=None, dt=False):
        if args is None:
            args = []
        self.key_callbacks.append(KeyCallback(key, "released", callback, args, dt))

    def on_key_press_var(self, key, obj, attr, value):
        self.key_callback_vars.append(KeyCallbackVar(key, "pressed", obj, attr, value))

    def on_key_held_var(self, key, obj, attr, value):
        self.key_callback_vars.append(KeyCallbackVar(key, "held", obj, attr, value))

    def on_key_released_var(self, key, obj, attr, value):
        self.key_callback_vars.append(KeyCallbackVar(key, "released", obj, attr, value))

    def update(self, dt):
        for callback in self.key_callbacks:
            callback.update(self.keys_pressed, self.keys_held, self.keys_released, dt)

        for callback_var in self.key_callback_vars:
            callback_var.update(self.keys_pressed, self.keys_held, self.keys_released)

        delays = self.delays[:]
        for delay in delays:
            delay.update()
            if delay.finished:
                self.delays.remove(delay)

        delay_vars = self.delay_vars[:]
        for delay in delay_vars:
            delay.update()
            if delay.finished:
                self.delay_vars.remove(delay)

        scheduled_callers = self.scheduled_callers[:]
        for caller in scheduled_callers:
            caller.update()
            if caller.finished:
                self.scheduled_callers.remove(caller)

    def add_delay(self, delay, callback):
        self.delays.append(Delay(delay, callback))

    def add_delay_var(self, delay, obj, attr, value):
        self.delay_vars.append(DelayVar(delay, obj, attr, value))

    def add_scheduled_caller(self, n_times, delay, callback, caller_id=None):
        if caller_id is None:
            max_id = -1
            if self.scheduled_callers:
                max_id = max([caller.caller_id for caller in self.scheduled_callers])
            caller_id = max_id + 1
        self.scheduled_callers.append(ScheduledCaller(n_times, callback, delay, caller_id))
