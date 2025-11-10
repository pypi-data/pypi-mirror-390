from typing import Any, Dict


class ComplexTypesParams(Dict[str, Any]):
    """Type-safe parameters for the query."""

    def __init__(self, *, user_id: int, tag_list: list[str], is_active: bool, min_score: float | None):
        super().__init__(user_id=user_id, tag_list=tag_list, is_active=is_active, min_score=min_score)


QUERY = """SELECT 
    user_id,
    tags,
    metadata
FROM users
WHERE 
    user_id = {user_id:Int64}
    AND tags IN {tag_list:Array(String)}
    AND is_active = {is_active:Bool}
    AND score >= {min_score:Nullable(Float64)}

"""
