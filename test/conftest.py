import pytest


def pytest_addoption(parser):
    parser.addoption("--key", action="store")
    parser.addoption("--secret", action="store")
    parser.addoption("--token", action="store")
    parser.addoption("--token-secret", action="store")


@pytest.fixture
def key(request):
    return request.config.getoption("--key")

@pytest.fixture
def secret(request):
    return request.config.getoption("--secret")

@pytest.fixture
def token(request):
    return request.config.getoption("--token")

@pytest.fixture
def token_secret(request):
    return request.config.getoption("--token-secret")


