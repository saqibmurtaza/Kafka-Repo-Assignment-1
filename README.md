User_Service:
User_Registration:
curl -X POST "http://localhost:8000/user/signup" --header "Content-Type: application/json" --data-raw "{\"username\": \"Saqib\", \"email\": \"saqibmurtaza@hotmail.com\", \"password\": \"saq321\", \"action\": \"Signup\"}"
User_Login:
curl -X POST "http://localhost:8000/user/login" --header "Content-Type: application/json" --header "apikey: 26e112195dd24e9c31bd6f2aed28473d" --data-raw "{\"email\": \"saqibmurtaza@hotmail.com\", \"password\": \"saq321\"}"

User_Profile:
curl -X GET "http://localhost:8000/user/profile" --header "email: saqibmurtaza@yahoo.com" --header "apikey:53e9e343ae6f00913924c985a3f01058"
User_List:

curl -X GET "http://localhost:8000/user" -H "accept: application/json" -H "email: saqibmurtaza@yahoo.com" -H "apikey: 53e9e343ae6f00913924c985a3f01058"
Order_service
Create_order:
curl -X POST "http://localhost:8000/orders" -H "Content-Type: application/json" -d "{\"item_name\": \"Afghani Carpet\", \"quantity\": 12, \"price\": 200, \"status\": \"pending\", \"user_email\": \"saqibmurtaza@hotmail.com\", \"user_phone\": \"03099457645\"}"
Update Order:

curl -X PUT "http://localhost:8000/orders/b4b0c1cd-1e30-4578-86e6-3f1a0e1d3835" -H "Content-Type: application/json" -H "apikey: 53e9e343ae6f00913924c985a3f01058" -H "email: saqibmurtaza@yahoo.com" -d "{\"item_name\": \"Games Gold\", \"quantity\": 100, \"price\": 200.50, \"status\": \"processing\", \"user_email\": \"saqibmurtaza@yahoo.com\", \"user_phone\": \"03171938567\"}"
Track Order:
curl -X GET "http://localhost:8000/orders/067d5b0a-1791-4cec-baf7-ff3603522cea"

Delete Order:
curl -X DELETE "http://localhost:8000/orders/067d5b0a-1791-4cec-baf7-ff3603522cea "
Orders List:

curl -X GET "http://localhost:8000/orders" ^
     -H "Content-Type: application/json"
Product Service:
1. Create Product (POST /product)
curl -X POST http://localhost:8000/product -H "Content-Type: application/json" -d "{\"product_name\": \"Trousers\", \"description\": \"i-5\", \"price\": 125.99}"



2. Get Product by ID (GET /product/{id})
curl -X GET http://localhost:8000/product/2

3. Delete Product by ID (DELETE /product/{id})
curl -X DELETE "http://localhost:8000/product/1" -H "apikey: 53e9e343ae6f00913924c985a3f01058" -H "email: saqibmurtaza@yahoo.com"
5. Update Product by ID (PUT /product/{id})
curl -X PUT http://localhost:8000/product/4 -H "Content-Type: application/json" -H "apikey: 53e9e343ae6f00913924c985a3f01058" -H "email: saqibmurtaza@yahoo.com" -d "{\"product_name\": \"Jeans\", \"description\": \"Cotton\", \"price\": 30.99}"

6. Get List of All Products (GET /product)
curl -X GET http://localhost:8000/product

Inventory Service:
1. Create Inventory (POST)

curl -X POST http://localhost:8000/inventory -H "Content-Type: application/json" -d "{\"item_name\": \"Ceiling Fans\", \"price\": 100.0, \"quantity\": 2, \"threshold\": 5, \"description\": \"item description\", \"email\": \"saqibmurtaza@yahoo.com\", \"stock_in_hand\": 10, \"unit_price\": 100.0}"
2. Track Inventory (GET)
curl -X GET http://localhost:8000/inventory/12

3. Update Inventory (PUT)
curl -X PUT http://localhost:8000/inventory/12 -H "Content-Type: application/json" -H "apikey: 53e9e343ae6f00913924c985a3f01058" -H "email: saqibmurtaza@yahoo.com" -d "{\"item_name\":\"Mangoes\",\"description\":\"Delicious fruit jam\",\"unit_price\":100.0,\"quantity\":1,\"stock_in_hand\":3,\"threshold\":5,\"email\":\"saqibmurtaza@yahoo.com\"}"
4. Delete Inventory (DELETE)
curl -X DELETE http://localhost:8000/inventory/13 -H "apikey: 53e9e343ae6f00913924c985a3f01058" -H "email: saqibmurtaza@yahoo.com"

5. Get List of All Products (GET /product)
curl -X GET http://localhost:8000/inventory



.env
MOCK_SUPABASE=true
SUPABASE_URL=https://nueavvbhalbwtwtgpejb.supabase.co
SUPABASE_DB_URL=postgresql://postgres.nueavvbhalbwtwtgpejb:saqibmurtaza@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51ZWF2dmJoYWxid3R3dGdwZWpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTkxMzg1ODIsImV4cCI6MjAzNDcxNDU4Mn0.Ole302HtcSWGcX_2W6ZFYCRk8lqG4Wqn54DZ3NczLSI

#EMAIL_CONFIGS
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=saqibkhan.gemini@gmail.com
EMAIL_APP_PASSWORD=wbvf ojko ngpn sxxx

# Kafka Configuration
BOOTSTRAP_SERVER=broker:19092
KAFKA_CLUSTERS_0_NAME=Local Kafka Cluster
KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS=broker:19092
DYNAMIC_CONFIG_ENABLED=true

#Topics & Consumer_Groups configuration

#PRODUCT_SERVICE
TOPIC_PRODUCT_CRUD=topic_products_crud
CONSUMER_GROUP_PRODUCT_MANAGER=consumer_product_manager
# CONSUMER_GROUP_NOTIFYME_MANAGER=consumer_notifyme_manager

#INVENTORY_SERVICE
TOPIC_INVENTORY_UPDATES=inventory_updates
TOPIC_NOTIFY_INVENTORY=notify_inventory
CONSUMER_GROUP_INV_MANAGER=consumer_inv_manager
CONSUMER_GROUP_NOTIFY_MANAGER=consumer_notify_manager

#ORDER_SERVICE
TOPIC_ORDER_STATUS=order_status

#USER_SERVICE
TOPIC_USER_EVENTS=user_events

#NOTIFICATION_SERVICE
CONSUMER_GROUP_NOTIFY_ORDER_STATUS=consumer_notify_order_status
CONSUMER_GROUP_NOTIFY_EVENTS=consumer_notify_events
TOPIC_ORDER_STATUS=order_status
TOPIC_USER_EVENTS=user_events

#TOKEN
JWT_SECRET=My_Secret_Key
JWT_ALGORITHM=HS256

PAYMENT_SERVICE
TOPIC_PAYMENT_EVENTS=payment_events
TOPIC_ORDER_STATUS=order_status
CONSUMER_GROUP_PAYMENT_EVENTS=consumer_payment_events
STRIPE_API_KEY=sk_test_51IydepGpWKw7OGqVMLwFITvZJrXFdZDhpNeujoZMrBRQQDqzYZWK2OjEDId00i2Qcap6aubiWD4iOW8ZlfB3eSde00grScqgkd

#URL's
PAYMENT_SERVICE_URL="http://payment_service:8012"
NOTIFICATION_SERVICE_URL="http://notification_service:8008"