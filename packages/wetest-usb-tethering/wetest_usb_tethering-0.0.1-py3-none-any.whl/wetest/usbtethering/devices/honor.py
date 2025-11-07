from .base import BaseDevice


class HonorDevice(BaseDevice):
    """荣耀设备，当前仅支持 MYA-TL10 机型"""

    def _toggle_usb_tethering_on(self) -> bool:
        """执行`开启 USB 共享`的具体操作"""
        for _ in range(3):
            self.shell("input keyevent KEYCODE_DPAD_DOWN")
        self.shell("input keyevent KEYCODE_ENTER")
