"""
Time Doctor Scraper Package
A Python package for scraping and exporting Time Doctor time tracking data
"""

from .parser import TimeDoctorParser
from .scraper import TimeDoctorScraper
from .transformer import TimeDoctorTransformer, export_to_csv, get_hours_summary

__version__ = "1.1.0"
__author__ = "Time Doctor Scraper"

__all__ = [
    "TimeDoctorScraper",
    "TimeDoctorParser",
    "TimeDoctorTransformer",
    "export_to_csv",
    "get_hours_summary",
]
