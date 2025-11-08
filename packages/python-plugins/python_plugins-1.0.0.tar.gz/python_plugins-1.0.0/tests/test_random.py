from python_plugins.random.random_str import secret_token, secret_token_16


def test_random_secret_token():
    token_1 = secret_token()
    assert len(token_1) == 64
    token_2 = secret_token_16()
    assert len(token_2) == 32
