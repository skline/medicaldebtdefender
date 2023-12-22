echo "Starting deployment script"

apt-get update && apt-get install -y tesseract-ocr && tesseract --version

echo "Finished deployment script"
