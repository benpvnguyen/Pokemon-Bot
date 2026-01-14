#!/usr/bin/env python3
"""
Pokemon Center Discord Bot
Monitors Pokemon Center's product listings and posts notifications to Discord.
"""

import discord
from discord.ext import commands, tasks
import requests
import json
import asyncio
from datetime import datetime
from pathlib import Path
import os

class PokemonCenterBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix='!pc ',
            intents=intents,
            help_command=commands.DefaultHelpCommand()
        )
        
        # Configuration
        self.cache_file = Path("pokemon_center_cache.json")
        self.previous_listings = self.load_cache()
        self.api_url = "https://www.pokemoncenter.com/api/products"  # UPDATE THIS
        self.check_interval = 300  # 5 minutes in seconds
        self.notification_channel_id = None  # Will be set via command
        
    def load_cache(self):
        """Load previously seen listings from cache file."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("Cache file corrupted, starting fresh")
                return {}
        return {}
    
    def save_cache(self, listings):
        """Save current listings to cache file."""
        with open(self.cache_file, 'w') as f:
            json.dump(listings, f, indent=2)
    
    async def fetch_listings(self):
        """Fetch current listings from Pokemon Center."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            # Use asyncio to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(self.api_url, headers=headers, timeout=10)
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Process the response - adjust based on actual API structure
            listings = {}
            if isinstance(data, dict) and 'products' in data:
                for product in data.get('products', []):
                    product_id = product.get('id') or product.get('sku')
                    listings[product_id] = {
                        'name': product.get('name', 'Unknown'),
                        'price': product.get('price', 'N/A'),
                        'url': product.get('url', ''),
                        'image': product.get('image', ''),
                        'description': product.get('description', ''),
                        'timestamp': datetime.now().isoformat()
                    }
            
            return listings
            
        except Exception as e:
            print(f"Error fetching listings: {e}")
            return None
    
    def find_new_listings(self, current_listings):
        """Compare current listings with cached listings to find new items."""
        if current_listings is None:
            return []
        
        new_items = []
        for product_id, product_info in current_listings.items():
            if product_id not in self.previous_listings:
                new_items.append(product_info)
        
        return new_items
    
    async def send_discord_notification(self, channel, new_items):
        """Send notification about new listings to Discord channel."""
        if not new_items or not channel:
            return
        
        for item in new_items:
            # Create embed for each new item
            embed = discord.Embed(
                title="🎮 New Pokemon Center Listing!",
                description=item['name'],
                color=discord.Color.red(),  # Pokemon red
                timestamp=datetime.now(),
                url=item.get('url', '')
            )
            
            # Add fields
            if item.get('price') != 'N/A':
                embed.add_field(name="💰 Price", value=str(item['price']), inline=True)
            
            if item.get('url'):
                embed.add_field(name="🔗 Link", value=f"[View Product]({item['url']})", inline=True)
            
            if item.get('description'):
                description = item['description'][:200]
                if len(item['description']) > 200:
                    description += "..."
                embed.add_field(name="📝 Description", value=description, inline=False)
            
            # Add thumbnail if available
            if item.get('image'):
                embed.set_thumbnail(url=item['image'])
            
            # Add footer
            embed.set_footer(text="Pokemon Center Monitor", icon_url="https://i.imgur.com/AfFp7pu.png")
            
            try:
                await channel.send(embed=embed)
                await asyncio.sleep(1)  # Avoid rate limiting
            except Exception as e:
                print(f"Error sending Discord message: {e}")
    
    @tasks.loop(seconds=300)  # Default 5 minutes
    async def check_for_new_listings(self):
        """Background task to check for new listings."""
        if not self.notification_channel_id:
            return
        
        channel = self.get_channel(self.notification_channel_id)
        if not channel:
            return
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for new listings...")
        
        current_listings = await self.fetch_listings()
        
        if current_listings:
            new_items = self.find_new_listings(current_listings)
            
            if new_items:
                print(f"Found {len(new_items)} new listings!")
                await self.send_discord_notification(channel, new_items)
            else:
                print("No new listings found")
            
            # Update cache
            self.previous_listings = current_listings
            self.save_cache(current_listings)
    
    @check_for_new_listings.before_loop
    async def before_check_for_new_listings(self):
        """Wait until bot is ready before starting the loop."""
        await self.wait_until_ready()
    
    async def setup_hook(self):
        """Setup hook called when bot starts."""
        # Start the background task
        self.check_for_new_listings.start()


# Create bot instance
bot = PokemonCenterBot()


@bot.event
async def on_ready():
    """Called when bot is ready."""
    print(f'🎮 Pokemon Center Bot is online!')
    print(f'Logged in as: {bot.user.name} (ID: {bot.user.id})')
    print(f'Connected to {len(bot.guilds)} server(s)')
    print('------')


@bot.command(name='setchannel')
@commands.has_permissions(administrator=True)
async def set_channel(ctx):
    """Set the current channel for Pokemon Center notifications."""
    bot.notification_channel_id = ctx.channel.id
    
    embed = discord.Embed(
        title="✅ Channel Set Successfully",
        description=f"Pokemon Center notifications will be posted in {ctx.channel.mention}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)
    print(f"Notification channel set to: {ctx.channel.name} (ID: {ctx.channel.id})")


@bot.command(name='status')
async def status(ctx):
    """Check bot status and configuration."""
    channel = bot.get_channel(bot.notification_channel_id) if bot.notification_channel_id else None
    
    embed = discord.Embed(
        title="🎮 Pokemon Center Bot Status",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Notification Channel",
        value=channel.mention if channel else "Not set (use `!pc setchannel`)",
        inline=False
    )
    
    embed.add_field(
        name="Check Interval",
        value=f"{bot.check_interval} seconds ({bot.check_interval // 60} minutes)",
        inline=True
    )
    
    embed.add_field(
        name="Cached Listings",
        value=str(len(bot.previous_listings)),
        inline=True
    )
    
    embed.add_field(
        name="Monitoring Status",
        value="🟢 Active" if bot.check_for_new_listings.is_running() else "🔴 Inactive",
        inline=True
    )
    
    await ctx.send(embed=embed)


@bot.command(name='interval')
@commands.has_permissions(administrator=True)
async def set_interval(ctx, seconds: int):
    """
    Set the check interval in seconds.
    
    Usage: !pc interval 300
    """
    if seconds < 60:
        await ctx.send("⚠️ Interval must be at least 60 seconds to avoid rate limiting.")
        return
    
    bot.check_interval = seconds
    bot.check_for_new_listings.change_interval(seconds=seconds)
    
    embed = discord.Embed(
        title="✅ Interval Updated",
        description=f"Check interval set to {seconds} seconds ({seconds // 60} minutes)",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)


@bot.command(name='check')
@commands.has_permissions(administrator=True)
async def manual_check(ctx):
    """Manually trigger a check for new listings."""
    await ctx.send("🔍 Checking for new listings...")
    
    current_listings = await bot.fetch_listings()
    
    if current_listings is None:
        await ctx.send("❌ Failed to fetch listings. Check API endpoint and connection.")
        return
    
    new_items = bot.find_new_listings(current_listings)
    
    if new_items:
        await ctx.send(f"✅ Found {len(new_items)} new listing(s)! Posting them now...")
        channel = bot.get_channel(bot.notification_channel_id) if bot.notification_channel_id else ctx.channel
        await bot.send_discord_notification(channel, new_items)
        
        # Update cache
        bot.previous_listings = current_listings
        bot.save_cache(current_listings)
    else:
        await ctx.send("✅ Check complete. No new listings found.")


@bot.command(name='reset')
@commands.has_permissions(administrator=True)
async def reset_cache(ctx):
    """Reset the cache (will treat all current listings as new on next check)."""
    bot.previous_listings = {}
    bot.save_cache({})
    
    embed = discord.Embed(
        title="✅ Cache Reset",
        description="All listings will be considered new on the next check.",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)


@bot.command(name='help')
async def help_command(ctx):
    """Show help information."""
    embed = discord.Embed(
        title="🎮 Pokemon Center Bot - Commands",
        description="Monitor Pokemon Center for new product listings",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="!pc setchannel",
        value="Set current channel for notifications (Admin only)",
        inline=False
    )
    
    embed.add_field(
        name="!pc status",
        value="Check bot status and configuration",
        inline=False
    )
    
    embed.add_field(
        name="!pc interval <seconds>",
        value="Set check interval (Admin only)\nExample: `!pc interval 300`",
        inline=False
    )
    
    embed.add_field(
        name="!pc check",
        value="Manually check for new listings (Admin only)",
        inline=False
    )
    
    embed.add_field(
        name="!pc reset",
        value="Reset cache (Admin only)",
        inline=False
    )
    
    embed.add_field(
        name="!pc help",
        value="Show this help message",
        inline=False
    )
    
    embed.set_footer(text="Commands marked (Admin only) require Administrator permission")
    
    await ctx.send(embed=embed)


def main():
    """Main entry point."""
    # Get bot token from environment variable
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        print("❌ Error: DISCORD_BOT_TOKEN environment variable not set!")
        print("\nPlease set your Discord bot token:")
        print("  Linux/Mac: export DISCORD_BOT_TOKEN='your_token_here'")
        print("  Windows: set DISCORD_BOT_TOKEN=your_token_here")
        print("\nOr create a .env file with:")
        print("  DISCORD_BOT_TOKEN=your_token_here")
        return
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        print("❌ Error: Invalid Discord bot token!")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")


if __name__ == "__main__":
    main()
