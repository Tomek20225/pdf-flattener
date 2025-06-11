# PDF Flattener

A command-line tool that converts PDF files into image-based documents, effectively making them resemble scanned documents. This process removes any interactive elements, forms, or embedded content while preserving the visual appearance. Ideal for creating consistent, non-editable versions of documents or preparing them for archiving.

## Features

- Converts PDFs to image-based documents, simulating scanned documents
- Preserves original metadata, including MacOS timestamps
- Allows for setting of custom creation and modification dates
- Configurable DPI settings for quality control
- Cross-platform support (Windows, macOS, Linux)

## Prerequisites

### System Dependencies

- **Poppler**: Required for PDF processing
  - macOS: `brew install poppler`
  - Linux: `sudo apt-get install poppler-utils`
  - Windows: Download and install from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases/)

### Python Dependencies

- Python 3.10 or higher
- Required Python packages (automatically installed via pip):
  - PyMuPDF (fitz)
  - pdf2image

## Installation

### From Source

1. Clone the repository:

   ```bash
   git clone https://github.com/Tomek20225/pdf-flattener.git
   cd pdf-flattener
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Build the executable:

   ```bash
   make build
   ```

4. (Optional) Install globally:
   ```bash
   sudo make install
   ```

### Using Pre-built Binaries

Download the latest release from the [Releases page](https://github.com/Tomek20225/pdf-flattener/releases) for your operating system.

## Usage

Basic usage:

```bash
flatten_pdf input.pdf
```

Advanced usage with options:

```bash
flatten_pdf input.pdf --output output.pdf --dpi 300 --creation-date 2024-01-01 --modification-date 2024-01-02
```

### Command-line Arguments

- `input_pdf`: Path to the input PDF file (required)
- `--output`, `-o`: Output PDF file name (default: "flat-{input_filename}")
- `--dpi`, `-d`: DPI for image extraction (default: 200)
- `--creation-date`, `-c`: Creation date in YYYY-MM-DD format
- `--modification-date`, `-m`: Modification date in YYYY-MM-DD format

## Building from Source

### Using Make

```bash
# Build the executable
make build

# Install globally
make install

# Clean build files
make clean

# Full rebuild and install
make reinstall
```

### Manual Build

```bash
pip install -r requirements.txt
pyinstaller --onefile flatten_pdf.py
```

## Testing

The project includes a comprehensive test suite using pytest. To run the tests:

1. Install test dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the tests:
   ```bash
   pytest tests/
   ```

Tests use temporary files and directories that are automatically cleaned up after each test run.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project uses the following open-source libraries:

- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - PDF manipulation
- [pdf2image](https://github.com/Belval/pdf2image) - PDF to image conversion
- [Poppler](https://poppler.freedesktop.org/) - PDF processing utilities

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/yourusername/pdf-flattener/issues) on GitHub.
