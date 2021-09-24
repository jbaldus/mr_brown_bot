from discord.ext import commands
from keep_alive import keep_alive
import os

def get_prefix(client, message):
  prefixes = ['=', '==']    # sets the prefixes
  if not message.guild:
    prefixes = ['==']   # Only allow '==' as a prefix when in DMs, this is optional
  # Allow users to @mention the bot instead of using a prefix when using a command. 
  return commands.when_mentioned_or(*prefixes)(client, message)


cogs = ['cogs.principal_conversationalist']
bot = commands.Bot(                                   # Create a new bot
  command_prefix=get_prefix,                          # Set the prefix
  description='A bot to help with naughty students',  # Set a description for the bot
  owner_id=os.environ.get("OWNER_ID"),                # Your unique User ID
  case_insensitive=True                               # Make the commands case insensitive
)


@bot.event
async def on_ready():          
  print(f'Logged in as {bot.user.name} - {bot.user.id}')
  for cog in cogs:
    bot.load_extension(cog)
  return


keep_alive()
token = os.environ.get("DISCORD_BOT_SECRET")

bot.run(token, bot=True, reconnect=True)
