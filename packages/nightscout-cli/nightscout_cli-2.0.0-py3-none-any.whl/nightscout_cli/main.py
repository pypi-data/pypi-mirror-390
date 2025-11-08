#!/usr/bin/env python3
"""
Nightscout CLI - Command line interface for Nightscout API
"""
import argparse
import requests
import json
import sys
import os
from datetime import datetime, timedelta, timezone

# --- Configuration Constants and Helper Functions ---
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "nightscout-cli")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def load_config():
    """Loads configuration from the config file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config file {CONFIG_FILE}: {e}", file=sys.stderr)
            sys.exit(1)
    return {}

def save_config(config_data):
    """Saves configuration to the config file."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
        print(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"Error saving config file {CONFIG_FILE}: {e}", file=sys.stderr)
        sys.exit(1)

def get_config_or_crash():
    """Determines final configuration, crashing if env vars and config file coexist."""
    # 1. Load from config file
    config_from_file = load_config()
    config_exists = bool(config_from_file)
    # 2. Check environment variables
    env_vars_set = {
        'host': os.environ.get("NIGHTSCOUT_HOST"),
        'port': os.environ.get("NIGHTSCOUT_PORT"),
        'api_secret': os.environ.get("NIGHTSCOUT_API_SECRET"),
    }
    env_vars_exist = any(env_vars_set.values())
    # 3. Crash condition
    if config_exists and env_vars_exist:
        print("Fatal Error: Both configuration file and environment variables are set.", file=sys.stderr)
        print(f"To use the config file, unset all NIGHTSCOUT_* environment variables.", file=sys.stderr)
        print(f"Config file: {CONFIG_FILE}", file=sys.stderr)
        print(f"Environment variables set: {', '.join([k for k, v in env_vars_set.items() if v is not None])}", file=sys.stderr)
        sys.exit(1)
    # 4. Determine final configuration defaults
    if env_vars_exist:
        # Prioritize environment variables if they are the only source
        print("Using environment variables for configuration.", file=sys.stderr)
        DEFAULT_HOST = env_vars_set['host'] or "127.0.0.1"
        DEFAULT_PORT = env_vars_set['port'] or "80"
        DEFAULT_API_SECRET = env_vars_set['api_secret'] or "soilentgreenandblue"
    elif config_exists:
        # Use config file if it's the only source
        print(f"Using configuration from {CONFIG_FILE}.", file=sys.stderr)
        DEFAULT_HOST = config_from_file.get('host', "127.0.0.1")
        DEFAULT_PORT = config_from_file.get('port', "80")
        DEFAULT_API_SECRET = config_from_file.get('api_secret', "soilentgreenandblue")
    else:
        # Fallback to hardcoded defaults
        print("Using default configuration (127.0.0.1:80). Please set host/secret.", file=sys.stderr)
        DEFAULT_HOST = "127.0.0.1"
        DEFAULT_PORT = "80"
        DEFAULT_API_SECRET = "soilentgreenandblue"
    return DEFAULT_HOST, DEFAULT_PORT, DEFAULT_API_SECRET

# Load configuration at script startup
DEFAULT_HOST, DEFAULT_PORT, DEFAULT_API_SECRET = get_config_or_crash()

# --- API Interaction Functions ---
def api_get(base_url, api_secret, endpoint, params=None, debug=False):
    """Make authenticated GET request to Nightscout API"""
    headers = {"API-SECRET": api_secret}
    url = f"{base_url}{endpoint}"
    if debug:
        print(f"DEBUG: GET {url}", file=sys.stderr)
        print(f"DEBUG: Headers: ***REDACTED***", file=sys.stderr) # Mask secret in debug output
        print(f"DEBUG: Params: {params}", file=sys.stderr)
    try:
        response = requests.get(url, headers=headers, params=params)
        if debug:
            print(f"DEBUG: Status Code: {response.status_code}", file=sys.stderr)
            print(f"DEBUG: Response length: {len(response.text)} bytes", file=sys.stderr)
            print(f"DEBUG: Full URL: {response.url}", file=sys.stderr)
        response.raise_for_status()
        result = response.json()
        if debug:
            print(f"DEBUG: Returned {len(result)} entries", file=sys.stderr)
        return result
    except requests.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        if debug and hasattr(e, 'response') and e.response is not None:
            print(f"DEBUG: Response text: {e.response.text}", file=sys.stderr)
        sys.exit(1)

def api_post(base_url, api_secret, endpoint, data):
    """Make authenticated POST request to Nightscout API"""
    headers = {
        "API-SECRET": api_secret,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(f"{base_url}{endpoint}", headers=headers, json=data)
        response.raise_for_status()
        # Try to parse as JSON, but if it fails just return the text
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"status": "success", "text": response.text}
    except requests.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def api_delete(base_url, api_secret, endpoint):
    """Make authenticated DELETE request to Nightscout API"""
    headers = {"API-SECRET": api_secret}
    try:
        response = requests.delete(f"{base_url}{endpoint}", headers=headers)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

# --- Command Implementations ---
def cmd_get(args):
    """Get the latest blood glucose reading"""
    base_url = f"http://{args.host}:{args.port}"
    # Use the count argument, defaulting to 1
    count = args.count if args.count is not None else 1
    entries = reversed(api_get(base_url, args.api_secret, "/api/v1/entries.json", params={"count": count}, debug=args.debug))

    if not entries:
        print("No data available")
        return

    for entry in entries:
        # Format: timestamp value units direction
        timestamp = datetime.fromisoformat(entry['dateString'].replace('Z', '+00:00'))
        value = entry.get('sgv', 'N/A')
        units = entry.get('units', 'mg/dL')
        direction = entry.get('direction', '')
        print(f"{timestamp.isoformat()} {value} {units} {direction}")

def cmd_history(args):
    """Get historical glucose data"""
    base_url = f"http://{args.host}:{args.port}"
    # Determine the start of today (UTC midnight)
    now_utc = datetime.now(timezone.utc)
    start_of_today_utc = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    # Calculate the start time aligned to midnight 'args.days_ago' ago
    start_time = start_of_today_utc - timedelta(days=args.days_ago)
    # Calculate the end time based on the period.
    # By default, a 1440 min (24hr) period captures the whole target day.
    end_time = start_time + timedelta(minutes=args.period)
    if args.debug:
        print(f"DEBUG: Start time (aligned to midnight): {start_time.isoformat()}", file=sys.stderr)
        print(f"DEBUG: End time: {end_time.isoformat()}", file=sys.stderr)
        print(f"DEBUG: Start timestamp (ms): {int(start_time.timestamp() * 1000)}", file=sys.stderr)
        print(f"DEBUG: End timestamp (ms): {int(end_time.timestamp() * 1000)}", file=sys.stderr)
    # Convert to milliseconds since epoch for the query
    params = {
        "find[date][$gte]": int(start_time.timestamp() * 1000),
        "find[date][$lte]": int(end_time.timestamp() * 1000),
        "count": 10000  # Large number to get all entries
    }
    entries = reversed(api_get(base_url, args.api_secret, "/api/v1/entries.json", params=params, debug=args.debug))
    if args.jsonl:
        # Output as JSONL (one JSON object per line)
        for entry in entries:
            # Include timestamp, sgv, units
            output = {
                "timestamp": entry.get('dateString'),
                "sgv": entry.get('sgv'),
                "units": entry.get('units', 'mg/dL'),
                "direction": entry.get('direction', '')
            }
            print(json.dumps(output))
    else:
        # Human-readable output
        for entry in entries:
            timestamp = entry.get('dateString')
            value = entry.get('sgv', 'N/A')
            units = entry.get('units', 'mg/dL')
            print(f"{timestamp} {value} {units}")

def cmd_push(args):
    """Push a blood glucose reading to Nightscout"""
    base_url = f"http://{args.host}:{args.port}"
    # Calculate timestamp - use UTC
    if args.minutes_ago:
        timestamp = datetime.now(timezone.utc) - timedelta(minutes=args.minutes_ago)
    else:
        timestamp = datetime.now(timezone.utc)
    # Prepare entry data
    entry = {
        "type": "sgv",
        "sgv": args.value,
        "dateString": timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
        "date": int(timestamp.timestamp() * 1000)  # milliseconds since epoch
    }
    # Add optional direction if provided
    if args.direction:
        entry["direction"] = args.direction
    # Post the entry (as an array - Nightscout expects an array)
    try:
        result = api_post(base_url, args.api_secret, "/api/v1/entries", [entry])
        print(f"Successfully pushed: {timestamp.isoformat()} {args.value} mg/dL")
        if args.direction:
            print(f"Direction: {args.direction}")
    except Exception as e:
        print(f"Failed to push entry: {e}", file=sys.stderr)
        sys.exit(1)

def cmd_list(args):
    """List recent glucose entries with their IDs"""
    base_url = f"http://{args.host}:{args.port}"
    params = {"count": args.count}
    entries = api_get(base_url, args.api_secret, "/api/v1/entries.json", params=params, debug=args.debug)
    if not entries:
        print("No entries found")
        return
    # CSV output
    print("id,timestamp,value")
    for entry in entries:
        entry_id = entry.get('_id', 'N/A')
        timestamp = entry.get('dateString', 'N/A')
        value = entry.get('sgv', 'N/A')
        print(f"{entry_id},{timestamp},{value}")

def cmd_delete(args):
    """Delete a glucose entry by ID"""
    base_url = f"http://{args.host}:{args.port}"
    if args.all:
        # Get all entries and delete them
        entries = api_get(base_url, args.api_secret, "/api/v1/entries.json", params={"count": 10000}, debug=args.debug)
        if not entries:
            print("No entries to delete")
            return
        confirm = input(f"Are you sure you want to delete {len(entries)} entries? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled")
            return
        deleted = 0
        for entry in entries:
            entry_id = entry.get('_id')
            if api_delete(base_url, args.api_secret, f"/api/v1/entries/{entry_id}"):
                deleted += 1
                print(f"Deleted {entry_id}")
        print(f"\nDeleted {deleted} of {len(entries)} entries")
    else:
        # Delete multiple entries by ID
        if not args.entry_ids:
            print("Error: at least one entry_id is required unless using --all", file=sys.stderr)
            sys.exit(1)
        deleted = 0
        failed = 0
        for entry_id in args.entry_ids:
            success = api_delete(base_url, args.api_secret, f"/api/v1/entries/{entry_id}")
            if success:
                print(f"Deleted {entry_id}")
                deleted += 1
            else:
                print(f"Failed to delete {entry_id}")
                failed += 1
        print(f"\nDeleted {deleted} entries, {failed} failed")

def cmd_config(args):
    """Set or display configuration."""
    current_config = load_config()
    if args.host or args.api_secret:
        # Set command
        if args.host:
            current_config['host'] = args.host
        if args.api_secret:
            current_config['api_secret'] = args.api_secret
        # Port can be included later if required, but for now we'll keep host and secret
        if args.port:
            current_config['port'] = args.port
        save_config(current_config)
    else:
        # Display command (if no arguments are passed)
        print(f"Current Config File: {CONFIG_FILE}")
        if current_config:
            print("-" * 30)
            print(f"Host: {current_config.get('host', 'N/A')}")
            print(f"Port: {current_config.get('port', 'N/A')}")
            # Do not display the secret directly
            secret_present = "Present" if 'api_secret' in current_config else "Not Set"
            print(f"API Secret: {secret_present}")
            print("-" * 30)
        else:
            print("Configuration file not found or is empty.")

# --- Main Parser Logic ---
def main():
    parser = argparse.ArgumentParser(
        description="Nightscout CLI - Command line interface for Nightscout API"
    )
    # Global arguments - now using defaults derived from config/env check
    parser.add_argument('--host', default=DEFAULT_HOST,
                        help=f'Nightscout host (default: {DEFAULT_HOST}, or config file/env var)')
    parser.add_argument('--port', default=DEFAULT_PORT,
                        help=f'Nightscout port (default: {DEFAULT_PORT}, or config file/env var)')
    parser.add_argument('--api-secret', default=DEFAULT_API_SECRET,
                        help='API secret (default: from config file/env var)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug output')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # config command
    parser_config = subparsers.add_parser('config', help='Set or display host and API secret')
    parser_config.add_argument('--host', help='Set the Nightscout host')
    parser_config.add_argument('--port', help='Set the Nightscout port')
    parser_config.add_argument('--api-secret', help='Set the API secret')
    parser_config.set_defaults(func=cmd_config)

    # get command
    parser_get = subparsers.add_parser('get', help='Get the latest blood glucose reading(s)')
    # Added optional positional argument for count
    parser_get.add_argument('count', type=int, nargs='?', default=None,
                            help='Number of entries to retrieve (default: 1)')
    parser_get.set_defaults(func=cmd_get)

    # history command
    parser_history = subparsers.add_parser('history', help='Get historical glucose data')
    parser_history.add_argument('--days-ago', type=int, default=1,  # CHANGED DEFAULT FROM 0 TO 1
                                help='Number of days ago to fetch data for (0=today, 1=yesterday). Start time is aligned to midnight UTC.')
    parser_history.add_argument('--period', type=int, default=1440,
                                help='Period in minutes to fetch (default: 1440 = 24 hours, starting from midnight).')
    parser_history.add_argument('--jsonl', action='store_true',
                                help='Output as JSONL (one JSON object per line)')
    parser_history.set_defaults(func=cmd_history)

    # push command
    parser_push = subparsers.add_parser('push', help='Push a blood glucose reading to Nightscout')
    parser_push.add_argument('value', type=int, help='Blood glucose value (mg/dL)')
    parser_push.add_argument('--minutes-ago', type=int, default=0,
                            help='Number of minutes ago for this reading (default: 0 = now)')
    parser_push.add_argument('--direction', choices=['Flat', 'FortyFiveUp', 'FortyFiveDown', 'SingleUp', 'SingleDown', 'DoubleUp', 'DoubleDown'],
                            help='Trend direction (optional)')
    parser_push.set_defaults(func=cmd_push)

    # list command
    parser_list = subparsers.add_parser('list', help='List recent glucose entries')
    parser_list.add_argument('--count', type=int, default=20,
                            help='Number of entries to list (default: 20)')
    parser_list.set_defaults(func=cmd_list)

    # delete command
    parser_delete = subparsers.add_parser('delete', help='Delete glucose entry/entries')
    parser_delete.add_argument('entry_ids', nargs='*', help='Entry ID(s) to delete')
    parser_delete.add_argument('--all', action='store_true',
                                help='Delete ALL entries (use with caution!)')
    parser_delete.set_defaults(func=cmd_delete)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # The global arguments (host, port, api_secret, debug) are automatically attached to args
    # and override any defaults for the sub-command, but here we pass the final args object.
    args.func(args)

if __name__ == '__main__':
    main()
