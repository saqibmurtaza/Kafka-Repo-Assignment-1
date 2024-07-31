# from datetime import datetime, timedelta, timezone
# import logging, jwt

# logging.basicConfig(level=logging.INFO)
# logger= logging.getLogger(__name__)

# key = "MRy3dx22zlCTvOUgo5tCrV0MypZh55Hf"
# secret = "zgPp1iKUPWeGYQrXesv7mzkTOe3BJHbd"

# payload= {
#     "iss": key,
#     "exp" : datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes),

# }
# token = jwt.encode(payload, secret, algorithm="HS256")
# logging.info(f'Token : {token}')
# print(token)

import datetime
import jwt

key = "MRy3dx22zlCTvOUgo5tCrV0MypZh55Hf"
secret = "zgPp1iKUPWeGYQrXesv7mzkTOe3BJHbd"

payload = {
    "iss": key,
    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
}

try:
    token = jwt.encode(payload, secret, algorithm="HS256")
    print("Generated JWT Token:")
    print(token)
except Exception as e:
    print("Error generating token:", str(e))
