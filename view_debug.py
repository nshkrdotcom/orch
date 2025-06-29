#!/usr/bin/env python3
"""
View the latest debug log and output files from the last pipeline run.
"""

import os
import json
import sys
from pathlib import Path
import argparse

def find_latest_debug_log(output_dir):
    """Find the most recent debug log file"""
    output_path = Path(output_dir)
    debug_logs = list(output_path.glob("*/debug_*.log"))
    
    if not debug_logs:
        print("No debug logs found.")
        return None
        
    # Sort by modification time
    latest = max(debug_logs, key=lambda p: p.stat().st_mtime)
    return latest

def find_output_files(output_dir):
    """Find all JSON output files in the directory"""
    output_files = []
    for f in Path(output_dir).rglob("*.json"):
        if "debug" not in f.name:  # Skip debug files
            output_files.append(f)
    
    # Sort by modification time
    output_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return output_files

def print_separator(title):
    """Print a formatted separator"""
    print(f"\n{'='*80}")
    print(f"=== {title} ===")
    print(f"{'='*80}\n")

def main():
    parser = argparse.ArgumentParser(description="View debug logs and outputs from pipeline runs")
    parser.add_argument("-o", "--output-dir", default="outputs", help="Output directory to search")
    parser.add_argument("-n", "--no-content", action="store_true", help="Only show file paths, not content")
    parser.add_argument("-l", "--log-only", action="store_true", help="Only show debug log")
    parser.add_argument("-f", "--files-only", action="store_true", help="Only show output files")
    
    args = parser.parse_args()
    
    # Find latest debug log
    if not args.files_only:
        debug_log = find_latest_debug_log(args.output_dir)
        if debug_log:
            print_separator(f"Debug Log: {debug_log}")
            if not args.no_content:
                with open(debug_log, 'r') as f:
                    print(f.read())
            else:
                print(f"Path: {debug_log}")
    
    # Find output files
    if not args.log_only:
        output_files = find_output_files(args.output_dir)
        
        if output_files:
            # Group by directory
            by_dir = {}
            for f in output_files:
                dir_name = f.parent.name
                if dir_name not in by_dir:
                    by_dir[dir_name] = []
                by_dir[dir_name].append(f)
            
            # Show most recent directory's files
            if by_dir:
                latest_dir = list(by_dir.keys())[0]
                print_separator(f"Output Files from: {latest_dir}")
                
                for f in by_dir[latest_dir]:
                    if not args.no_content:
                        print(f"\n--- {f.name} ---")
                        try:
                            with open(f, 'r') as file:
                                content = json.load(file)
                                print(json.dumps(content, indent=2))
                        except json.JSONDecodeError:
                            with open(f, 'r') as file:
                                print(file.read())
                        except Exception as e:
                            print(f"Error reading {f}: {e}")
                    else:
                        print(f"Path: {f}")

if __name__ == "__main__":
    main()