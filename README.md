# EasyBrowser Examples

Two minimal test examples for EasyBrowser:

- `cloudflare_turnstile.py`
- `recaptcha_v3_score_detector.py`

## Install

Install the SDK from PyPI:

```bash
pip install easybrowser-sdk
patchright install chromium
```

Install the example dependencies:

```bash
pip install -r requirements.txt
```

For local SDK development, install the sibling package in editable mode:

```bash
pip install -e ..\sdk
```

EasyLauncher must be installed and running. Download it from:

https://easybrowser.pages.dev/

## Run

```bash
python cloudflare_turnstile.py
python recaptcha_v3_score_detector.py
```

The scripts use fixed test URLs and do not require command-line arguments.
