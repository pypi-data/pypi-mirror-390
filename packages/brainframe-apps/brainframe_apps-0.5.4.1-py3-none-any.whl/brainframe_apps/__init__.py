try:
    from importlib.metadata import version
    __version__ = version("brainframe-apps")
except Exception:
    __version__ = "unknown"

from .cli import cli_main
from .add_stream import add_stream_main
from .capsule_control import capsule_control_main
from .delete_stream import delete_stream_main
from .get_configuration import save_settings_main
from .get_zone_statuses import get_zone_statuses_main
from .identity_control import identity_control_main
from .license_control import license_control
from .list_stream import list_stream_main
from .process_image import process_image_main
from .set_configuration import load_settings_main
from .start_analyzing import start_analyzing_main
from .stop_analyzing import stop_analyzing_main
from .user_control import user_control
