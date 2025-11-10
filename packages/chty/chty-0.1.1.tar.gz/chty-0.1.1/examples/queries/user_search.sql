SELECT 
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
LIMIT {max_results:Int32}

