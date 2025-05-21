import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ✅ ステータス切替タスク
statuses = [
    lambda: discord.Game(name="作成者: あですぅー！(kinakomochi1216)"),
    lambda: discord.Game(name=f"{len(bot.guilds)}個のサーバーで稼働中")
]
status_index = 0

@tasks.loop(seconds=3)
async def update_status():
    global status_index
    await bot.change_presence(activity=statuses[status_index]())
    status_index = (status_index + 1) % len(statuses)

@bot.event
async def on_ready():
    await tree.sync()
    update_status.start()
    print(f"✅ Botログイン成功：{bot.user}")
    print(f"✅ スラッシュコマンド同期完了")

async def load_extensions():
    extensions = [
        "cogs.admin",
        "cogs.moderation",
        "cogs.security",
        "cogs.channel",
        "cogs.ad_control",
        "cogs.report"
    ]
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"🔄 Loaded {ext}")
        except Exception as e:
            print(f"❌ Failed to load {ext}: {e}")

async def main():
    await load_extensions()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())




