# WARNING: BUILD PROCESS WON'T WORK ON WINDOWS

# Variables
SCRIPT_NAME = flatten_pdf.py
BINARY_NAME = flatten_pdf
INSTALL_PATH = /usr/local/bin

# Default target
all: build

# Build target
build:
	pip install -r requirements.txt
	pyinstaller --onefile $(SCRIPT_NAME)

# Install target (copy the binary to the system path)
install:
	sudo cp dist/$(BINARY_NAME) $(INSTALL_PATH)

# Clean up build files
clean:
	rm -rf build dist __pycache__ $(BINARY_NAME).spec

# Full build and install process
reinstall: clean build install

# Run tests
test:
	pytest tests/