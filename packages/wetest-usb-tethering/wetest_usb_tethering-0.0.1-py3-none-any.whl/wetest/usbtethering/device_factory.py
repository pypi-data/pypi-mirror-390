import logging
from typing import Callable, Dict, Optional

from .devices.base import BaseDevice
from .uiautomator_manager import UIAutomatorManager

logger = logging.getLogger(__name__)


def _create_honor_device(manager: UIAutomatorManager, timeout: int) -> "HonorDevice":
    """创建荣耀设备实例"""
    from .devices import HonorDevice

    return HonorDevice(manager, timeout)


def _create_oppo_device(manager: UIAutomatorManager, timeout: int) -> "OppoDevice":
    """创建OPPO设备实例"""
    from .devices import OppoDevice

    return OppoDevice(manager, timeout)


# 品牌与创建函数映射
SUPPORTED_BRANDS: Dict[str, Callable] = {"honor": _create_honor_device, "oppo": _create_oppo_device}


def create_device(
    device_serial: Optional[str] = None,
    max_retries: int = 3,
    timeout: int = 5,
    error_handler: Optional[Callable] = None,
) -> BaseDevice:
    """自动检测设备并创建合适的实例"""
    manager = UIAutomatorManager(device_serial, max_retries, error_handler)
    device_info = manager.device.device_info
    brand = device_info.get("brand", "unknown").lower()
    model = device_info.get("model", "unknown")
    logger.info(f"Detected device: {brand} ({model})")

    create_func = SUPPORTED_BRANDS.get(brand)
    if create_func:
        return create_func(manager, timeout)
    else:
        raise NotImplementedError(
            f"Device {brand} ({model}) is not supported. "
            f"Supported brands: {', '.join(SUPPORTED_BRANDS.keys())}. "
            f"Please check for updates or submit a feature request."
        )
