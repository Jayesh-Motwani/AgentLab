import contextvars

current_sources = contextvars.ContextVar("current_sources", default=None)
