CURL COMMANDS

Verify User_Service endpoints

1. For GET Requests:
Request to /user:
curl -X GET "http://localhost:8000/user" ^
     -u "saqibmurtazakhan:saqibmurtaza"
Request to /user/signup:
Description: Registers a new user.
curl -X POST "http://localhost:8000/user/signup" ^
     -H "Content-Type: application/json" ^
     -d "{\"username\": \"newuser\", \"email\": \"newuser@example.com\", \"password\": \"password123\", \"action\": \"Signup\"}"
2. POST /user/login
Description: Logs in an existing user.
curl -X POST "http://localhost:8000/user/login" ^
     -H "Content-Type: application/json" ^
     -d "{\"username\": \"newuser\", \"email\": \"newuser@example.com\", \"password\": \"password123\", \"action\": \"Login\"}"

3. GET /user/profile
Description: Retrieves user profile information. Requires a token.
curl -X GET "http://localhost:8000/user/profile?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjozLCJlbWFpbCI6Im5ld3VzZXJAZXhhbXBsZS5jb20iLCJleHAiOjE3MjQ5NjMyNDUsImlzcyI6Ik15X1NlY3JldF9LZXkifQ.J5PuXHfJ2Dhn5ZGpPciy92HvuoTsXNSZwqfxIxM8VQo" ^
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjozLCJlbWFpbCI6Im5ld3VzZXJAZXhhbXBsZS5jb20iLCJleHAiOjE3MjQ5NjMyNDUsImlzcyI6Ik15X1NlY3JldF9LZXkifQ.J5PuXHfJ2Dhn5ZGpPciy92HvuoTsXNSZwqfxIxM8VQo"


