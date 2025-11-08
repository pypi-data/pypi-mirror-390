import pytest

from faker import Faker

fakers = Faker()

@pytest.fixture
def fake():
    return fakers