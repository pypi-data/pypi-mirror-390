# Leap Extraction Tool (LeapX)

Leap Extraction Tool is a lightweight service designed to extract structured data from documents such as PDFs, images, and text files. It leverages AI-powered parsing and OCR capabilities to identify key information with high accuracy and speed.

### Features

* Automated text and data extraction
* Support for multiple file formats
* Fast and scalable API-based workflow

### Usage

Upload your document, JsonSchema, trigger extraction, and retrieve structured JSON output instantly.


```bash
pip install leapx
```
### Additional Information

For more details on the extraction process and supported file formats, please refer to the documentation.

For activating the uv pre-commit
```bash
uv run pre-commit install
```

### Setup Pre-commit Hooks

After cloning the repo, run the following command to set up all pre-commit hooks:

```bash
uv run bash scripts/setup-hooks.sh

```

---
