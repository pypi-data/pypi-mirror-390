#
# Copyright (c) 2021 Dilili Labs, Inc.  All rights reserved. Contains Dilili Labs Proprietary Information. RESTRICTED COMPUTER SOFTWARE.  LIMITED RIGHTS DATA.
#
"""
Enhanced URL List Parser for BrainFrame

This module provides an improved URL list parser with the following features:
1. Ignores lines starting with '<' (after whitespace)
2. Only processes lines containing 'rtsp://'
3. Extracts the first value starting with 'rtsp://' from comma-separated values
4. Optionally extracts stream name from the field after the RTSP URL
5. Replaces 'localhost' with actual IP address

CSV Format:
- rtsp://url              -> Uses URL as name
- rtsp://url,name         -> Uses 'name' as stream name
- rtsp://url,             -> Uses URL as name (empty field)

This is a drop-in replacement for the original urls.py with backward compatibility.
"""

import os
if __name__ == "__main__":
    os.environ['BF_LOG_PRINT'] = 'TRUE'

import socket
import sys
from argparse import ArgumentParser
from collections import namedtuple
from pathlib import Path
import csv
import json
import ast

# Named tuple to hold stream URL and optional name
StreamInfo = namedtuple('StreamInfo', ['url', 'name', 'json'])

# Try to import from brainframe_apps, fallback to print for standalone testing
try:
    from brainframe_apps.logger_factory import log
except ImportError:
    # Standalone mode for testing without brainframe_apps installed
    class StandaloneLogger:
        @staticmethod
        def debug(msg):
            print(msg)
        
        @staticmethod
        def error(msg):
            print(f"ERROR: {msg}", file=sys.stderr)
    
    log = StandaloneLogger()


def get_ip():
    """Get the local machine's IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("192.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


class UrlList:
    """
    Iterator for reading and parsing stream URLs from a list file.
    
    This is a wrapper class that provides backward compatibility with the original
    implementation while adding new features.
    
    Features:
    - Ignores empty lines
    - Ignores comment lines starting with '#'
    - Ignores lines starting with '<' (after stripping whitespace)
    - Only processes lines containing 'rtsp://'
    - Extracts the first comma-separated value that starts with 'rtsp://'
    - Replaces 'localhost' with actual IP address
    
    Returns None if the file cannot be opened or doesn't exist.
    """
    
    def __new__(cls, url_list: Path):
        __url_list = __UrlList__(url_list)
        
        if __url_list is None:
            return None
        
        self = object.__new__(cls)
        self.url_list = __url_list
        
        return self
    
    def __init__(self, url_list: Path):
        pass
    
    def __iter__(self):
        return self
    
    def __next__(self):
        """
        Get the next valid stream info from the file.
        
        Returns:
            StreamInfo: Named tuple with 'url' and 'name' attributes
            
        Raises:
            StopIteration: When no more URLs are available
        """
        for line_str in self.url_list:
            # Parse the line to extract URL and name
            stream_info = self._parse_line(line_str)
            
            if stream_info is not None:
                return stream_info
        
        # End of iteration
        raise StopIteration
    
    def _parse_line(self, line_str):
        """
        Parse a single line to extract the stream URL and optional name.
        
        Args:
            line_str: Stripped line from the file
            
        Returns:
            StreamInfo or None: Named tuple with url and name, or None if line should be skipped
        """
        # Skip lines starting with '<' (scheduling groups)
        if line_str.startswith('<'):
            return None
        
        # Skip lines that don't contain 'rtsp://'
        if 'rtsp://' not in line_str:
            return None
        
        # Split by comma
        try:
            # csv.reader expects an iterable of lines, so we wrap the single line in a list
            parts = next(csv.reader([line_str]))
        except StopIteration:
            return None
        
        # Find the part starting with 'rtsp://'
        url = None
        url_index = -1
        for i, part in enumerate(parts):
            part_stripped = part.strip()
            if part_stripped.startswith('rtsp://'):
                url = part_stripped
                url_index = i
                break
        
        if url is None:
            # No part started with 'rtsp://' (edge case)
            return None
        
        # Check if there's a name field after the URL
        name = None
        if url_index + 1 < len(parts):
            name_field = parts[url_index + 1].strip()
            if name_field:  # Non-empty
                name = name_field
        
        # If no name provided, use the URL as the name
        if name is None:
            name = url
        
        # Check for a third column to use as runtime options
        json_data = None
        if url_index + 2 < len(parts):
            options_field = parts[url_index + 2].strip()
            if options_field:
                try:
                    py_dict = ast.literal_eval(options_field)
                    json_data = json.dumps(py_dict)
                except (ValueError, SyntaxError) as e:
                    log.error(f"Could not parse runtime options string: {options_field}")
                    log.error(f"Error: {e}")
                    json_data = options_field
        
        return StreamInfo(url=url, name=name, json=json_data)


class __UrlList__:
    """
    Internal iterator that reads lines from the URL list file.
    
    This class handles the actual file I/O and basic line processing.
    """
    
    def __new__(cls, url_list: Path):
        if url_list is None:
            log.error("The stream list file is None")
            return None
        
        if os.path.isfile(url_list) is not True:
            log.error(f"{url_list} file is not found")
            return None
        
        return object.__new__(cls)
    
    def __init__(self, url_list: Path):
        self.localhost_ip = get_ip()
        self.file = open(url_list)
    
    def __iter__(self):
        return self
    
    def __next__(self):
        """
        Read the next line from the file.
        
        Returns:
            str: Next non-empty, non-comment line with localhost replaced
            
        Raises:
            StopIteration: When end of file is reached
        """
        for self.line in self.file:
            line_str = self.line.strip()
            
            # Skip empty lines
            if line_str == "":
                continue
            
            # Skip comment lines starting with "#"
            if line_str.startswith("#"):
                continue
            
            # Skip lines starting with '<' (after whitespace)
            if line_str.startswith("<"):
                continue
            
            # Replace localhost with actual IP
            one_url = line_str.replace("localhost", str(self.localhost_ip))
            
            return one_url
        
        else:
            # End of file
            self.file.close()
            raise StopIteration


def _urls_parse_args(parser):
    """Add URL list argument to argument parser."""
    parser.add_argument(
        "--stream-urls",
        default='stream-urls.csv',
        help="The name of the file with the list of stream urls. Default: %(default)s",
    )


def main():
    """Main entry point for testing the URL parser."""
    parser = ArgumentParser(description="BrainFrame Apps files, dirs, args")
    _urls_parse_args(parser)
    args = parser.parse_args()
    
    url_list = UrlList(Path(args.stream_urls))
    if url_list:
        stream_count = 0
        for stream_info in url_list:
            stream_count += 1
            log.debug(f"Stream {stream_count}:")

            log.debug(f"  RTSP URL: {stream_info.url}")
            log.debug(f"  Name: {stream_info.name}")
            
            if stream_info.json:
                try:
                    runtime_options = json.loads(stream_info.json)
                    log.debug("  JSON Key/Value Pairs:")
                    for key, value in runtime_options.items():
                        log.debug(f"     {key}: {value}")
                        
                except json.JSONDecodeError as e:
                    log.error(f"  Failed to parse JSON: {e}")
    
    return


if __name__ == "__main__":
    main()
