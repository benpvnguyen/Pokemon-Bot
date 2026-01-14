# Pokemon Center Discord Bot Setup Guide

A Discord bot that monitors Pokemon Center for new product listings and posts beautiful embed notifications to your Discord server.

## Features

- 🤖 Automated monitoring with configurable intervals
- 📢 Posts new listings to a designated Discord channel
- 🎨 Beautiful embed messages with product images
- ⚙️ Easy configuration with Discord commands
- 🔄 Manual check capability
- 📊 Status monitoring
- 🔐 Admin-only commands for security

## Prerequisites

1. Python 3.8 or higher
2. A Discord account
3. Administrator access to a Discord server

## Step 1: Create a Discord Bot

1. **Go to Discord Developer Portal**
   - Visit: https://discord.com/developers/applications
   - Log in with your Discord account

2. **Create New Application**
   - Click "New Application"
   - Give it a name (e.g., "Pokemon Center Monitor")
   - Click "Create"

3. **Create Bot User**
   - Go to the "Bot" tab on the left sidebar
   - Click "Add Bot" → "Yes, do it!"
   - Under "Privileged Gateway Intents", enable:
     - ✅ MESSAGE CONTENT INTENT (important!)
     - ✅ SERVER MEMBERS INTENT (optional)

4. **Get Your Bot Token**
   - Under the bot settings, click "Reset Token"
   - Copy the token (you'll need this later)
   - ⚠️ **NEVER share this token publicly!**

5. **Invite Bot to Your Server**
   - Go to "OAuth2" → "URL Generator"
   - Select scopes:
     - ✅ bot
     - ✅ applications.commands (optional)
   - Select bot permissions:
     - ✅ Send Messages
     - ✅ Embed Links
     - ✅ Read Messages/View Channels
     - ✅ Read Message History
   - Copy the generated URL at the bottom
   - Open the URL in your browser
   - Select your server and authorize

## Step 2: Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements_discord.txt
```

Or install individually:
```bash
pip install discord.py requests python-dotenv
```

2. **Set up your bot token:**

**Option A: Environment Variable (Recommended)**

Linux/Mac:
```bash
export DISCORD_BOT_TOKEN='your_bot_token_here'
```

Windows (Command Prompt):
```cmd
set DISCORD_BOT_TOKEN=your_bot_token_here
```

Windows (PowerShell):
```powershell
$env:DISCORD_BOT_TOKEN='your_bot_token_here'
```

**Option B: .env File (More Permanent)**

Create a file named `.env` in the same directory as the bot:
```
DISCORD_BOT_TOKEN=your_bot_token_here
```

Then modify the bot script to load it:
```python
from dotenv import load_dotenv
load_dotenv()  # Add this at the top of main()
```

## Step 3: Configure the API Endpoint

**IMPORTANT:** You need to find Pokemon Center's actual JSON API endpoint.

### How to Find the API Endpoint:

1. Open Pokemon Center website in Chrome/Firefox
2. Press F12 to open Developer Tools
3. Go to "Network" tab
4. Filter by "XHR" or "Fetch"
5. Refresh the page or navigate to product listings
6. Look for JSON responses containing product data
7. Copy the full URL of the API endpoint

### Update the Bot Script:

Edit line 27 in `pokemon_center_discord_bot.py`:
```python
self.api_url = "YOUR_ACTUAL_API_ENDPOINT_HERE"
```

### Adjust JSON Parsing (if needed):

The `fetch_listings()` method (lines 49-77) may need adjustment based on the actual JSON structure. Common structures:

**Example 1: Products in array**
```python
if isinstance(data, list):
    for product in data:
        product_id = product.get('id')
        # ... process product
```

**Example 2: Products nested in object**
```python
if isinstance(data, dict):
    products = data.get('data', {}).get('products', [])
    for product in products:
        # ... process product
```

## Step 4: Run the Bot

Start the bot:
```bash
python pokemon_center_discord_bot.py
```

You should see:
```
🎮 Pokemon Center Bot is online!
Logged in as: YourBotName (ID: 123456789)
Connected to 1 server(s)
------
```

## Step 5: Configure in Discord

Once the bot is running, use these commands in your Discord server:

### 1. Set Notification Channel
```
!pc setchannel
```
Run this command in the channel where you want new listing notifications.

### 2. Check Status
```
!pc status
```
Verify the bot is configured correctly.

### 3. Test Manually
```
!pc check
```
Manually trigger a check for new listings.

## Bot Commands Reference

| Command | Description | Permission |
|---------|-------------|------------|
| `!pc setchannel` | Set current channel for notifications | Admin |
| `!pc status` | Check bot status and configuration | Everyone |
| `!pc interval <seconds>` | Set check interval (min: 60) | Admin |
| `!pc check` | Manually check for new listings | Admin |
| `!pc reset` | Reset cache (treats all as new) | Admin |
| `!pc help` | Show command help | Everyone |

### Command Examples:

**Set check interval to 10 minutes:**
```
!pc interval 600
```

**Set check interval to 1 hour:**
```
!pc interval 3600
```

**Manual check:**
```
!pc check
```

## How It Works

1. **Background Task**: The bot runs a background task that checks Pokemon Center every X seconds (default: 5 minutes)

2. **New Item Detection**: Compares current listings with cached listings to identify new products

3. **Discord Notification**: Posts a beautiful embed for each new item with:
   - Product name and image
   - Price
   - Direct link to product
   - Description (truncated if long)
   - Timestamp

4. **Cache Management**: Stores seen listings in `pokemon_center_cache.json` to avoid duplicate notifications

## Customization

### Change Bot Prefix

Edit line 17 in the bot script:
```python
command_prefix='!pc ',  # Change '!pc ' to whatever you want
```

### Customize Embed Colors

Edit the embed creation in `send_discord_notification()`:
```python
color=discord.Color.blue(),    # Try: .red(), .green(), .gold(), .purple()
```

### Change Default Check Interval

Edit line 25:
```python
self.check_interval = 300  # Change 300 to your desired seconds
```

### Add Ping/Mention on New Items

Modify the notification sending:
```python
await channel.send(f"<@&YOUR_ROLE_ID> New listing!", embed=embed)
```

### Customize Embed Footer

Edit line 141:
```python
embed.set_footer(text="Your Custom Text", icon_url="your_icon_url")
```

## Running as a Background Service

### Linux (systemd)

Create `/etc/systemd/system/pokemon-discord-bot.service`:
```ini
[Unit]
Description=Pokemon Center Discord Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/bot
Environment="DISCORD_BOT_TOKEN=your_token_here"
ExecStart=/usr/bin/python3 /path/to/pokemon_center_discord_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable pokemon-discord-bot
sudo systemctl start pokemon-discord-bot
sudo systemctl status pokemon-discord-bot
```

View logs:
```bash
sudo journalctl -u pokemon-discord-bot -f
```

### Windows (as a Windows Service)

Use NSSM (Non-Sucking Service Manager):

1. Download NSSM: https://nssm.cc/download
2. Open Command Prompt as Administrator
3. Run:
```cmd
nssm install PokemonBot
```
4. In the GUI:
   - Path: `C:\Python\python.exe`
   - Startup directory: `C:\path\to\bot`
   - Arguments: `pokemon_center_discord_bot.py`
   - Environment: Add `DISCORD_BOT_TOKEN=your_token`
5. Click "Install service"
6. Start with: `nssm start PokemonBot`

### Screen/tmux (Simple Linux Solution)

Using screen:
```bash
screen -S pokemon-bot
python3 pokemon_center_discord_bot.py
# Press Ctrl+A, then D to detach
```

Reattach later:
```bash
screen -r pokemon-bot
```

### Docker (Advanced)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements_discord.txt .
RUN pip install -r requirements_discord.txt

COPY pokemon_center_discord_bot.py .

CMD ["python", "pokemon_center_discord_bot.py"]
```

Build and run:
```bash
docker build -t pokemon-bot .
docker run -d --name pokemon-bot \
  -e DISCORD_BOT_TOKEN=your_token \
  --restart unless-stopped \
  pokemon-bot
```

## Troubleshooting

### Bot doesn't come online
- ✅ Check bot token is correct
- ✅ Verify MESSAGE CONTENT INTENT is enabled in Discord Developer Portal
- ✅ Check Python version is 3.8+

### No notifications appearing
- ✅ Run `!pc setchannel` in the desired channel
- ✅ Check bot has permission to send messages and embeds
- ✅ Verify API endpoint is correct with `!pc check`

### "Error fetching listings"
- ✅ Verify internet connection
- ✅ Check API endpoint is accessible
- ✅ Review console output for detailed error messages

### Rate limiting / Bot getting blocked
- ✅ Increase check interval: `!pc interval 900` (15 minutes)
- ✅ Don't set interval below 60 seconds
- ✅ Add delays in code if making multiple requests

### Bot crashes or stops
- ✅ Check console for error messages
- ✅ Set up as a service with auto-restart
- ✅ Ensure sufficient permissions

### Cache issues
- Reset with: `!pc reset`
- Or manually delete `pokemon_center_cache.json`

## Security Best Practices

1. **Never commit bot token to git**
   - Add `.env` and `*.json` to `.gitignore`

2. **Use environment variables for sensitive data**
   - Don't hardcode tokens in the script

3. **Restrict admin commands**
   - Bot uses `@commands.has_permissions(administrator=True)`
   - Only server admins can change settings

4. **Regular updates**
   - Keep discord.py and other libraries updated
   - Monitor for security vulnerabilities

## Advanced Features (Optional)

### Add Reaction Roles
```python
@bot.event
async def on_raw_reaction_add(payload):
    # Add role when user reacts to notification
    pass
```

### Add Database Support
```python
import sqlite3
# Store listings in SQLite instead of JSON
```

### Add Multiple Region Support
```python
regions = {
    'US': 'https://www.pokemoncenter.com/api/products',
    'UK': 'https://www.pokemoncenter.co.uk/api/products',
}
```

### Add Price Drop Alerts
```python
def detect_price_changes(old_listings, new_listings):
    # Compare prices and notify on drops
    pass
```

## Support

If you encounter issues:
1. Check the console output for detailed error messages
2. Verify all prerequisites are met
3. Test the API endpoint manually in a browser
4. Review Discord bot permissions
5. Check Python and library versions

## License

This bot is provided as-is for educational and personal use. Respect Pokemon Center's terms of service and don't abuse their API.

## Notes

- Be respectful of Pokemon Center's servers
- Don't set intervals too low (minimum 60 seconds recommended)
- The bot is for personal/community use only
- API endpoints may change - update the script accordingly
