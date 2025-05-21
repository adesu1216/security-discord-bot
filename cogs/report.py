import discord
from discord.ext import commands
from discord import app_commands, Interaction
import json
import os
from datetime import timedelta, datetime

REPORT_FILE = "report_channel_config.json"

# 通報チャンネル設定の読み書き
def load_report_channels():
    try:
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"report_channels": {}}

def save_report_channels(data):
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 通報チャンネル作成
    @app_commands.command(name="craft_report_channel", description="通報チャンネルを自動作成します（管理者専用）")
    async def craft_channel(self, interaction: Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 管理者権限が必要です。", ephemeral=True)
            return

        guild = interaction.guild
        existing = discord.utils.get(guild.text_channels, name="✍️-通報ログ")
        if existing:
            await interaction.response.send_message(f"⚠️ すでに存在しています: {existing.mention}", ephemeral=True)
            return

        channel = await guild.create_text_channel(name="✍️-通報ログ")
        config = load_report_channels()
        config["report_channels"][str(guild.id)] = channel.id
        save_report_channels(config)

        await interaction.response.send_message(f"✅ 通報チャンネルを作成しました: {channel.mention}", ephemeral=False)

    # 通報機能
    @app_commands.command(name="report", description="ユーザーを通報します")
    @app_commands.describe(user="通報するユーザー", reason="通報理由")
    async def report(self, interaction: Interaction, user: discord.Member, reason: str):
        config = load_report_channels()
        channel_id = config["report_channels"].get(str(interaction.guild.id))

        if not channel_id:
            await interaction.response.send_message("⚠️ 通報チャンネルが設定されていません。管理者に連絡してください。", ephemeral=True)
            return

        try:
            report_channel = interaction.guild.get_channel(channel_id)
            embed = discord.Embed(title="⚡️ 通報", color=discord.Color.red())
            embed.add_field(name="通報者", value=interaction.user.mention, inline=False)
            embed.add_field(name="対象ユーザー", value=user.mention, inline=False)
            embed.add_field(name="理由", value=reason, inline=False)
            await report_channel.send(embed=embed)
            await interaction.response.send_message("✅ 通報が送信されました。", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ エラーが発生しました: {e}", ephemeral=True)

    # ミュート機能
    @app_commands.command(name="mute", description="指定ユーザーを一定時間ミュートします（例：/mute @ユーザー 20）")
    @app_commands.describe(user="ミュートするユーザー", minutes="ミュート時間（分）")
    async def mute(self, interaction: Interaction, user: discord.Member, minutes: int):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ ミュート権限がありません。", ephemeral=True)
            return

        if user.timed_out_until and user.timed_out_until > discord.utils.utcnow():
            await interaction.response.send_message(f"⚠️ {user.mention} はすでにミュートされています。", ephemeral=True)
            return

        until = discord.utils.utcnow() + timedelta(minutes=minutes)

        try:
            await user.timeout(until, reason=f"{minutes}分間のミュート by {interaction.user}")
            await interaction.response.send_message(f"🔇 {user.mention} を {minutes} 分間ミュートしました。", ephemeral=False)
        except Exception as e:
            await interaction.response.send_message(f"❌ ミュートに失敗しました: {e}", ephemeral=True)

    # アンミュート機能
    @app_commands.command(name="unmute", description="指定ユーザーのミュートを解除します（管理者専用）")
    @app_commands.describe(user="ミュート解除するユーザー")
    async def unmute(self, interaction: Interaction, user: discord.Member):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ ミュート解除権限がありません。", ephemeral=True)
            return

        if not user.timed_out_until or user.timed_out_until <= discord.utils.utcnow():
            await interaction.response.send_message(f"ℹ️ {user.mention} は現在ミュートされていません。", ephemeral=True)
            return

        try:
            await user.timeout(None, reason="手動でミュート解除")
            await interaction.response.send_message(f"🔊 {user.mention} のミュートを解除しました。", ephemeral=False)
        except Exception as e:
            await interaction.response.send_message(f"❌ ミュート解除に失敗しました: {e}", ephemeral=True)

# 登録
async def setup(bot):
    await bot.add_cog(Report(bot))
