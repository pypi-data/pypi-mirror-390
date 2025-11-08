# gau-python (Get All URLs - Python)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)

An asynchronous Python port of the original `gau` (GetAllUrls) by `lc`. This tool fetches known URLs from AlienVault's Open Threat Exchange (OTX), the Wayback Machine, Common Crawl, and URLScan for any given domain.

This version is designed to be used both as a powerful command-line tool and as a flexible library in other Python projects.

## Features

-   **Fast and Asynchronous:** Built with `asyncio` and `httpx` to fetch from all providers concurrently.
-   **Multiple Providers:** Gathers data from Wayback Machine, OTX, Common Crawl, and URLScan.io.
-   **CLI and Library:** Use it directly from your terminal or `import get_urls` in your own scripts.
-   **Rich Filtering:** Filter results by date, status code, MIME type, and file extension blacklists.
-   **Resilient:** Includes automatic retries with exponential backoff to handle network errors and API rate limits.
-   **Installable Package:** A proper Python package that can be installed with `pip`.

## Installation

### From PyPI (Recommended)

```bash
pip install gau-python
```

### From Source

```bash
git clone https://github.com/H3xano/gau-python.git
cd gau-python
pip install -e .
```

## Usage (Command-Line)

`gau` can accept domains from command-line arguments or from `stdin`.

### Examples

```bash
# Scan a single domain
gau example.com

# Scan multiple domains
gau example.com google.com

# Pipe domains from another tool
echo "example.com" | gau

# Include subdomains and use more threads
gau example.com --subs --threads 10

# Save output to a file
gau example.com -o example_urls.txt

# Output as JSON
gau example.com --json
```

### Command-Line Flags

| Flag            | Description                                                 | Example                                  |
| --------------- | ----------------------------------------------------------- | ---------------------------------------- |
| `domains`       | One or more domains to scan (or read from stdin)            | `gau example.com`                        |
| `-o`            | Filename to write results to                                | `gau -o out.txt example.com`             |
| `--threads`, `-t` | Number of concurrent workers to spawn                     | `gau --threads 20 example.com`           |
| `--timeout`     | Timeout (in seconds) for HTTP requests                      | `gau --timeout 30 example.com`           |
| `--retries`     | Number of retries for failed HTTP requests                  | `gau --retries 10 example.com`           |
| `--subs`        | Include subdomains of the target domain                     | `gau --subs example.com`                 |
| `--fp`          | Filter out duplicate URLs with different parameters         | `gau --fp example.com`                   |
| `--blacklist`   | Comma-separated list of extensions to skip                  | `gau --blacklist png,jpg,gif example.com`|
| `--providers`   | Comma-separated list of providers to use                    | `gau --providers wayback,otx example.com`|
| `--json`        | Output results in JSON format                               | `gau --json example.com`                 |
| `--mc`          | Match status codes (e.g., show only 200, 302)               | `gau --mc 200,302 example.com`           |
| `--fc`          | Filter status codes (e.g., hide 404, 403)                   | `gau --fc 404,403 example.com`           |
| `--mt`          | Match MIME types (e.g., show only application/json)         | `gau --mt application/json example.com`  |
| `--ft`          | Filter MIME types (e.g., hide text/css)                     | `gau --ft text/css example.com`          |
| `--from`        | Fetch URLs from a specific start date (YYYYMM)              | `gau --from 202201 example.com`          |
| `--to`          | Fetch URLs up to a specific end date (YYYYMM)               | `gau --to 202301 example.com`            |
| `--verbose`, `-v` | Show verbose logging output                                 | `gau -v example.com`                     |
| `--version`     | Display the tool's version                                  | `gau --version`                          |

## Usage (as a Library)

The primary strength of this Python port is its usability as a library. You can import the `get_urls` async generator to integrate `gau`'s functionality into your own tools.

```python
import asyncio
from gau import get_urls

async def main():
    target_domains = ["example.com"]

    # Define a custom configuration for the scan
    scan_config = {
        'subdomains': True,
        'threads': 20,
        'providers': ["wayback", "otx"],
        'filters': {
            'matchmimetypes': ['application/json']
        }
    }

    print("[*] Searching for API endpoints...")
    async for url in get_urls(domains=target_domains, config=scan_config):
        print(f"[+] Found endpoint: {url}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration File

The tool can be configured via a TOML file. It will look for `config.toml` in the current directory or `~/.gau.toml`. Any command-line flags will override settings from the config file.

**Example `config.toml`:**
```toml
threads = 15
retries = 10
subdomains = true
provider_delay = 0.5 # Wait 0.5s between starting each provider

# Your urlscan.io API key for better results
[urlscan]
apikey = "YOUR_API_KEY_HERE"

# Default filters to apply on every run
[filters]
filterstatuscodes = ["404", "403"]
filtermimetypes = ["image/png", "image/jpeg", "text/css"]
```

## Credits

This project is a Python port of the original Go-based [gau](https://github.com/lc/gau) by [lc](https://github.com/lc). A huge thank you to him for the original tool and inspiration.
