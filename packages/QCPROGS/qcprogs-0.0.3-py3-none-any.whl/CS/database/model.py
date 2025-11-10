from typing import TypedDict, Dict, List

class RuleItem(TypedDict):
    RESULT: str
    STATUS: str

class DataMapItem(TypedDict):
    SCHEMA: str
    TABEL: str
    RULE_MAP: Dict[str, RuleItem]
    QUERY: str

