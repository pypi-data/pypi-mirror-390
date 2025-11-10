SELECT number, number * {multiplier:Int32} AS result 
FROM system.numbers 
WHERE number < {limit:Int32}

