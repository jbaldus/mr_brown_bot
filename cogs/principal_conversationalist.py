from discord.ext import commands
import asyncio
from enum import Enum, auto
from dataclasses import dataclass

class Moods(Enum):
  ENCOURAGING = auto()
  DISCIPLINARY = auto()

  def flip(self):
    if self == self.ENCOURAGING:
      return self.DISCIPLINARY
    return self.ENCOURAGING

class State(Enum):
  NONE = auto()
  QUERY_PURPOSE = auto()
  DISPENSE_RESPONSE = auto()
  DISMISSIVE = auto()
  SILENT = auto()

  def next(self):
    v = self.value + 1
    if v > self.SILENT.value:
      v = self.SILENT.value
    return State(v)

@dataclass
class StudentConvo:
  mood: Moods 
  state: State = State.QUERY_PURPOSE

  def next(self):
    self.state = self.state.next()

###############################
class PrincipalConversationalist(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.memory = {}
    self.mood = Moods.ENCOURAGING

  @commands.command(
    description="""
    mood good|bad - Sets Mr. Brown's mood to good|bad
    mood flip     - Toggles Mr. Brown's mood
    mood          - Mr. Brown responds with his current mood
    """
  )
  async def mood(self, ctx, arg=None):
    if arg == None:
      await ctx.send(str(self.mood), delete_after=2.0)
    elif arg.lower() == "good":
      self.mood = Moods.ENCOURAGING
    elif arg.lower() == "bad":
      self.mood = Moods.DISCIPLINARY
    elif arg.lower() == "flip":
      self.mood = self.mood.flip()
    else:
      await ctx.send(f"I'm sorry I don't understand *{ctx.message.content}*", delete_after=5.0)
    await ctx.message.delete(delay=5.0)


  async def _forget_user(self, user):
      await asyncio.sleep(30)
      self.memory.pop(user)


  def is_command(self, message):
    prefixes = self.bot.command_prefix(self.bot, message)
    if message.content.startswith(tuple(prefixes)):
      return True
    return False


  @commands.Cog.listener()
  async def on_message(self, message):
    if message.author == self.bot.user:
      return

    if str(message.channel) != 'principals-office':
      return

    if self.is_command(message):
      return

    name = message.author.nick or message.author.name
    student_convo = self.memory.get(message.author.id, StudentConvo(self.mood))
    
    if student_convo.state == State.QUERY_PURPOSE:
      await message.channel.send(f"Hello, {name}. What are you here for?")
      
    elif student_convo.state == State.DISPENSE_RESPONSE:
      if student_convo.mood == Moods.ENCOURAGING:
        await message.channel.send(f"I believe in you, {name}. I know you can achieve your goals, and that you are a good person with value. I love you. Have a Good Day!")
      elif student_convo.mood == Moods.DISCIPLINARY:
        await message.channel.send(f"I'm very disappointed in you, {name}. I expect better from you. Please do better, and don't do this again. Good day to you!")
      
      
      asyncio.create_task(self._forget_user(message.author.id))
      
    elif student_convo.state == State.DISMISSIVE:
      await message.channel.send('I said, "Good Day!"')

    elif student_convo.state == State.SILENT:
      ''' This should never happen, but in case we get here... '''
      asyncio.create_task(self._forget_user(message.author.id))

    student_convo.next()
    self.memory[message.author.id] = student_convo



  @commands.command(
    description="""
    memory - Dumps the contents of Mr. Brown's Memory
    """
  )
  async def memory(self, ctx, arg=None):
    if arg == None:
      await ctx.send(str(self.memory), delete_after=60.0)
    await ctx.message.delete(delay=5.0)



def setup(bot):
  bot.add_cog(PrincipalConversationalist(bot))
