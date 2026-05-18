import pytest
import asyncio
import os

os.environ["DB_PATH"] = "/tmp/test_weatherops.db"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
