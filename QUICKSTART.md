# Quick Start Guide - Pokemon Center Discord Bot

## 5-Minute Setup

### 1. Install Dependencies
```bash
pip install discord.py requests python-dotenv
```

### 2. Create Discord Bot
1. Go to https://discord.com/developers/applications
2. Click "New Application" → Name it → "Create"
3. Go to "Bot" tab → "Add Bot"
4. Enable "MESSAGE CONTENT INTENT" under Privileged Gateway Intents
5. Click "Reset Token" and copy your token
6. Go to "OAuth2" → "URL Generator"
   - Check: `bot`
   - Bot Permissions: Check "Send Messages", "Embed Links", "Read Messages/View Channels"
   - Copy the URL and open in browser to invite bot to your server

### 3. Configure Bot Token

Create a file named `.env`:
```
DISCORD_BOT_TOKEN=paste_your_token_here
```

### 4. Update API Endpoint

Open `pokemon_center_discord_bot.py` and find line 27:
```python
self.api_url = "YOUR_ACTUAL_API_HERE"
```

**How to find the API:**
1. Open Pokemon Center in browser
2. Press F12 → Network tab → Filter by "XHR"
3. Refresh page
4. Look for JSON responses with product data
5. Copy that URL

### 5. Run the Bot
```bash
python pokemon_center_discord_bot.py
```

### 6. Configure in Discord

In your Discord server, type:
```
!pc setchannel
```
(in the channel where you want notifications)

Then check status:
```
!pc status
```

## Done! 🎉

The bot will now check every 5 minutes and post new listings.

## Common Commands

- `!pc check` - Manual check
- `!pc interval 600` - Change to 10 minutes
- `!pc help` - Show all commands

## Troubleshooting

**Bot not online?**
- Check token in .env file
- Verify MESSAGE CONTENT INTENT is enabled

**No notifications?**
- Run `!pc setchannel` first
- Use `!pc check` to test manually
- Check console for errors

**Need help?** See full DISCORD_BOT_SETUP.md for detailed guide.
