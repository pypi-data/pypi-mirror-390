from visions import VisionsBaseType

from typing import Any

class Handler:
    handlers = {}
    default_handler = None 

    @classmethod
    def register(cls, keyword):
        def decorator(func):
            cls.handlers[keyword] = func
            return func
        return decorator

    @classmethod
    def register_default(cls):
        def decorator(func):
            cls.default_handler = func
            return func
        return decorator

    @classmethod
    def render_bottom(cls, type, data, *args, **kwargs):
        if type in cls.handlers:
            return cls.handlerstype
        elif cls.default_handler is not None: 
            return cls.default_handler(data)
        else:
            raise ValueError(f"No handler registered for {type}")