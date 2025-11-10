# ================================================================
# File: yemot_flow/call.py
# ================================================================
"""Call – אובייקט שיחה בודדת עם תמיכה ב-async"""
from __future__ import annotations

import asyncio
from typing import List, Tuple, Optional, Any, Union, TYPE_CHECKING

from .actions import build_go_to_folder, build_id_list_message, build_read
from .utils import now_ms

if TYPE_CHECKING:
    from .flow import Flow

Message = Tuple[str, str]


class CallInterrupted(Exception):
    """נזרק כשהשיחה צריכה להיפסק לקבלת קלט מהמשתמש"""
    def __init__(self, response: str):
        self.response = response
        super().__init__()


class Call:
    """
    אובייקט שיחה יחידה עם תמיכה מלאה ב-async/await
    
    Methods:
        read() -> str: קבלת קלט מהמשתמש (מחזיר את הקלט ישירות)
        play_message() -> None: השמעת הודעה למשתמש
        goto() -> None: מעבר לשלוחה אחרת
        hangup() -> None: ניתוק השיחה
    """
    
    def __init__(self, params: dict, *, flow: "Flow") -> None:
        self.params: dict = params.copy()
        self.flow: "Flow" = flow
        self.call_id: Optional[str] = params.get("ApiCallId")
        self.response_parts: List[str] = []
        self.last_activity_ms: int = now_ms()
        self._waiting_for_input: bool = False
        self._expected_param: Optional[str] = None
        self._handler_state: str = "fresh"  # fresh, waiting_input, completed

    def update_params(self, new_params: dict) -> None:
        """עדכון פרמטרי השיחה"""
        self.params.update(new_params)
        self.last_activity_ms = now_ms()

    # -------- API Methods --------
    
    def play_message(
        self, 
        messages: List[Message], 
        *, 
        remove_invalid_chars: Optional[bool] = None,
        url_encode: bool = False
    ) -> None:
        """
        השמעת הודעות למשתמש
        
        Args:
            messages: רשימת הודעות כ-tuples של (סוג, תוכן)
                     למשל: [('text', 'שלום'), ('file', 'welcome.wav')]
            remove_invalid_chars: האם לנקות תווים לא חוקיים
            url_encode: האם לקודד URL (שימושי לעברית)
        
        Example:
            call.play_message([('text', 'ברוכים הבאים')])
        """
        response = build_id_list_message(messages, remove_invalid_chars=remove_invalid_chars, url_encode=url_encode)
        raise CallInterrupted(response)

    async def read(
        self, 
        messages: List[Message], 
        *, 
        mode: str = "tap",
        pre_message: Optional[List[Message]] = None,
        val_name: str = "Digits",
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
        """
        קבלת קלט מהמשתמש - מחזיר את התוצאה ישירות
        
        Args:
            messages: הודעות לקבלת הקלט [('text', 'הקש מספר')]
            mode: סוג הקלט - 'tap' (הקשה), 'record' (הקלטה), 'stt' (זיהוי דיבור)
            pre_message: הודעה להשמעה לפני הקלט (שילוב עם &)
            val_name: שם הפרמטר שיוחזר
            max_digits: מספר ספרות מקסימלי
            min_digits: מספר ספרות מינימלי  
            digits_allowed: ספרות מותרות (למשל: "123")
            sec_wait: זמן המתנה בשניות
            replace_char: תו סיום (בדרך כלל "#")
            path: נתיב לשמירת הקלטה
            file_name: שם קובץ להקלטה
            max_length: אורך מקסימלי להקלטה (שניות)
            lang: שפה לזיהוי דיבור (he-IL/en-US)
        
        Returns:
            str: הקלט שהתקבל מהמשתמש
            
        ⚠️ ניקוי אוטומטי:
            - STT: מילות מילוי (אה, אמ) + תווים אסורים
            - מספרי טלפון (val_name מכיל "phone"/"tel"): ואלידציה
            - הודעות: גרשיים נמחקים, נקודות/& הופכים לפסיק
            
        Examples:
            # קבלת מספר
            digits = await call.read([('text', 'הקש מספר')], max_digits=1, digits_allowed="123")
            
            # הקלטה
            file_path = await call.read([('text', 'תתחיל הקלטה')], mode="record", max_length=60)
            
            # זיהוי דיבור
            name = await call.read([('text', 'אמור את שמך')], mode="stt", val_name="name", lang="he-IL")
            
            # טלפון (ניקוי אוטומטי)
            phone = await call.read([('text', 'אמור טלפון')], mode="stt", val_name="phone", lang="he-IL")
        """
        
        # אם יש כבר קלט מהקריאה הקודמת
        existing_value = self.params.get(val_name)
        
        if existing_value is not None:
            # ניקוי אוטומטי לתוצאות זיהוי דיבור
            if mode == "stt":
                from .utils import clean_speech_text, sanitize_text, validate_phone_number
                # ניקוי מילות מילוי
                cleaned = clean_speech_text(existing_value)
                
                # בדיקה מיוחדת למספר טלפון
                if "phone" in val_name.lower() or "tel" in val_name.lower():
                    cleaned = validate_phone_number(cleaned)
                else:
                    # ניקוי תווים אסורים רגיל
                    cleaned = sanitize_text(cleaned, remove_invalid_chars=True)
                
                return cleaned
            elif mode == "record":
                # הקלטה - מחזיר את הנתיב כמו שהוא
                return existing_value
            else:
                # הקשות רגילות - מחזיר כמו שהוא
                return existing_value
        
        # אין קלט - צריך לבקש מהמשתמש
        
        # מכין את כל הפרמטרים לbuild_read
        all_opts = {**opts, "val_name": val_name, "max_digits": max_digits, "min_digits": min_digits, 
                   "digits_allowed": digits_allowed, "sec_wait": sec_wait, "replace_char": replace_char,
                   "path": path, "file_name": file_name, "max_length": max_length, "lang": lang}
        
        # אם יש הודעה מקדימה, נשלב אותה
        if pre_message:
            from .actions import build_id_list_message, build_combined_action
            pre_action = build_id_list_message(pre_message)
            read_action = build_read(messages, mode=mode, **all_opts)
            response = build_combined_action([pre_action, read_action])
        else:
            response = build_read(messages, mode=mode, **all_opts)
            
        raise CallInterrupted(response)

    def goto(self, folder: str) -> None:
        """
        מעבר לשלוחה אחרת
        
        Args:
            folder: שם השלוחה למעבר אליה
                   "" או "/" - שלוחה ראשית
                   "info" - שלוחת מידע
                   "hangup" - ניתוק השיחה
        
        Example:
            call.goto("info")  # מעבר לשלוחת מידע
            call.goto("")      # חזרה לשלוחה הראשית
        """
        response = build_go_to_folder(folder)
        raise CallInterrupted(response)

    def hangup(self) -> None:
        """
        ניתוק השיחה
        
        Example:
            call.hangup()  # מנתק את השיחה
        """
        self.goto("hangup")

    def play_and_read(self, play_messages: List[Message], read_messages: List[Message], **read_opts):
        """השמעת הודעה ואז קבלת קלט - כל זה באותה תגובה"""
        from .actions import build_id_list_message, build_read, build_combined_action
        
        play_action = build_id_list_message(play_messages)
        read_action = build_read(read_messages, **read_opts)
        
        combined = build_combined_action([play_action, read_action])
        raise CallInterrupted(combined)

    def render_response(self) -> str:
        """עיבוד התגובה הסופית - לא אמור להיקרא עוד"""
        if not self.response_parts:
            return "noop"
        resp = "\n".join(self.response_parts)
        self.response_parts.clear()
        return resp

