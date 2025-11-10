from typing import Any, Dict
from datetime import datetime

class UserSearchParams(Dict[str, Any]):
    def __init__(self, *, search_pattern: str, min_age: int, start_date: datetime, max_results: int):
        super().__init__(search_pattern=search_pattern, min_age=min_age, start_date=start_date, max_results=max_results)

QUERY = """SELECT 
    user_id,
    username,
    email,
    created_at
FROM users
WHERE 
    username LIKE {search_pattern:String}
    AND age >= {min_age:Int32}
    AND created_at >= {start_date:DateTime}
ORDER BY created_at DESC
LIMIT {max_results:Int32}"""
