# URLScanner

Security Header Audit — one route (`/audit`) with **GET + POST** and a tiny CLI.
This API runs locally on http://127.0.0.1:8000

**POST**
This endpoints accepts a url as input and then scanns the headsers of the url

**GET**
This endpoint shows a list of the 10 most recent scans

## Install
```bash
pip install "threatboard[api,cli]"
threatapi
threatctl post https://example.com
threatctl get
