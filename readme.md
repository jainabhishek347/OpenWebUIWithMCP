# Project Setup

## Prerequisites
- Python 3.8+
- [uv](https://pypi.org/project/uv/) installed

Install `uv`:
```bash
pip install uv
```

Run the following command to start the server:
```bash
uvx mcpo --port 8002 -- uv run main.py
```
## Steps to Connect to Open Web UI

1. **Open Settings**
   - Navigate to `Settings → Connection`.

2. **Add URL and API Key**
   - URL: `"https://generativelanguage.googleapis.com/v1beta/openai"`
   - Gemini API Key: `"Add your GEMINI API Key"`

3. **Configure Tools**
   - Go to the `Tools` section.
   - Add the **Server URL** with proxy: `http://0.0.0.0:8002`