# Type stubs for call.py - משפר IntelliSense
from typing import List, Tuple, Optional, Union

Message = Tuple[str, str]

class CallInterrupted(Exception):
    response: str
    def __init__(self, response: str) -> None: ...

class Call:
    """אובייקט שיחה עם תמיכה ב-async/await"""
    
    call_id: Optional[str]
    params: dict
    
    def __init__(self, params: dict, *, flow: "Flow") -> None: ...
    
    def play_message(
        self, 
        messages: List[Message], 
        *, 
        remove_invalid_chars: Optional[bool] = None,
        url_encode: bool = False
    ) -> None:
        """השמעת הודעות למשתמש"""
        ...
    
    async def read(
        self, 
        messages: List[Message], 
        *, 
        mode: str = "tap",
        pre_message: Optional[List[Message]] = None,
        val_name: str = "val",
        max_digits: Union[int, str] = "*",
        min_digits: int = 1,
        digits_allowed: str = "",
        sec_wait: int = 7,
        replace_char: str = "*/",
        path: str = "",
        file_name: str = "",
        max_length: int = 120,
        lang: str = "he-IL",
        **opts
    ) -> Optional[str]:
        """קבלת קלט מהמשתמש - מחזיר את התוצאה"""
        ...
    
    def goto(self, folder: str) -> None:
        """מעבר לשלוחה אחרת"""
        ...
    
    def hangup(self) -> None:
        """ניתוק השיחה"""
        ...