#!/usr/bin/env python3

# Copyright 2015 shiro <shiro@worldofcorecraft.com>
# This file is part of SSI.

# SSI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# SSI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with SSI.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import os
import subprocess
import sys

def main():
    tools = iterate_tools()
    if len(tools) == 0:
        sys.stderr.write('No tools found\n')
    elif len(tools) == 1:
        launch_tool(tools[0])
    else:
        tool = select_tool(tools)
        launch_tool(tool)
    pass

def iterate_tools():
    tools = []
    for name in os.listdir('tools'):
        if os.path.isdir(os.path.join('tools', name)):
            tools.append(name)
    return tools

def select_tool(tools):
    parser = argparse.ArgumentParser(description='Explore DBC data visually')
    parser.add_argument('--tool', '-t', help='Select tool to use')
    args = parser.parse_args()
    if not args.tool or args.tool not in tools:
        sys.stderr.write('Must select a tool\n')
        sys.exit(1)
    return args.tool

def launch_tool(tool):
    module = os.path.join(os.path.join('tools', tool), 'main.py')
    if not os.path.exists(module):
        sys.stderr.write('Tool has no main.py\n')
        sys.exit(1)
    path = os.path.abspath(module)
    subprocess.call(path, cwd=os.path.dirname(path), shell=True)

if __name__ == '__main__':
    main()
