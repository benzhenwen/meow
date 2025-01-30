import disnake
from disnake.ext import commands

import sqlite_handler

import math
import random
import asyncio
from collections import OrderedDict
from collections import deque

# Fetch the token from token.txt
try:
    with open("token.txt", "r") as token_file:
        TOKEN = token_file.read().strip()
except Exception as e:
    print(f"Error reading token.txt: {e}")
    exit(1)

# Define intents
intents = disnake.Intents.default()
intents.messages = True  # Enable message-related intents
intents.message_content = True  # Enable access to message content
intents.guilds = True  # Ensure the bot can interact with guilds
intents.guild_scheduled_events = True  # Enable slash command interactions
intents.reactions = True  # Enable reaction tracking
intents.members = True  # Helps with fetching full member data

# Set up the bot
bot = commands.InteractionBot(intents=intents, max_messages=None)

# Cache for custom emojis
emoji_cache = {}
def cache_emoji(guild_id, emoji_id, emoji_name):
    if guild_id is None:
        # Handle default emojis
        emoji_cache[emoji_name] = emoji_id
        try:
            print(f"Cached default emoji '{emoji_name}': {emoji_id}")
        except UnicodeEncodeError:
            print(f"Cached default emoji '{emoji_name}' (unicode print raw): {repr(emoji_id)}")
        return

    source_guild = disnake.utils.get(bot.guilds, id=guild_id)
    if source_guild:
        emoji = disnake.utils.get(source_guild.emojis, id=emoji_id)
        if emoji:
            emoji_cache[emoji_name] = emoji
            try:
                print(f"Cached emoji '{emoji_name}': {emoji}")
            except UnicodeEncodeError:
                print(f"Cached emoji '{emoji_name}' (unicode print raw): {repr(emoji)}")
        else:
            print(f"Custom emoji '{emoji_name}' not found in the source guild.")
    else:
        print(f"Source guild with ID {guild_id} not found.")

# democracy message cache
class LimitedMessageCache(OrderedDict):
    def __init__(self, max_size=5000):
        super().__init__()
        self.max_size = max_size

    def add(self, message: disnake.Message):
        if len(self) >= self.max_size:
            self.popitem(last=False)  # Remove the oldest message
        self[message.id] = message

message_cache: LimitedMessageCache = None

# ready
@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

    # Cache emojis on startup
    cache_emoji(1236977197923831860, 1238555945185972224, "frank")      # frank
    cache_emoji(1040556771489611881, 1189037275724656801, "fen_bonk")   # fen_bonk
    cache_emoji(None, "\u2705", "white_check_mark")                     # white_check_mark
    cache_emoji(None, "\u274c", "x")                                    # x
    cache_emoji(None, "\uD83E\uDEC3", "pregnant_man")                   # pregnant_man

    # max size that each guild gets for message cache
    global message_cache
    message_cache = LimitedMessageCache(max_size=math.floor(40000 / len(bot.guilds)))
    print(f"Max cached messages per server ({len(bot.guilds)}) is {message_cache.max_size}")

    for guild in bot.guilds:
        sqlite_handler.setup_tables_for_server(guild.id)
        print("setup server database: " + str(guild.id) + " - " + guild.name)

        max_cache_per_channel = min(250, math.floor((message_cache.max_size / len(guild.channels) / 2)))
        print(f"limiting cache per channel size to: {max_cache_per_channel}")

        for channel in guild.channels:
            try:
                count = 0
                async for message in channel.history(limit=max_cache_per_channel):  # Adjust limit as needed
                    if message:
                        message_cache.add(message) # Cache messages
                        count += 1
                        if guild.id == 1040556771489611881 and channel.id == 1333441107027169371 and message.reactions:
                            await check_message_reactions(message)
                print(f"Cached {count} recent messages for {guild.name} - {channel.name}")
            except disnake.Forbidden as e:
                pass # no access to channel
            except AttributeError as e:
                pass # channel has no history
            except Exception as e:
                print(f"Error fetching message history: {e}")
        
    print("Setup Complete")

# guild setup stuff with db
@bot.event
async def on_guild_join(guild: disnake.Guild):
    await sqlite_handler.setup_tables_for_server(guild.id)

@bot.event
async def on_message(message: disnake.Message):
    message_cache.add(message)

    meow_count = message.content.lower().count("meow") if message.content else 0

    # bot has opinions 
    if message.guild.id == 1040556771489611881 and message.channel.id == 1333441107027169371 and message.content:
        if meow_count > 0 or ":3" in message.content.lower():
            try:
                await message.add_reaction(emoji_cache["white_check_mark"])
            except Exception as e:
                pass
        
        if "woof" in message.content.lower() or "chirr" in message.content.lower():
            try:
                await message.add_reaction(emoji_cache["x"])
            except Exception as e:
                pass

    # do not respond to bots
    if message.author.bot:
        return 

    # meow and nya~
    if meow_count > 0:
        sqlite_handler.add_meows(message.guild.id, message.author.id, meow_count)
        if random.random() < sqlite_handler.query_setting_value(message.guild.id, "meowchance"):
            sqlite_handler.add_meows(message.guild.id, bot.user.id, 1)
            try:
                await message.channel.send("meow")
            except Exception as e:
                print(f"Failed to meow :( am sad: {e}")
            
    if message.content and ":3" in message.content.lower():
        if random.random() < sqlite_handler.query_setting_value(message.guild.id, "nyachance"):
            try:
                await message.channel.send(":3")
            except Exception as e:
                print(f"Failed to nya~~~~ :( am sad: {e}")


    # Emoji reaction after mention
    if bot.user.mentioned_in(message):
        try:
            await message.add_reaction(emoji_cache["frank"])
        except Exception as e:
            print(f"Failed to add reaction frank after mention: {e}")
        
    # rob pregananant 
    if message.author.id == 1028450411012706314 and random.random() < 0.02:
        try:
            await message.add_reaction(emoji_cache["pregnant_man"])
        except Exception as e:
            print(f"Failed to add reaction pregnant_man: {e}")

    # crafty hammer 
    if message.author.id == 590979003431649283 and random.random() < 0.02:
        try:
            await message.add_reaction(emoji_cache["fen_bonk"])
        except Exception as e:
            print(f"Failed to add reaction fen_bonk: {e}")

# whenever you edit a message
@bot.event
async def on_raw_message_edit(payload: disnake.RawMessageUpdateEvent):
    # fetch the channel
    guild = disnake.utils.get(bot.guilds, id=payload.guild_id)
    if not guild:
        return
    channel = guild.get_channel(payload.channel_id)
    if not channel:
        return

    try:
        message = await channel.fetch_message(payload.message_id)
        message_cache[payload.message_id] = message # Cache message
    except disnake.NotFound:
        print(f"Message {payload.message_id} not found in channel history.")
        return
    
    # bot has opinions 
    if message.guild.id == 1040556771489611881 and message.channel.id == 1333441107027169371 and message.content:
        if "meow" in message.content.lower() or ":3" in message.content.lower():
            try:
                await message.add_reaction(emoji_cache["white_check_mark"])
            except Exception as e:
                pass
        else:
            try:
                await message.remove_reaction(emoji_cache["white_check_mark"], member=guild.get_member(1245117054114074724))
            except Exception as e:
                pass
        
        if "woof" in message.content.lower() or "chirr" in message.content.lower():
            try:
                await message.add_reaction(emoji_cache["x"])
            except Exception as e:
                pass
        else:
            try:
                await message.remove_reaction(emoji_cache["x"], member=guild.get_member(1245117054114074724))
            except Exception as e:
                pass


# message delete caching
class DeletedMessageCache:
    def __init__(self, capacity=50):
        self.server_queues = {}
        self.capacity = capacity

    def add_message(self, server_id: int, message: disnake.Message):
        if server_id not in self.server_queues:
            self.server_queues[server_id] = deque(maxlen=self.capacity)
        
        self.server_queues[server_id].append(message)

    def get_messages(self, server_id: int):
        return list[disnake.Message](self.server_queues.get(server_id, []))
    
freedom_queue = DeletedMessageCache()
moderator_queue = DeletedMessageCache()

@bot.event
async def on_raw_message_delete(payload: disnake.RawMessageDeleteEvent):
    # fetch the channel
    guild = disnake.utils.get(bot.guilds, id=payload.guild_id)
    if not guild:
        print(f"Warning: guild not found for message delete")
    channel = guild.get_channel(payload.channel_id)
    if not channel:
        print(f"Warning: channel not for message delete")

    message: disnake.Message = message_cache.get(payload.message_id)
    if message is None:
        try:
            message = await channel.fetch_message(payload.message_id)
            message_cache.add(message) # Cache message
        except disnake.NotFound:
            print(f"Message {payload.message_id} not found in channel history.")
            return
        
    if message.guild and message.author:
        if message.guild.id == 1040556771489611881 and message.channel.id == 1333441107027169371:
            freedom_queue.add_message(message.guild.id, message)
        else:
            moderator_queue.add_message(message.guild.id, message)
    else:
        print("A message was deleted, but the context could not be fully determined.")

# freedom!!!!!
@bot.event
async def on_raw_reaction_add(payload: disnake.RawReactionActionEvent):
    await on_raw_reaction(payload, True)
@bot.event
async def on_raw_reaction_remove(payload: disnake.RawReactionActionEvent):
    await on_raw_reaction(payload, False) 

# cache channel
freedom_channel = None
async def on_raw_reaction(payload: disnake.RawReactionActionEvent, is_adding: bool):
    if payload.guild_id != 1040556771489611881 or payload.channel_id != 1333441107027169371:
        return
    
    global freedom_channel
    if freedom_channel == None:
        # cache the channel
        freedom_guild = disnake.utils.get(bot.guilds, id=1040556771489611881)
        if not freedom_guild:
            print(f"Warning: guild not found for freedom channel caching")
        freedom_channel = freedom_guild.get_channel(1333441107027169371)
        if not freedom_channel:
            print(f"Warning: channel not for freedom channel caching")
        print(f"Freedom channel cached")

    # Retrieve message from cache or fetch from Discord if missing
    message: disnake.Message = message_cache.get(payload.message_id)
    if message is None:
        try:
            message = await freedom_channel.fetch_message(payload.message_id)
            message_cache.add(message) # Cache message
        except disnake.NotFound:
            print(f"Message {payload.message_id} not found in channel history.")
            return
    else: # message is cached, need to update values
        for reaction in message.reactions:
            if str(reaction.emoji) == str(payload.emoji):
                reaction.count += 1 if is_adding else -1
                if reaction.count == 0:
                    reaction.message.reactions.remove(reaction)
                break
        else:
            emo = payload.emoji if payload.emoji.is_custom_emoji else str(payload.emoji)
            dr = disnake.Reaction(message=message, emoji=emo, data={"count":1, "me":False, "emoji":emo})
            message.reactions.append(dr)

    await check_message_reactions(message)

async def check_message_reactions(message: disnake.Message):
    try:
        white_check_count = 0
        x_count = 0

        for reac in message.reactions:
            if reac.emoji == emoji_cache["white_check_mark"]:
                white_check_count = reac.count
            elif reac.emoji == emoji_cache["x"]:
                x_count = reac.count

        # print(f"Checked message: {message.id}, ✅: {white_check_count}, ❌: {x_count}")

        if (x_count - white_check_count) >= 3:
            await message.delete()

    except Exception as e:
        print(f"Failed to delete message: {e}")

# Slash commands
@bot.slash_command(description="How many times has someone meow!")
async def get_meow_count(inter, user: disnake.User = commands.Param(default=None, description="target user"), is_ephemeral: bool = commands.Param(default=True, description="Make the response private")):
    user = user or inter.author  # Default to the user who invoked the command
    meow_count = sqlite_handler.query_meow_value(inter.guild.id, user.id)
    await inter.response.send_message(f"{user.display_name} has meowed {meow_count} times!", ephemeral=is_ephemeral)

# Slash command to display the leaderboard
@bot.slash_command(description="Display the leaderboard of top meowers.")
async def leaderboard(inter, is_ephemeral: bool = commands.Param(default=True, description="Make the response private")):
    server_id = inter.guild.id
    top_meowers = sqlite_handler.get_top_meowers(server_id)

    if not top_meowers:
        await inter.response.send_message("An error occurred, or the server hasn't meowed yet.", ephemeral=True)
        return

    # Fetch all members in parallel
    async def fetch_member(user_id):
        try:
            return await inter.guild.fetch_member(int(user_id))
        except disnake.NotFound:
            return None

    user_ids = [user_id for user_id, _ in top_meowers]
    members = await asyncio.gather(*(fetch_member(user_id) for user_id in user_ids))

    # Build the leaderboard message
    leaderboard_message = "**Meow!! mrrrp mrr mrrow:**\n"
    for idx, (user_id, meow_count) in enumerate(top_meowers, start=1):
        member = members[idx - 1]
        username = member.display_name if member else "unknown"
        leaderboard_message += f"{idx}. {username} - {meow_count}\n"

    await inter.response.send_message(leaderboard_message, ephemeral=is_ephemeral)

class PageEmbed(disnake.ui.View):
    def __init__(self, embeds):
        super().__init__(timeout=None)
        self.embeds = embeds
        self.current_page = 0
        self.max_pages = len(embeds)

    @disnake.ui.button(label="Previous", style=disnake.ButtonStyle.primary)
    async def previous_page(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        else:
            await interaction.response.defer()  # No page change

    @disnake.ui.button(label="Next", style=disnake.ButtonStyle.primary)
    async def next_page(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if self.current_page < self.max_pages - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        else:
            await interaction.response.defer()  # No page change

# Slash command to view the message cache
@bot.slash_command(description="View the deleted message cache for this server.")
async def get_message_cache(inter, is_ephemeral: bool = commands.Param(default=True, description="Make the response private")):

    # Check if the user is the server owner or has the moderator role
    moderator_role_id = 1040564073445720124
    is_server_owner = inter.author.id == inter.guild.owner_id
    has_moderator_role = any(role.id == moderator_role_id for role in inter.author.roles) or inter.author.id == 972654681706889216

    if not (is_server_owner or has_moderator_role):
        await inter.response.send_message("no peeking owo~ (invalid permission)", ephemeral=True)
        return
    
    # queue empty
    deleted_messages = moderator_queue.get_messages(inter.guild.id)
    deleted_messages.reverse()
    if not deleted_messages:
        await inter.response.send_message("The message cache is empty. The bot has likely been reset recently.", ephemeral=True)
        return
    
    # body
    embeds = []
    index = 1
    
    for msg in deleted_messages:
        embed = disnake.Embed(title="Deleted Message ({index}/{len(deleted_messages)})", color=disnake.Color.red())
        embed.add_field(name="Time", value=f"<t:{int(msg.created_at.timestamp())}:f>", inline=True)
        embed.add_field(name="Author", value=f"<@{msg.author.id}>", inline=True)
        embed.add_field(name="Channel", value=f"<#{msg.channel.id}>", inline=True)
        
        if msg.content:
            embed.add_field(name="Content", value=msg.content, inline=False)

        if msg.attachments:
            attachments = ", ".join(attachment.url for attachment in msg.attachments)
            embed.add_field(name="Attachments", value=attachments, inline=False)

        if msg.reactions:
            reactions = ", ".join(str(reaction.emoji)+f" ({reaction.count})" for reaction in msg.reactions)
            embed.add_field(name="Reactions", value=reactions, inline=False)

        embeds.append(embed)
        index += 1

    # Send the first embed with pagination controls
    await inter.response.send_message(embed=embeds[0], view=PageEmbed(embeds), ephemeral=is_ephemeral)


# Slash command to view the message cache
@bot.slash_command(description="View the freedom history.", guild_ids=[1040556771489611881])
async def get_freedom_cache(inter, is_ephemeral: bool = commands.Param(default=True, description="Make the response private")):
    if inter.guild.id != 1040556771489611881 or inter.channel.id != 1333441107027169371:
        await inter.response.send_message("This command cannot be used in this channel.", ephemeral=True)
        return

    # queue empty
    deleted_messages = freedom_queue.get_messages(inter.guild.id)
    deleted_messages.reverse()
    if not deleted_messages:
        await inter.response.send_message("The message cache is empty. The bot has likely been reset recently.", ephemeral=True)
        return
    
    # body
    embeds = []
    index = 1
    
    for msg in deleted_messages:
        embed = disnake.Embed(title=f"Deleted Message ({index}/{len(deleted_messages)})", color=disnake.Color.blue())
        embed.add_field(name="Time", value=f"<t:{int(msg.created_at.timestamp())}:f>", inline=True)
        embed.add_field(name="Author", value=f"<@{msg.author.id}>", inline=True)
        
        if msg.content:
            embed.add_field(name="Content", value=msg.content, inline=False)

        if msg.attachments:
            attachments = ", ".join(attachment.url for attachment in msg.attachments)
            embed.add_field(name="Attachments", value=attachments, inline=False)

        if msg.reactions:
            reactions = ", ".join(str(reaction.emoji)+f" ({reaction.count})" for reaction in msg.reactions)
            embed.add_field(name="Reactions", value=reactions, inline=False)

        embeds.append(embed)
        index += 1

    # Send the first embed with pagination controls
    await inter.response.send_message(embed=embeds[0], view=PageEmbed(embeds), ephemeral=is_ephemeral)



# Run the bot
try:
    sqlite_handler.open_conns()
    bot.run(TOKEN)
finally:
    sqlite_handler.close_conns()
