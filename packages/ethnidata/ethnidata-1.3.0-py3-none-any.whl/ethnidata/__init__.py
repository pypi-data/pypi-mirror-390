"""
EthniData v1.3.0 - Complete Demographics Prediction from Names
Predict nationality, ethnicity, gender, region, language AND religion!

New in v1.3.0:
- 🕌 RELIGION PREDICTION! (Christianity, Islam, Hinduism, Buddhism, Judaism)
- 🌍 5 CONTINENTS: Americas, Europe, Asia, Africa, Oceania
- 🌐 165 COUNTRIES globally
- 🗣️  46 LANGUAGES
- 📊 220K+ names database
- 98%+ data coverage with religion info

Features:
- ✅ Nationality prediction (165 countries)
- ✅ Religion prediction - NEW! (5 major religions)
- ✅ Gender prediction
- ✅ Region prediction (5 continents)
- ✅ Language prediction (46 languages)
- ✅ Ethnicity prediction
- ✅ Full name analysis

Usage:
    from ethnidata import EthniData

    ed = EthniData()

    # Nationality
    result = ed.predict_nationality("Ahmet")

    # Religion (NEW!)
    result = ed.predict_religion("Muhammad")

    # Gender
    result = ed.predict_gender("Emma")

    # Region
    result = ed.predict_region("Chen")

    # Language
    result = ed.predict_language("José")

    # ALL at once
    result = ed.predict_all("Maria")
    # Returns: nationality, religion, gender, region, language, ethnicity
"""

__version__ = "1.3.0"
__author__ = "Tefik Yavuz Oz"
__license__ = "MIT"

from .predictor import EthniData

__all__ = ["EthniData"]
