from .start import register_start_handlers
from .echo import register_echo_handlers

def register_all_handlers(dp):
    register_start_handlers(dp)
    register_echo_handlers(dp)