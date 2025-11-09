"""
EthniData - Ethnicity and Nationality Prediction from Names
Predict nationality, ethnicity, and demographics from names

Usage:
    from ethnidata import EthniData

    ed = EthniData()

    # Predict nationality
    result = ed.predict_nationality("Ahmet")
    # {'name': 'ahmet', 'country': 'TUR', 'confidence': 0.85, 'top_countries': [...]}

    # Predict ethnicity
    result = ed.predict_ethnicity("Tanaka", name_type="last")
    # {'name': 'tanaka', 'ethnicity': 'East Asian', 'country': 'JPN', ...}
"""

__version__ = "1.0.0"
__author__ = "Tefik Yavuz Oz"
__license__ = "MIT"

from .predictor import EthniData

__all__ = ["EthniData"]
