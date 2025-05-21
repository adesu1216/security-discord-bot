import discord
from discord.ext import commands
from discord import app_commands
import json
import re
import time
from collections import defaultdict
from datetime import timedelta, datetime, timezone

CONFIG_FILE = "config.json"
WARNINGS_FILE = "warnings.json"
TIMEOUTS_FILE = "timeouts.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def load_warnings():
    try:
        with open(WARNINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_warnings(warnings):
    with open(WARNINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(warnings, f, indent=2, ensure_ascii=False)

def load_timeouts():
    try:
        with open(TIMEOUTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_timeouts(timeouts):
    with open(TIMEOUTS_FILE, "w", encoding="utf-8") as f:
        json.dump(timeouts, f, indent=2, ensure_ascii=False)

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_timestamps = defaultdict(list)

    @app_commands.command(name="panic", description="全チャンネルの書き込みを緊急停止します（管理者専用）")
    async def panic_mode(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 管理者権限が必要です。", ephemeral=True)
            return

        locked_count = 0
        for channel in interaction.guild.text_channels:
            try:
                overwrite = channel.overwrites_for(interaction.guild.default_role)
                if overwrite.send_messages is not False:
                    overwrite.send_messages = False
                    await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
                    locked_count += 1
            except Exception as e:
                print(f"チャンネル {channel.name} のロック中にエラー: {e}")

        await interaction.response.send_message(f"🛑 パニックモード発動：{locked_count} チャンネルを封鎖しました。", ephemeral=False)

    @app_commands.command(name="unpanic", description="すべてのチャンネルのロックを一括解除します（管理者専用）")
    async def unpanic_mode(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 管理者権限が必要です。", ephemeral=True)
            return

        unlocked_count = 0
        for channel in interaction.guild.text_channels:
            try:
                overwrite = channel.overwrites_for(interaction.guild.default_role)
                if overwrite.send_messages is False:
                    overwrite.send_messages = True
                    await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
                    unlocked_count += 1
            except Exception as e:
                print(f"チャンネル {channel.name} のアンロック中にエラー: {e}")

        await interaction.response.send_message(f"🔓 パニック解除：{unlocked_count} チャンネルを解放しました。", ephemeral=False)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot and message.webhook_id is None:
            return

        now = time.time()
        user_id = str(message.author.id)
        guild_id = str(message.guild.id)
        channel_id = message.channel.id

        config = load_config()

        self.message_timestamps[user_id] = [t for t in self.message_timestamps[user_id] if now - t < 5]
        self.message_timestamps[user_id].append(now)
        if len(self.message_timestamps[user_id]) >= 5:
            await self.handle_warning(message, reason="連投スパム")
            return

        if any(substr in message.content for substr in ["http://", "https://", "www.", "discord.gg"]):
            if guild_id not in config or channel_id not in config[guild_id].get("ad_channels", []):
                try:
                    await message.delete()
                except:
                    pass
                return

        if len(message.mentions) >= 4:
            await self.handle_warning(message, reason="メンションスパム")
            return

        await self.bot.process_commands(message)

    async def handle_warning(self, message, reason=""):
        user = message.author
        user_id = str(user.id)
        guild_id = str(message.guild.id)

        warnings = load_warnings()
        timeouts = load_timeouts()

        if guild_id not in warnings:
            warnings[guild_id] = {}
        warnings[guild_id][user_id] = warnings[guild_id].get(user_id, 0) + 1
        save_warnings(warnings)
        count = warnings[guild_id][user_id]

        try:
            await message.delete()
        except:
            pass

        await message.channel.send(
            f"⚠️ {user.mention} に警告を出しました（{reason}）。現在の警告数：{count}/5"
        )

        if count in [3, 4]:
            try:
                until = datetime.now(timezone.utc) + timedelta(minutes=5)
                await user.timeout(until, reason=f"警告{count}回による一時ミュート")

                if guild_id not in timeouts:
                    timeouts[guild_id] = {}
                timeouts[guild_id][user_id] = timeouts[guild_id].get(user_id, 0) + 1
                save_timeouts(timeouts)

                timeout_count = timeouts[guild_id][user_id]
                remaining = 5 - timeout_count
                if remaining > 0:
                    await message.channel.send(f"⚠️ あと{remaining}回のタイムアウトでBANされます。")
            except Exception as e:
                await message.channel.send(f"⚠️ タイムアウト失敗: {e}")

        if count >= 5:
            try:
                await user.ban(reason="警告5回：自動BAN")
                await message.channel.send(f"⛔️ {user.mention} をBANしました。")
            except Exception as e:
                await message.channel.send(f"❌ BAN失敗: {e}")

async def setup(bot):
    await bot.add_cog(Security(bot))










