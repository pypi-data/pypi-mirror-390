"""
Kapetanios Unit Root Test Package
==================================

Unit root testing against the alternative hypothesis of up to m structural breaks.

Based on: Kapetanios, G. (2005). Unit-root testing against the alternative 
hypothesis of up to m structural breaks. Journal of Time Series Analysis, 
26(1), 123-133.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/kapetanios
"""

from .core import KapetaniosTest, KapetaniosResult, kapetanios_test

__version__ = "1.0.1"
__author__ = "Dr. Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"

__all__ = [
    "KapetaniosTest",
    "KapetaniosResult",
    "kapetanios_test",
]
