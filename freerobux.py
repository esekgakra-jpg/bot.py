import discord
from discord.ext import commands

Intents = discord.Intents.default()
Intents.members = True 
Intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=Intents)

warned_users = {}

EXEMPT_ROLES = [1350172437291208754, 1329362352784539749]
EXEMPT_USERS = [1328697094550327366, 1416429825253572638, 430779566747811843]

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} sistemi korumaya hazır!')

@bot.event
async def on_message(message):
    if message.author.bot or message.guild is None:
        return

    if message.author.id in EXEMPT_USERS:
        await bot.process_commands(message)
        return

    user_roles = [role.id for role in message.author.roles]
    is_exempt = False
    for role_id in EXEMPT_ROLES:
        if role_id in user_roles:
            is_exempt = True
            break
    
    if is_exempt:
        await bot.process_commands(message)
        return

    content = message.content.lower()
    user_id = message.author.id
    is_violation = False
    
    if "raid" in content:
        is_violation = True
    elif "@everyone" in message.content or "@here" in message.content:
        is_violation = True
    elif "http://" in content or "https://" in content or "discord.gg/" in content:
        is_violation = True

    if is_violation:
        if user_id in warned_users:
            try:
                await message.author.edit(roles=[])
                await message.channel.set_permissions(message.author, send_messages=False)
                await message.channel.send(f"⚠️ {message.author.mention}, LOL FUCKING L RAIDER LIL BOZO")
                del warned_users[user_id]
            except discord.Forbidden:
                await message.channel.send("Error:404")
        else:
            warned_users[user_id] = True
            await message.channel.send(f"⚠️ {message.author.mention}, Don't Say That Word, Tag Everyone or Post Links!", delete_after=10)

    await bot.process_commands(message)

bot.run('MTM0MDc0MjM0ODE3NDI2NjUxMA.GAH3Ug.yYj2DlIe5gGAf7ygEeN-xmaIp4RYNVrFzDNjrk')
