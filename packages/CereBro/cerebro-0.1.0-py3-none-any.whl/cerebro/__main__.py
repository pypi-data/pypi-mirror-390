"""Main entry point for the application."""

import argparse
from cerebro.app import CereBroApp


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CereBro - TUI for Ollama LLMs"
    )
    parser.add_argument(
        "-u",
        "--ollama-url",
        default="http://localhost:11434",
        help="URL of your Ollama instance",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    
    args = parser.parse_args()
    
    app = CereBroApp(ollama_url=args.ollama_url)
    app.run()


if __name__ == "__main__":
    main()