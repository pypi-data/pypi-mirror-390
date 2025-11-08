import time
import datetime
from python_plugins.jwt import jwt_encode, jwt_decode


def test_jwt(fake):
    payload = {"some": fake.sentence()}
    key = fake.vin()
    # print(payload, key)
    token = jwt_encode(payload, key)
    # print(token)
    decoded = jwt_decode(token, key)
    # print(decoded)
    assert decoded["some"] == payload["some"]
    delta = 100
    token = jwt_encode(payload, key, delta)
    # print(token)
    decoded = jwt_decode(token, key)
    # print(decoded)
    assert decoded["some"] == payload["some"]
    # print(decoded["exp"],time.mktime(datetime.datetime.now().timetuple()))
    assert "exp" in decoded
    exp_time = time.mktime(datetime.datetime.now().timetuple()) + delta - 10
    assert decoded["exp"] > exp_time
    # print(datetime.datetime.fromtimestamp(decoded["exp"]))
