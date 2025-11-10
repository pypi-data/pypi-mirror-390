# -----------------------------
# File: yemot_flow/__init__.py
# -----------------------------
"""
Yemot Flow - ספריית Python לבניית מערכות IVR עם ימות המשיח

דוגמה לשימוש:
```python
from yemot_flow import Flow

app = Flask(__name__)
flow = Flow(print_log=True)

@flow.get("")
async def welcome(call):
    digits = await call.read([('text', 'הקש מספר')], max_digits=1)
    if digits == "1":
        call.goto("info")
```
"""

from .flow import Flow  # noqa: F401
from .call import Call, CallInterrupted  # noqa: F401
from .utils import sanitize_text, clean_speech_text, validate_phone_number  # noqa: F401

__all__ = ["Flow", "Call", "CallInterrupted", "sanitize_text", "clean_speech_text", "validate_phone_number"]

# Version info
__version__ = "0.2.19"