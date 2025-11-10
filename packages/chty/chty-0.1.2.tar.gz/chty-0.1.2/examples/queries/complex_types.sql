SELECT 
    user_id,
    tags,
    metadata
FROM users
WHERE 
    user_id = {user_id:Int64}
    AND tags IN {tag_list:Array(String)}
    AND is_active = {is_active:Bool}
    AND score >= {min_score:Nullable(Float64)}

