# -*- coding: utf-8 -*-
#
# Copyright 2025 NXP
#
# SPDX-License-Identifier: MIT

"""
External sample MCP describe how to retrieve U-Boot configuration references for board predeploy operations.
"""


from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from fc_common.config import Config
from fc_mcp.mcp_base import MCPPlugin


class Plugin(MCPPlugin):
    def __init__(self, mcp):
        super().__init__(mcp)
        user_config = Config.load_user_config()
        self.predeploy_knowledge_url = user_config.get("PREDEPLOY_KNOWLEDGE_URL", "")

    def register_tools(self):
        @self.mcp.tool()
        def get_uboot_config(
            resource_id: str, build: str = "Linux_Factory", build_number: str = "668"
        ) -> Dict[str, Any]:
            """
            Get U-Boot configuration reference for board predeploy operations.
            Fetches the appropriate U-Boot environment configuration from the TFTP server
            and provides formatted usage instructions.

            Args:
                resource_id: Resource identifier (e.g., 'imx95-19x19-evk-sh62')
                build: Build type (default: 'Linux_Factory')
                build_number: Build number (default: '668')

            Returns:
                Dictionary with U-Boot configuration and usage instructions
            """

            try:
                # Fetch available config files
                board_name = (
                    resource_id.rsplit("-", 1)[0] if "-" in resource_id else resource_id
                )
                available_files = self._fetch_directory_listing()

                if not available_files:
                    return {
                        "board_name": board_name,
                        "operation": "get_uboot_config",
                        "success": False,
                        "error": "No U-Boot configuration files found on the server",
                        "server_url": self.predeploy_knowledge_url,
                    }

                # Find the appropriate config file for the board
                config_file = self._find_board_config_file(board_name, available_files)

                if not config_file:
                    available_boards = [
                        f.replace("_uboot_env_daily.txt", "") for f in available_files
                    ]
                    return {
                        "board_name": board_name,
                        "operation": "get_uboot_config",
                        "success": False,
                        "error": f"No configuration found for board '{board_name}'",
                        "available_boards": sorted(available_boards),
                        "suggestion": "Check the board name against the available boards list",
                    }

                # Fetch the config file content
                config_content = self._fetch_uboot_config(config_file)

                # Format the configuration
                formatted_config = self._format_uboot_config(
                    board_name, build, build_number, config_content
                )

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                return {
                    "board_name": board_name,
                    "operation": "get_uboot_config",
                    "success": True,
                    "config_file_used": config_file,
                    "server_url": self.predeploy_knowledge_url + config_file,
                    "retrieved_at": current_time,
                    "build_info": {
                        "build": build,
                        "build_number": build_number,
                        "board": board_name,
                    },
                    "uboot_config": formatted_config,
                    "usage_instructions": [
                        "1. Boot the board and interrupt U-Boot to get to the U-Boot prompt",
                        "2. Copy and paste the U-Boot commands below one by one",
                        "3. Use 'saveenv' command to save the environment to persistent storage",
                        "4. Use 'reset' or 'boot' command to continue with the new configuration",
                    ],
                    "important_notes": [
                        f"• Ensure build {build} #{build_number} artifacts are available",
                        "• Make sure network connectivity is properly configured",
                        "• Backup current U-Boot environment before applying changes",
                        "• Verify all paths and URLs are accessible from the target board",
                    ],
                    "troubleshooting": {
                        "if_commands_fail": "Check network connectivity and server accessibility",
                        "if_files_not_found": f"Verify build {build} #{build_number} is available on the server",
                        "if_boot_fails": "Check U-Boot environment variables and file paths",
                        "if_network_issues": "Verify IP configuration and TFTP server accessibility",
                    },
                }

            except Exception as exce:
                return {
                    "board_name": board_name,
                    "operation": "get_uboot_config",
                    "success": False,
                    "error": f"Failed to get U-Boot configuration: {str(exce)}",
                    "fallback_manual_steps": [
                        f"1. Open browser and go to {self.predeploy_knowledge_url}",
                        f"2. Look for file containing '{board_name}' in the name",
                        "3. Download the appropriate *_uboot_env_daily.txt file",
                        f"4. Replace placeholders with build={build}, build_number={build_number}",
                        "5. Apply the configuration manually in U-Boot prompt",
                    ],
                }

        @self.mcp.tool()
        def list_available_boards() -> Dict[str, Any]:
            """
            List all available boards that have U-Boot configurations.
            Fetches the directory listing from TFTP server and extracts board names.

            Returns:
                Dictionary with list of available boards and their config files
            """

            try:
                available_files = self._fetch_directory_listing()

                if not available_files:
                    return {
                        "operation": "list_available_boards",
                        "success": False,
                        "error": "No U-Boot configuration files found on the server",
                        "server_url": self.predeploy_knowledge_url,
                    }

                boards = []
                for filename in available_files:
                    if filename not in ["template_uboot_env_daily.txt", "template.txt"]:
                        board_name = filename.replace("_uboot_env_daily.txt", "")
                        boards.append(
                            {"board_name": board_name, "config_file": filename}
                        )

                boards.sort(key=lambda x: x["board_name"])

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                return {
                    "operation": "list_available_boards",
                    "success": True,
                    "server_url": self.predeploy_knowledge_url,
                    "retrieved_at": current_time,
                    "total_boards": len(boards),
                    "available_boards": boards,
                    "board_names_only": [board["board_name"] for board in boards],
                    "usage_tip": "Use any of these board names with get_uboot_config() function",
                }

            except Exception as exce:
                return {
                    "operation": "list_available_boards",
                    "success": False,
                    "error": f"Failed to list available boards: {str(exce)}",
                    "fallback_manual_steps": [
                        f"1. Open browser and go to {self.predeploy_knowledge_url}",
                        "2. Look for files ending with '_uboot_env_daily.txt'",
                        "3. Extract board names from filenames (remove '_uboot_env_daily.txt' suffix)",
                    ],
                }

    def _fetch_directory_listing(self) -> List[str]:
        """Fetch and parse the directory listing from TFTP server"""
        response = requests.get(self.predeploy_knowledge_url, timeout=30)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch directory listing: HTTP {response.status_code}"
            )

        soup = BeautifulSoup(response.text, "html.parser")

        files = []
        for link in soup.find_all("a"):  # pylint: disable=not-an-iterable
            href = link.get("href")
            if href and href.endswith("_uboot_env_daily.txt"):
                files.append(href)

        return files

    def _fetch_uboot_config(self, filename: str) -> str:
        """Fetch the content of a specific U-Boot config file"""
        file_url = f"{self.predeploy_knowledge_url}{filename}"
        response = requests.get(file_url, timeout=30)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch file {filename}: HTTP {response.status_code}"
            )

        return response.text

    def _find_board_config_file(
        self, board_name: str, available_files: List[str]
    ) -> Optional[str]:
        """Find the appropriate config file for the given board name"""
        # Normalize board name
        normalized_board = board_name.lower().replace("-", "").replace("_", "")

        # Try exact match first
        for filename in available_files:
            file_board = (
                filename.replace("_uboot_env_daily.txt", "")
                .replace("-", "")
                .replace("_", "")
            )
            if normalized_board == file_board.lower():
                return filename

        # Try partial match
        for filename in available_files:
            file_board = filename.replace("_uboot_env_daily.txt", "")
            if normalized_board in file_board.lower().replace("-", "").replace("_", ""):
                return filename

        return None

    def _format_uboot_config(
        self, board_name: str, build: str, build_number: str, config_content: str
    ) -> str:
        """Format the U-Boot configuration with variable substitution"""

        # Replace placeholders in config content
        formatted_content = config_content.replace("${BUILD}", build)
        formatted_content = formatted_content.replace("${BUILD_NUMBER}", build_number)
        formatted_content = formatted_content.replace("${BOARD}", board_name)

        return formatted_content.strip()
