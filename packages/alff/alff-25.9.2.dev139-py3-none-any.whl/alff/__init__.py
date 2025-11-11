"""
<img src="./1images/kde_color_128x128.png" style="float: left; margin-right: 20px" width="120" />

ALFF: Frameworks for Active Learning of Graph-based Force Fields and Computation of Material Properties.

Developed and maintained by [C.Thang Nguyen](https://thangckt.github.io)
"""

from pathlib import Path

ALFF_ROOT = Path(__file__).parent

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.1_fallback"

__author__ = "C.Thang Nguyen"
__contact__ = "http://thangckt.github.io/email"


# warnings.filterwarnings(action="ignore", module=".*paramiko.*")
