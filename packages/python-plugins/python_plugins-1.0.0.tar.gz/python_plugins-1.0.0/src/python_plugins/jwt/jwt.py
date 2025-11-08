import jwt
import datetime


def jwt_encode(payload: dict, key: str, delta: int = None, algorithm="HS256"):
    """encode payload.

    :param payload: _description_
    :param key: _description_
    :param delta: _description_, defaults to None
    :param algorithm: _description_, defaults to "HS256"
    :return: An encoded access token
    """
    if delta and delta > 0:
        exp = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
            seconds=delta
        )
        payload |= {"exp": exp}

    token = jwt.encode(payload, key, algorithm)
    return token


def jwt_decode(encoded, key: str, algorithm="HS256"):
    """decode jwt."""

    payload = jwt.decode(encoded, key, algorithm)
    return payload
