#!/usr/bin/env python3
"""
Multi-server deployment for deep research MCP servers.
Creates separate MCP server instances for each index to comply with OpenAI's deep research specification.
"""

import argparse
import logging
import signal
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

from .deep_research_mcp import DeepResearchMCP
from .mcp import load_config_from_yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiDeepResearchMCP:
    """Manager for multiple deep research MCP servers."""

    def __init__(
        self, config_paths: List[str], base_port: int = 8000, base_url: str = ""
    ):
        self.config_paths = config_paths
        self.base_port = base_port
        self.base_url = base_url.rstrip("/")
        self.servers: List[DeepResearchMCP] = []
        self.server_info: List[Dict[str, Any]] = []
        self.processes: List[subprocess.Popen] = []

        # Load all configurations
        self._load_configurations()

    def _load_configurations(self) -> None:
        """Load all YAML configurations and create server info."""
        current_port = self.base_port

        for config_path in self.config_paths:
            try:
                server_name, server_description, index_configs, server_config = (
                    load_config_from_yaml(config_path)
                )

                # Create separate server info for each index
                for i, index_config in enumerate(index_configs):
                    # Use configured port or increment from base
                    port = server_config.get("port", current_port)
                    host = server_config.get("host", "0.0.0.0")

                    server_info = {
                        "name": index_config.name,
                        "description": index_config.description,
                        "config": index_config,
                        "host": host,
                        "port": port,
                        "config_path": config_path,
                        "url": f"http://{host}:{port}/mcp",
                        "server_name": server_name,
                        "server_description": server_description,
                    }

                    self.server_info.append(server_info)
                    current_port += 1

            except Exception as e:
                logger.error(f"Error loading config {config_path}: {e}")
                raise

    def create_servers(self) -> None:
        """Create DeepResearchMCP instances for each index."""
        for info in self.server_info:
            try:
                server = DeepResearchMCP(info["config"], base_url=self.base_url)
                self.servers.append(server)
                logger.info(
                    f"Created server for index '{info['name']}' on port {info['port']}"
                )
            except Exception as e:
                logger.error(f"Error creating server for {info['name']}: {e}")
                raise

    def run_servers_subprocess(self) -> None:
        """Run each server in a separate subprocess."""
        logger.info(f"Starting {len(self.server_info)} deep research MCP servers...")

        def signal_handler(signum, frame):
            logger.info("Received shutdown signal, stopping all servers...")
            self.stop_servers()
            sys.exit(0)

        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            # Start each server in a separate process
            for i, info in enumerate(self.server_info):
                cmd = [
                    sys.executable,
                    "-m",
                    "src.full_text_search.mcp.deep_research_mcp",
                    "--name",
                    info["name"],
                    "--description",
                    info["description"],
                    "--data-file",
                    info["config"].data_file,
                    "--id-column",
                    info["config"].id_column,
                    "--text-column",
                    info["config"].text_column,
                    "--searchable-columns",
                    *info["config"].searchable_columns,
                    "--host",
                    info["host"],
                    "--port",
                    str(info["port"]),
                ]

                if info["config"].index_path:
                    cmd.extend(["--index-path", info["config"].index_path])

                if self.base_url:
                    cmd.extend(["--base-url", self.base_url])

                logger.info(
                    f"Starting server {i + 1}/{len(self.server_info)}: {info['name']} on {info['host']}:{info['port']}"
                )

                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                self.processes.append(process)

                # Give each server time to start
                time.sleep(2)

            # Print server information
            self.print_server_info()

            # Wait for all processes
            logger.info("All servers started. Press Ctrl+C to stop all servers.")

            # Monitor processes
            while True:
                time.sleep(5)

                # Check if any process died
                for i, process in enumerate(self.processes):
                    if process.poll() is not None:
                        logger.error(
                            f"Server {self.server_info[i]['name']} (PID {process.pid}) exited with code {process.returncode}"
                        )

                        # Get stderr output
                        stderr_output = process.stderr.read() if process.stderr else ""
                        if stderr_output:
                            logger.error(
                                f"Server {self.server_info[i]['name']} stderr: {stderr_output}"
                            )

                        # Restart the server
                        logger.info(
                            f"Restarting server {self.server_info[i]['name']}..."
                        )
                        self.processes[i] = subprocess.Popen(
                            cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                        )

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, stopping all servers...")
            self.stop_servers()
        except Exception as e:
            logger.error(f"Error running servers: {e}")
            self.stop_servers()
            raise

    def run_servers_threaded(self) -> None:
        """Run each server in a separate thread (alternative to subprocess)."""
        logger.info(
            f"Starting {len(self.server_info)} deep research MCP servers in threads..."
        )

        self.create_servers()

        def run_server(server, info):
            try:
                server.run_server(host=info["host"], port=info["port"])
            except Exception as e:
                logger.error(f"Error running server {info['name']}: {e}")

        # Start servers in threads
        with ThreadPoolExecutor(max_workers=len(self.servers)) as executor:
            futures = []
            for server, info in zip(self.servers, self.server_info):
                future = executor.submit(run_server, server, info)
                futures.append(future)

            # Print server information
            self.print_server_info()

            logger.info("All servers started. Press Ctrl+C to stop all servers.")

            try:
                # Wait for all futures to complete
                for future in futures:
                    future.result()
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received, stopping all servers...")
                # The executor will clean up threads on exit

    def stop_servers(self) -> None:
        """Stop all running servers."""
        for process in self.processes:
            if process.poll() is None:
                logger.info(f"Stopping server PID {process.pid}")
                process.terminate()

                # Wait a bit for graceful shutdown
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Force killing server PID {process.pid}")
                    process.kill()

    def print_server_info(self) -> None:
        """Print information about all running servers."""
        logger.info("\n" + "=" * 80)
        logger.info("DEEP RESEARCH MCP SERVERS RUNNING")
        logger.info("=" * 80)

        for info in self.server_info:
            logger.info(f"Index: {info['name']}")
            logger.info(f"  Description: {info['description']}")
            logger.info(f"  URL: {info['url']}")
            logger.info(f"  Data file: {info['config'].data_file}")
            logger.info(
                f"  Searchable columns: {', '.join(info['config'].searchable_columns)}"
            )
            logger.info("")

        logger.info(
            "Each server provides 'search' and 'fetch' tools compatible with OpenAI Deep Research."
        )
        logger.info(
            "Use these URLs to configure MCP connections in ChatGPT or via API."
        )
        logger.info("=" * 80)

    def generate_config_examples(self) -> None:
        """Generate example configurations for connecting to these servers."""
        logger.info("\n" + "=" * 80)
        logger.info("EXAMPLE CONFIGURATIONS")
        logger.info("=" * 80)

        logger.info("\nFor OpenAI API (Responses endpoint):")
        logger.info("```json")
        logger.info('"tools": [')

        for i, info in enumerate(self.server_info):
            comma = "," if i < len(self.server_info) - 1 else ""
            logger.info("  {")
            logger.info('    "type": "mcp",')
            logger.info(f'    "server_label": "{info["name"]}",')
            logger.info(f'    "server_url": "{info["url"]}",')
            logger.info('    "allowed_tools": ["search", "fetch"],')
            logger.info('    "require_approval": "never"')
            logger.info(f"  }}{comma}")

        logger.info("]")
        logger.info("```")

        logger.info("\nFor ChatGPT Connectors:")
        for info in self.server_info:
            logger.info(f"- Index: {info['name']}")
            logger.info(f"  URL: {info['url']}")
            logger.info(f"  Description: {info['description']}")

        logger.info("=" * 80)


def main():
    """CLI entry point for running multiple deep research MCP servers."""
    parser = argparse.ArgumentParser(
        description="Multi-server deep research MCP deployment"
    )

    parser.add_argument(
        "--config",
        action="append",
        required=True,
        help="YAML configuration file (can be specified multiple times)",
    )
    parser.add_argument(
        "--base-port",
        type=int,
        default=8000,
        help="Base port number (servers will use sequential ports starting from this)",
    )
    parser.add_argument(
        "--base-url", default="", help="Base URL for document URLs (optional)"
    )
    parser.add_argument(
        "--mode",
        choices=["subprocess", "threaded"],
        default="subprocess",
        help="Server execution mode (subprocess is more robust)",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show example configurations and exit",
    )

    args = parser.parse_args()

    try:
        # Create multi-server manager
        multi_server = MultiDeepResearchMCP(
            config_paths=args.config, base_port=args.base_port, base_url=args.base_url
        )

        if args.show_config:
            multi_server.generate_config_examples()
            return 0

        # Run servers
        if args.mode == "subprocess":
            multi_server.run_servers_subprocess()
        else:
            multi_server.run_servers_threaded()

    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
