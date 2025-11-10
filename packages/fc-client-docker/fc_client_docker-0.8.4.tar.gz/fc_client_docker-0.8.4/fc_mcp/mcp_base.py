# -*- coding: utf-8 -*-
#
# Copyright 2025 NXP
#
# SPDX-License-Identifier: MIT


from importlib.metadata import entry_points


class MCPPlugin:
    def __init__(self, mcp):
        self.mcp = mcp
        self.register_tools()

    def register_tools(self):
        pass

    @staticmethod
    def load_plugins(mcp):
        for entry_point in entry_points(group="fc.mcp.plugins"):
            plugin_class = entry_point.load()
            plugin_class(mcp)
