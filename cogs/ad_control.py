import discord
from discord.ext import commands
from discord import app_commands
import json

CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

class AdControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_ad_channel", description="このチャンネルをリンク許可チャンネルに登録します（管理者専用）")
    async def set_ad_channel(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 管理者権限が必要です。", ephemeral=True)
            return

        config = load_config()
        guild_id = str(interaction.guild.id)
        channel_id = interaction.channel.id

        if guild_id not in config:
            config[guild_id] = {"ad_channels": []}

        if channel_id in config[guild_id]["ad_channels"]:
            await interaction.response.send_message(
                "⚠️ このチャンネルはすでにリンク許可チャンネルとして登録されています。重複登録はできません。",
                ephemeral=True
            )
            return

        config[guild_id]["ad_channels"].append(channel_id)
        save_config(config)
        await interaction.response.send_message("✅ このチャンネルをリンク許可チャンネルとして登録しました。", ephemeral=False)

    @app_commands.command(name="remove_ad_channel", description="このチャンネルのリンク許可を解除します（管理者専用）")
    async def remove_ad_channel(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 管理者権限が必要です。", ephemeral=True)
            return

        config = load_config()
        guild_id = str(interaction.guild.id)
        channel_id = interaction.channel.id

        if guild_id not in config or channel_id not in config[guild_id].get("ad_channels", []):
            await interaction.response.send_message("⚠️ このチャンネルはリンク許可チャンネルに登録されていません。", ephemeral=True)
            return

        config[guild_id]["ad_channels"].remove(channel_id)
        save_config(config)
        await interaction.response.send_message("🗑 このチャンネルをリンク許可リストから削除しました。", ephemeral=False)

    @app_commands.command(name="view_ad_channels", description="リンク許可チャンネル一覧を表示します（管理者専用）")
    async def view_ad_channels(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 管理者専用コマンドです。", ephemeral=True)
            return

        config = load_config()
        guild_id = str(interaction.guild.id)
        ad_channels = config.get(guild_id, {}).get("ad_channels", [])

        if not ad_channels:
            await interaction.response.send_message("📭 登録されているリンク許可チャンネルはありません。", ephemeral=True)
            return

        mentions = [f"<#{cid}>" for cid in ad_channels]
        embed = discord.Embed(
            title="🔗 登録済みリンク許可チャンネル一覧",
            description="\n".join(mentions),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdControl(bot))

