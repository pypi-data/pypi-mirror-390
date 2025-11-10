"""
EthniData v2.0.0 - MASSIVE UPDATE! Global Demographics Prediction
Predict nationality, ethnicity, gender, region, language AND religion!

🔥 NEW in v2.0.0 - MASSIVE DATABASE EXPANSION:
- 📊 **415K+ records** (88% increase from 220K)
- 🌍 **238 countries** (up from 165)
- 🗣️  **72 languages** (up from 46)
- 🕌 **Enhanced religious coverage** - More balanced distribution!
  - Islam: 69K+ records (was 2.8K)
  - Christianity: 122K+ records
  - Hinduism: 3.9K+ records (was 171)
  - Buddhism: 6.8K+ records (was 490)
  - Judaism: 4.8K+ records (was 3.5K)
- 🌎 **Better regional balance**:
  - Europe: 37.6% • Americas: 32.3%
  - Asia: 14.1% • Africa: 13.4% • Oceania: 2.0%

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

__version__ = "2.0.0"
__author__ = "Tefik Yavuz Oz"
__license__ = "MIT"

from .predictor import EthniData

__all__ = ["EthniData"]
