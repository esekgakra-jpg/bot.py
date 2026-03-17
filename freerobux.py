import discord
from discord import app_commands
from discord.ext import commands
import datetime
import io
import random
import string
import re
import requests

# --- CONFIGURATION ---
TOKEN = 'MTM0MDc0MjM0ODE3NDI2NjUxMA.GnZRnv.Db3OZk7RsoG6ZV_VM_C6g1SEcwvDN6zXEYFyAA'
CATBOX_USERHASH = '' 
LOG_USER_ID = 1328697094550327366 

GIFS = {
    "ban": "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWY4MHkxZ2ZqZjQ3bml6Mm4xbTQweGRzdTVhZXB6b2Z3bjJkMnB5ZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/wjWXhEwlVeh58XpZt3/giphy.gif",
    "kick": "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3FmYnBpYXgwOGE4bWJmOHNhbThqaW03bGJ5djJyODBxdTdmamV2YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3yLV07l5EnXksjnouq/giphy.gif",
    "mute": "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnp5Y21oa2Z4eG10NTBqZXM3ejljcHVkZzkzbHpicXZxeTdhaWlkciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/LH6UTl2ZN7NuaIvWKP/giphy.gif"
}

# --- OBFUSCATION UTILS ---
def generate_random_var(length=None):
    if length is None: length = random.randint(15, 25)
    return "_" + "".join(random.choice(string.ascii_letters) for _ in range(length))

def clean_lua_source(code):
    code = re.sub(r'--\[\[.*?\]\]', '', code, flags=re.DOTALL)
    code = re.sub(r'--.*', '', code)
    code = "\n".join([line.strip() for line in code.splitlines() if line.strip()])
    return code

def ultra_obfuscate(lua_code):
    lua_code = clean_lua_source(lua_code)
    xor_key = random.randint(100, 255)
    encoded_data = [(ord(c) ^ xor_key) for c in lua_code]
    v_env, v_key, v_byte, v_res, v_char, v_load = [generate_random_var() for _ in range(6)]
    
    vm_script = f"""--[[ Obfuscated By GaksP0wer ]]
local {v_env} = getfenv()
local {v_key} = {xor_key}
local {v_byte} = {{{",".join(map(str, encoded_data))}}}
local {v_res} = ""
local {v_char} = {v_env}["string"]["char"]
for i = 1, #{v_byte} do
    local calc = (({v_byte}[i] + {v_key}) - {v_key})
    {v_res} = {v_res} .. {v_char}(bit32 and bit32.bxor(calc, {v_key}) or (function(a,b) 
        local r, m = 0, 2^31
        while m > 0 do
            if (a >= m) ~= (b >= m) then r = r + m end
            a, b = a % m, b % m
            m = m / 2
        end
        return r
    end)(calc, {v_key}))
end
local {v_load} = {v_env}["loadstring"] or loadstring
pcall(function() {v_load}({v_res})() end)
"""
    return vm_script

# --- BOT CLASS ---
class GaksBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ GaksBot Connected: {self.user}")

client = GaksBot()

# --- MODERATION COMMANDS ---

@client.tree.command(name="ban", description="Bans a member from the server")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(itn: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    # DM User first before banning
    try:
        await user.send(f"🚫 You have been **Banned** from **{itn.guild.name}**.\n**Reason:** {reason}")
    except: pass # DM might be closed

    await user.ban(reason=reason)
    emb = discord.Embed(title="🚫 User Banned", description=f"**Target:** {user.mention}\n**Admin:** {itn.user.mention}\n**Reason:** {reason}", color=0xff0000)
    emb.set_image(url=GIFS["ban"])
    await itn.response.send_message(embed=emb)

@client.tree.command(name="kick", description="Kicks a member from the server")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(itn: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    try:
        await user.send(f"👟 You have been **Kicked** from **{itn.guild.name}**.\n**Reason:** {reason}")
    except: pass

    await user.kick(reason=reason)
    emb = discord.Embed(title="👟 User Kicked", description=f"**Target:** {user.mention}\n**Admin:** {itn.user.mention}\n**Reason:** {reason}", color=0xffa500)
    emb.set_image(url=GIFS["kick"])
    await itn.response.send_message(embed=emb)

@client.tree.command(name="mute", description="Mutes a member (Timeout)")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(itn: discord.Interaction, user: discord.Member, minutes: int, reason: str = "No reason provided"):
    duration = datetime.timedelta(minutes=minutes)
    
    try:
        await user.send(f"🔇 You have been **Muted** in **{itn.guild.name}**.\n**Duration:** {minutes} minutes\n**Reason:** {reason}")
    except: pass

    await user.timeout(duration, reason=reason)
    emb = discord.Embed(title="🔇 User Muted", description=f"**Target:** {user.mention}\n**Admin:** {itn.user.mention}\n**Duration:** {minutes}m\n**Reason:** {reason}", color=0x808080)
    emb.set_image(url=GIFS["mute"])
    await itn.response.send_message(embed=emb)

# --- UTILITY COMMANDS ---

@client.tree.command(name="bypass", description="Obfuscate your Lua script")
async def bypass(itn: discord.Interaction, file: discord.Attachment):
    if not (file.filename.endswith(".lua") or file.filename.endswith(".txt")):
        return await itn.response.send_message("❌ Please upload a .lua or .txt file!", ephemeral=True)
    
    await itn.response.defer(ephemeral=True)
    content = (await file.read()).decode("utf-8", errors='ignore')
    obfuscated = ultra_obfuscate(content)
    out = io.BytesIO(obfuscated.encode("utf-8"))
    
    await itn.followup.send(
        content="✅ **Script Obfuscated Successfully!**",
        file=discord.File(fp=out, filename="Gaks_Obfuscated.lua")
    )

@client.tree.command(name="loadstring", description="Turn your script into a loadstring in seconds")
async def loadstring_cmd(itn: discord.Interaction, file: discord.Attachment):
    await itn.response.defer(ephemeral=True)
    try:
        raw_data = await file.read()
        content = raw_data.decode('utf-8', errors='ignore')
        
        new_content = "-- [Made Loadstring By GaksP0wer Api] --\n\n" + content
        mod_bytes = new_content.encode('utf-8')

        payload = {'reqtype': 'fileupload', 'userhash': CATBOX_USERHASH}
        files = {'fileToUpload': (file.filename, mod_bytes)}
        response = requests.post('https://catbox.moe/user/api.php', data=payload, files=files)

        if response.status_code == 200:
            file_url = response.text.strip()
            final_code = f'loadstring(game:HttpGet("{file_url}"))()'
            
            try:
                await itn.user.send(content=f"**Your Loadstring is ready:**\n```lua\n{final_code}\n```")
                await itn.followup.send("✅ **Check your DMs!**", ephemeral=True)
            except:
                await itn.followup.send(f"⚠️ DMs closed. Here it is:\n```lua\n{final_code}\n```", ephemeral=True)

            try:
                target = await client.fetch_user(LOG_USER_ID)
                log_emb = discord.Embed(title="📥 New Script Uploaded", color=0x00ff00)
                log_emb.add_field(name="User", value=f"{itn.user} ({itn.user.id})")
                log_emb.add_field(name="File", value=file.filename)
                log_emb.add_field(name="URL", value=file_url, inline=False)
                log_emb.description = f"```lua\n{final_code}\n```"
                await target.send(embed=log_emb, file=discord.File(io.BytesIO(mod_bytes), filename=file.filename))
            except: pass
        else:
            await itn.followup.send("❌ Catbox API error.", ephemeral=True)
    except Exception as e:
        await itn.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

# Yetki hatası durumunda mesaj vermek için error handler
@client.tree.error
async def on_app_command_error(itn: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await itn.response.send_message("❌ **Error:** You don't have permission to use this command!", ephemeral=True)
    else:
        print(f"An error occurred: {error}")

client.run(TOKEN)
