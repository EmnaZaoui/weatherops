import pytest
import asyncio

pytest_plugins = ['pytest_asyncio']

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )