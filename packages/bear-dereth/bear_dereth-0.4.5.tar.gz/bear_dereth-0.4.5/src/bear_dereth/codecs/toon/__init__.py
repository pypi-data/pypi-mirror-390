"""An implementation of Token-Oriented Object Notation (TOON) codec.

{
  "users": [
    { "id": 1, "name": "Alice", "role": "admin" },
    { "id": 2, "name": "Bob", "role": "user" }
  ]
}

TOON conveys the same information with fewer tokens:

users[2]{id,name,role}:
  1,Alice,admin
  2,Bob,user
"""
