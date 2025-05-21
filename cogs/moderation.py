import discord
from discord.ext import commands
from discord import app_commands, Interaction
from datetime import timedelta, datetime
import json

WARNINGS_FILE = "warnings.json"

def load_warnings():
    try:
        with open(WARNINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_warnings(warnings):
    with open(WARNINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(warnings, f, indent=2, ensure_ascii=False)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="指定ユーザーに手動で警告を出します（管理者専用）")
    @app_commands.describe(user="警告するユーザー")
    async def warn(self, interaction: Interaction, user: discord.Member):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 管理者権限が必要です。", ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        user_id = str(user.id)

        warnings = load_warnings()
        if guild_id not in warnings:
            warnings[guild_id] = {}

        warnings[guild_id][user_id] = warnings[guild_id].get(user_id, 0) + 1
        save_warnings(warnings)
        count = warnings[guild_id][user_id]

        await interaction.response.send_message(
            f"⚠️ {user.mention} に警告を出しました。現在の警告数：{count}/5"
        )

        if count == 3:
            try:
                until = datetime.utcnow() + timedelta(minutes=1)
                await user.timeout(until, reason="警告3回：一時ミュート")
                await interaction.channel.send(f"⏱ {user.mention} を60秒タイムアウトしました。")
            except Exception as e:
                await interaction.channel.send(f"⚠️ タイムアウト失敗: {e}")

        if count >= 5:
            try:
                await user.ban(reason="警告5回：自動BAN")
                await interaction.channel.send(f"⛔️ {user.mention} をBANしました。")
            except Exception as e:
                await interaction.channel.send(f"❌ BAN失敗: {e}")

    @app_commands.command(name="reset_warnings", description="指定ユーザーの警告数をリセットします（管理者専用）")
    @app_commands.describe(user="リセットするユーザー")
    async def reset_warnings(self, interaction: Interaction, user: discord.Member):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 管理者権限が必要です。", ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        user_id = str(user.id)

        warnings = load_warnings()
        if guild_id in warnings and user_id in warnings[guild_id]:
            del warnings[guild_id][user_id]
            save_warnings(warnings)
            await interaction.response.send_message(f"✅ {user.mention} の警告数をリセットしました。")
        else:
            await interaction.response.send_message(f"ℹ️ {user.mention} は警告を受けていません。", ephemeral=True)

    @app_commands.command(name="log", description="警告されているユーザー一覧を表示します（管理者専用）")
    async def log_warnings(self, interaction: Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 管理者権限が必要です。", ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        warnings = load_warnings()

        if guild_id not in warnings or not warnings[guild_id]:
            await interaction.response.send_message("⚠️ このサーバーには警告されているユーザーはいません。", ephemeral=True)
            return

        embed = discord.Embed(title="📋 警告ユーザー一覧", color=discord.Color.orange())
        for user_id, count in warnings[guild_id].items():
            embed.add_field(name=f"ユーザーID: {user_id}", value=f"警告数: {count}", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
