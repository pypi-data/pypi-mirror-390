import argparse
import asyncio
import sys
import tomli
from pathlib import Path
from loguru import logger
from . import get_urls, __version__, OutputManager
from gau.runner import Runner
from typing import List, Dict, Any

VERSION = "2.3.0"  # Python Port Version


def load_config(config_path: Path | None) -> Dict[str, Any]:
    """Loads configuration from a TOML file."""
    default_config_paths = [
        Path.home() / '.gau.toml',
        Path.cwd() / 'config.toml'
    ]

    if config_path:
        if not config_path.exists():
            logger.warning(f"Config file not found at {config_path}. Using defaults.")
            return {}
        paths_to_try = [config_path]
    else:
        paths_to_try = default_config_paths

    for path in paths_to_try:
        if path.exists():
            logger.info(f"Loading configuration from {path}")
            with open(path, 'rb') as f:
                return tomli.load(f)

    logger.info("No config file found. Using default settings.")
    return {}


def merge_configs(args: argparse.Namespace, file_config: Dict[str, Any], parser: argparse.ArgumentParser) -> Dict[str, Any]:
    """
    Merges command-line arguments and file configuration.
    CLI arguments take precedence.
    """
    # Start with defaults, then layer file config, then args
    config = {
        'threads': 10, 'timeout': 20, 'retries': 5, 'verbose': False,
        'subdomains': False, 'parameters': False, 'json': False,
        'providers': ["wayback", "commoncrawl", "otx", "urlscan"],
        'blacklist': ["ttf", "woff", "svg", "png", "jpg", "gif"],
        'filters': {}, 'urlscan': {}
    }

    config.update(file_config)

    # Override with command-line arguments if they are not the default value
    cli_args = vars(args)
    for key, value in cli_args.items():
        if key in config and value is not None:
            # Handle special cases for flags that are always present
            if isinstance(value, bool) and value:
                config[key] = value
            elif isinstance(value, (int, str)) and value != parser.get_default(key):
                config[key] = value
            elif isinstance(value, list) and value:
                config[key] = value
            elif isinstance(value, (int, str, float)) and value != parser.get_default(key):
                config[key] = value

    # Map specific flags to config dictionary
    config['output_file'] = args.o
    config['subdomains'] = args.subs
    config['parameters'] = args.fp

    # Handle filters
    config['filters'] = {
        'from': args.from_date, 'to': args.to_date,
        'matchstatuscodes': args.mc, 'filterstatuscodes': args.fc,
        'matchmimetypes': args.mt, 'filtermimetypes': args.ft,
    }

    return config


def setup_logging(verbose: bool):
    log_level = "DEBUG" if verbose else "INFO"
    logger.remove()
    logger.add(sys.stderr, level=log_level, format="<level>{level: <8}</level> | <level>{message}</level>")


def get_domains_from_stdin() -> List[str]:
    if not sys.stdin.isatty():
        return [line.strip() for line in sys.stdin]
    return []


async def run_from_cli(config: Dict[str, Any], domains: List[str]):
    """The async function that uses the library to run the scan from the CLI."""

    # 1. Get the async generator of URLs from the library function.
    urls_generator = get_urls(domains=domains, config=config)

    # 2. Use the OutputManager to handle writing the results.
    output_manager = OutputManager(config)
    await output_manager.write_results(urls_generator)


def main():
    """Main CLI entry point function."""
    parser = argparse.ArgumentParser(description="getallurls (gau) - Python Port")
    parser.add_argument('domains', nargs='*', help="Domain(s) to fetch URLs for")
    parser.add_argument('--version', action='version', version=f'gau-python {VERSION}')
    parser.add_argument('--config', type=Path, help="Path to config file")
    parser.add_argument('-o', type=Path, help="Filename to write results to")
    parser.add_argument('--threads', '-t', type=int, help="Number of workers (threads)")
    parser.add_argument('--timeout', type=int, help="Timeout for HTTP requests")
    parser.add_argument('--retries', type=int, help="Retries for HTTP requests")
    parser.add_argument('--verbose', '-v', action='store_true', help="Enable verbose output")
    parser.add_argument('--subs', action='store_true', help="Include subdomains of target domain")
    parser.add_argument('--fp', action='store_true', help="Remove different parameters of the same endpoint")
    parser.add_argument('--json', action='store_true', help="Output as JSON")
    parser.add_argument('--blacklist', type=lambda s: s.split(','), help="Comma-separated list of extensions to skip")
    parser.add_argument('--providers', type=lambda s: s.split(','), help="Comma-separated list of providers to use")

    # Filter flags
    parser.add_argument('--mc', type=lambda s: s.split(','), default=[], help="Match status codes")
    parser.add_argument('--fc', type=lambda s: s.split(','), default=[], help="Filter status codes")
    parser.add_argument('--mt', type=lambda s: s.split(','), default=[], help="Match mime-types")
    parser.add_argument('--ft', type=lambda s: s.split(','), default=[], help="Filter mime-types")
    parser.add_argument('--from', dest='from_date', help="Fetch URLs from date (YYYYMM)")
    parser.add_argument('--to', dest='to_date', help="Fetch URLs to date (YYYYMM)")

    args = parser.parse_args()

    # Load and merge configurations
    file_config = load_config(args.config)
    config = merge_configs(args, file_config, parser)

    # Setup logging
    setup_logging(config['verbose'])

    # Get domains
    domains = args.domains + get_domains_from_stdin()
    if not domains:
        parser.error("No domains specified. Provide domains as arguments or via stdin.")

    unique_domains = sorted(list(set(domains)))
    logger.info(f"Starting scan for {len(unique_domains)} domain(s) with {config['threads']} workers.")

    try:
        asyncio.run(run_from_cli(config, unique_domains))
    except KeyboardInterrupt:
        logger.info("Scan interrupted by user. Exiting.")

if __name__ == "__main__":
    main()