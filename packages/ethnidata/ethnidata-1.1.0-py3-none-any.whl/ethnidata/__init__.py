"""
EthniData v1.1.0 - Ethnicity, Nationality, Gender, Region and Language Prediction
Predict demographics from names using a comprehensive global database

New in v1.1.0:
- Gender prediction (Cinsiyet tahmini)
- Region prediction (Bölge: Europe, Asia, Americas, Africa, Oceania)
- Language prediction (Yaygın dil tahmini)
- predict_all() method - All predictions at once
- Enhanced data: 600K+ names from multiple sources

Usage:
    from ethnidata import EthniData

    ed = EthniData()

    # Nationality
    result = ed.predict_nationality("Ahmet")

    # Gender (NEW!)
    result = ed.predict_gender("Emma")

    # Region (NEW!)
    result = ed.predict_region("Chen")

    # Language (NEW!)
    result = ed.predict_language("José")

    # ALL at once (NEW!)
    result = ed.predict_all("Maria")
"""

__version__ = "1.1.0"
__author__ = "Tefik Yavuz Oz"
__license__ = "MIT"

from .predictor import EthniData

__all__ = ["EthniData"]
