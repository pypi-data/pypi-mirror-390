# TNS CLI Tool

Command-line interface for TAO Name Service - production-ready CLI similar to btcli.

## Quick Installation (Recommended)

### Install from PyPI (Once Published)

```bash
# Install globally - just like 'pip install btcli' for Bittensor
pip install tnscli

# Verify installation
tns --version
tns --help
```

### Install from Source

```bash
# Clone or download the repository
cd tns/cli

# Install globally (creates 'tns' command)
pip install .

# Or install in editable mode for development
pip install -e .
```

After installation, the `tns` command will be available from any directory:
```bash
tns --help
tns stats
tns check mydomain
```

## Alternative: Local Installation

If you prefer to run locally without system-wide installation:

```bash
# 1. Run the automated install script
./install.sh

# 2. Activate the virtual environment
source venv/bin/activate

# 3. Use the CLI
./tns.py --help
```

## Commands

### Query Commands (No Wallet Required)

**Check Domain Availability:**
```bash
python tns.py check alice
```

**Resolve Domain:**
```bash
python tns.py resolve alice.tao
```

**Search Domains:**
```bash
python tns.py search alice --limit 20
```

**Lookup by Address:**
```bash
python tns.py lookup 5F3sa2TJAbpD9LgKr8WZitnWjExqWXqUhPnK8Mv5S3FQGn8Y
python tns.py lookup ADDRESS --type coldkey
python tns.py lookup ADDRESS --type hotkey
```

**Platform Statistics:**
```bash
python tns.py stats
```

### Blockchain Commands (Require Wallet)

**Register Domain:**
```bash
python tns.py register alice 5F3sa2TJAbpD9LgKr8WZitnWjExqWXqUhPnK8Mv5S3FQGn8Y
# You will be prompted for your mnemonic phrase
```

**Link Hotkey:**
```bash
python tns.py link alice 5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY
```

**Transfer Domain:**
```bash
python tns.py transfer alice 5F3sa2TJAbpD9LgKr8WZitnWjExqWXqUhPnK8Mv5S3FQGn8Y
```

**Renew Domain:**
```bash
python tns.py renew alice
```

## Features

- Rich terminal output with colors and tables
- Interactive confirmations for blockchain transactions
- Secure mnemonic input (hidden)
- Error handling and validation
- Support for all TNS operations

## Environment Variables

- `TNS_API_URL`: TNS REST API endpoint
- `TNS_WS_URL`: Subtensor WebSocket endpoint

Current configuration uses secure Cloudflare tunnel endpoints for production reliability.

## Examples

### Check if domain is available
```bash
$ python tns.py check alice
✓ alice.tao is AVAILABLE
Registration fee: 0.5 TAO
```

### Resolve a domain
```bash
$ python tns.py resolve alice
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field              ┃ Value                                              ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Owner              │ 5F3sa2TJAbpD9LgKr8WZitnWjExqWXqUhPnK8Mv5S3FQGn8Y │
│ Coldkey            │ 5F3sa2TJAbpD9LgKr8WZitnWjExqWXqUhPnK8Mv5S3FQGn8Y │
│ Hotkey             │ 5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY │
│ Expires at block   │ 5256000                                            │
│ Registered at block│ 1000                                               │
│ Status             │ Active                                             │
└────────────────────┴────────────────────────────────────────────────────┘
```

### View statistics
```bash
$ python tns.py stats
╭───────── TNS Platform Statistics ──────────╮
│ Total Domains: 42                          │
│ Active Domains: 38                         │
│ Expired Domains: 4                         │
│ Total Events: 156                          │
│ Recent Registrations (24h): 5              │
╰────────────────────────────────────────────╯
```

## Security Notes

- Never share your mnemonic phrase
- The CLI prompts for mnemonic securely (hidden input)
- Mnemonic is not stored or logged
- All blockchain transactions require confirmation

## Troubleshooting

**Import Error:**
Make sure you're in the virtual environment and have installed dependencies.

**Connection Error:**
Check that the API and blockchain node are running at the configured URLs.

**Transaction Failed:**
Ensure you have sufficient TAO balance to pay transaction fees.
