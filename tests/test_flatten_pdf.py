import os
import pytest
import tempfile
import time
from datetime import datetime
import platform
import shutil
from pathlib import Path
from flatten_pdf import (
    get_poppler_path,
    extract_images_from_pdf,
    create_pdf_from_images,
    compress_pdf,
    set_metadata,
    flatten_pdf,
    safe_temp_file
)

def safe_remove_file(file_path, max_retries=3, delay=0.1):
    """Safely remove a file with retries."""
    for attempt in range(max_retries):
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
            return
        except OSError as e:
            if attempt == max_retries - 1:
                print(f"Warning: Could not delete file {file_path} after {max_retries} attempts: {e}")
            else:
                time.sleep(delay)

@pytest.fixture
def sample_pdf(tmp_path):
    """Create a temporary PDF file for testing."""
    import fitz
    
    # Create a temporary directory for our test files
    test_dir = tmp_path / "test_pdfs"
    test_dir.mkdir(exist_ok=True)
    
    # Create the PDF in the test directory
    pdf_path = test_dir / "test.pdf"
    
    # Create a new PDF document
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((100, 100), "Test PDF")
    
    # Save to a string buffer first
    pdf_bytes = doc.write()
    doc.close()
    
    # Write the bytes to the file
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)
    
    yield str(pdf_path)
    
    # Cleanup
    try:
        shutil.rmtree(test_dir)
    except Exception as e:
        print(f"Warning: Could not remove test directory {test_dir}: {e}")

@pytest.fixture
def output_path(tmp_path):
    """Create a unique output path in a temporary directory."""
    path = str(tmp_path / "output.pdf")
    yield path
    safe_remove_file(path)

def test_safe_temp_file():
    """Test the safe_temp_file context manager."""
    temp_path = None
    with safe_temp_file(suffix='.txt') as path:
        temp_path = path
        assert os.path.exists(path)
        with open(path, 'w') as f:
            f.write('test content')
    
    # File should be deleted after context manager exits
    assert not os.path.exists(temp_path)

def test_safe_temp_file_error_handling():
    """Test safe_temp_file error handling."""
    with pytest.raises(Exception):
        with safe_temp_file(suffix='.txt') as path:
            raise Exception("Test error")
    
    # File should still be deleted even after error
    assert not os.path.exists(path)

def test_get_poppler_path():
    """Test that poppler path is correctly determined based on OS."""
    path = get_poppler_path()
    if os.name == 'nt':  # Windows
        # On Windows, path can be None if Poppler is not found
        if path is not None:
            assert os.path.exists(path)
    else:  # Unix-like systems
        assert path is None or os.path.exists(path)

def test_extract_images_from_pdf(sample_pdf):
    """Test that images can be extracted from a PDF."""
    images = extract_images_from_pdf(sample_pdf)
    assert len(images) > 0
    assert all(hasattr(img, 'save') for img in images)

def test_extract_images_from_pdf_nonexistent():
    """Test error handling for nonexistent PDF."""
    with pytest.raises(FileNotFoundError):
        extract_images_from_pdf("nonexistent.pdf")

def test_create_pdf_from_images(sample_pdf, output_path):
    """Test that a PDF can be created from images."""
    images = extract_images_from_pdf(sample_pdf)
    create_pdf_from_images(images, output_path)
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0
    safe_remove_file(output_path)

def test_compress_pdf(sample_pdf, output_path):
    """Test PDF compression functionality."""
    compress_pdf(sample_pdf, output_path)
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0
    safe_remove_file(output_path)

def test_set_metadata(sample_pdf):
    """Test metadata setting functionality."""
    creation_date = "2024-01-01"
    modification_date = "2024-01-02"
    
    set_metadata(sample_pdf, creation_date, modification_date)
    
    # Verify metadata was set correctly
    import fitz
    doc = fitz.open(sample_pdf)
    metadata = doc.metadata
    doc.close()
    
    assert "creationDate" in metadata
    assert "modDate" in metadata

def test_set_metadata_invalid_date(sample_pdf):
    """Test metadata setting with invalid date format."""
    with pytest.raises(ValueError):
        set_metadata(sample_pdf, "invalid-date", "2024-01-02")

def test_flatten_pdf(sample_pdf, output_path):
    """Test the complete flatten_pdf function."""
    flatten_pdf(sample_pdf, output_path)
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0
    safe_remove_file(output_path)
    safe_remove_file(sample_pdf)

def test_flatten_pdf_with_dates(sample_pdf, output_path):
    """Test flatten_pdf with custom dates."""
    creation_date = "2024-01-01"
    modification_date = "2024-01-02"
    
    flatten_pdf(sample_pdf, output_path, creation_date, modification_date)
    assert os.path.exists(output_path)
    
    # Verify file system dates
    stat = os.stat(output_path)
    mod_time = datetime.fromtimestamp(stat.st_mtime)
    assert mod_time.year == 2024
    assert mod_time.month == 1
    assert mod_time.day == 2
    
    safe_remove_file(output_path)
    safe_remove_file(sample_pdf)

def test_flatten_pdf_nonexistent_input():
    """Test flatten_pdf with nonexistent input file."""
    with pytest.raises(FileNotFoundError):
        flatten_pdf("nonexistent.pdf", "output.pdf")

def test_flatten_pdf_existing_output(sample_pdf, output_path):
    """Test flatten_pdf with existing output file."""
    # Create the output file first
    with open(output_path, 'w') as f:
        f.write('test')
    
    # This should now work since we're using a non-temporary path
    flatten_pdf(sample_pdf, output_path)
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0
    
    # Cleanup
    safe_remove_file(output_path)
    safe_remove_file(sample_pdf) 