"""
EthniData v3.0.0 - ULTRA MASSIVE EXPANSION! Global Demographics Prediction
Predict nationality, ethnicity, gender, region, language AND religion!

🔥 NEW in v3.0.0 - ULTRA MASSIVE DATABASE EXPANSION:
- 📊 **5.8M+ records** (14x increase from v2.0.0 - 1,290% growth!)
- 🌍 **238 countries** - complete global coverage
- 🗣️  **72 languages**
- 🕌 **Dramatically enhanced religious coverage**:
  - Christianity: 3.7M+ records
  - Buddhism: 1.1M+ records (massive Asian expansion)
  - Islam: 500K+ records
  - Hinduism: 90K+ records
  - Judaism: 4.8K+ records
- 🌎 **Perfectly balanced regional distribution**:
  - Asia: 34% • Americas: 32% • Africa: 31% • Europe: 3% • Oceania: 0.1%

Features:
- ✅ Nationality prediction (238 countries)
- ✅ Religion prediction (5 major religions)
- ✅ Gender prediction
- ✅ Region prediction (5 continents)
- ✅ Language prediction (72 languages)
- ✅ Ethnicity prediction
- ✅ Full name analysis

Usage:
    from ethnidata import EthniData

    ed = EthniData()

    # Nationality
    result = ed.predict_nationality("Ahmet")

    # Religion
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

__version__ = "3.0.0"
__author__ = "Tefik Yavuz Oz"
__license__ = "MIT"

from .predictor import EthniData

__all__ = ["EthniData"]
