CURL COMMANDS:

Verify Order_Service endpoints
After configuring the routes and plugins:
1. Test the GET Operation (Unauthenticated)
curl -X GET "http://localhost:8000/orders"

2. Test the POST Operation (Unauthenticated)
curl -X POST "http://localhost:8000/orders" -H "Content-Type: application/json" -d "{\"item_name\": \"Item B\", \"quantity\": 2, \"price\": 500.0, \"user_email\": \"saqibmurtazakhan@gmail.com\", \"user_phone\": \"03171938567\"}"

3. Test the PUT Operation (Authenticated)
curl -X PUT "http://localhost:8000/orders/1" ^
     -H "Content-Type: application/json" ^
     -u "saqibmurtazakhan:saqibmurtaza" ^
     -d "{\"item_name\": \"Updated Item\", \"quantity\": 3, \"price\": 150.0, \"user_email\": \"updatedemail@example.com\", \"user_phone\": \"03171938567\"}"



4. Test the DELETE Operation (Authenticated)
curl -X DELETE "http://localhost:8000/orders/1" ^
     -u "saqibmurtazakhan:saqibmurtaza"

