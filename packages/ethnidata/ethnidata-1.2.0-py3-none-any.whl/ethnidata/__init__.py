"""
EthniData v1.2.0 - Ethnicity, Nationality, Gender, Region and Language Prediction
Predict demographics from names using a comprehensive global database

New in v1.2.0:
- Enhanced database: 310K+ unique names (120K first names, 190K last names)
- 172 countries, 4 regions (Americas, Europe, Asia, Oceania)
- Unified database schema for faster queries
- Improved data quality from Olympics, US Census, Phone Directories
- Better country normalization

Features:
- Nationality prediction
- Gender prediction
- Region prediction (Europe, Asia, Americas, Africa, Oceania)
- Language prediction
- Full name analysis

Usage:
    from ethnidata import EthniData

    ed = EthniData()

    # Nationality
    result = ed.predict_nationality("Ahmet")

    # Gender
    result = ed.predict_gender("Emma")

    # Region
    result = ed.predict_region("Chen")

    # Language
    result = ed.predict_language("José")

    # ALL at once
    result = ed.predict_all("Maria", "Garcia")
"""

__version__ = "1.2.0"
__author__ = "Tefik Yavuz Oz"
__license__ = "MIT"

from .predictor import EthniData

__all__ = ["EthniData"]
