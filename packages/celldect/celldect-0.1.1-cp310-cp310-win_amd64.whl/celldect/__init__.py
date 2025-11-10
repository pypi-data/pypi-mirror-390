import os
import sys

try:
    from .compiled.core import *
except ImportError as e:
    # 如果是开发模式，从.pyx文件导入
    try:
        from .core import *
    except ImportError:
        raise ImportError(
            "Failed to import compiled modules. "
            "Please ensure the package was properly installed."
        ) from e

__version__ = "0.1.0"