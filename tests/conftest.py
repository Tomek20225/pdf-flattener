import pytest
import os
import shutil
import tempfile

@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Clean up any temporary files after each test."""
    yield
    temp_dir = tempfile.gettempdir()
    for file in os.listdir(temp_dir):
        if file.startswith("tmp") and file.endswith(".pdf"):
            try:
                os.remove(os.path.join(temp_dir, file))
            except OSError:
                pass 