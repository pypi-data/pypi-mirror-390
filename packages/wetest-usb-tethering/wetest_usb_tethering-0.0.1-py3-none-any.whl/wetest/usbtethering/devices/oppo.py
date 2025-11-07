from .base import BaseDevice


class OppoDevice(BaseDevice):
    """OPPO A59s"""

    def _toggle_usb_tethering_on(self) -> bool:
        """执行`开启 USB 共享`的具体操作"""
        for _ in range(2):
            self.shell("input keyevent KEYCODE_ENTER")
