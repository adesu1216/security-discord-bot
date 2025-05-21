import discord
from discord.ext import commands
from discord import app_commands

class Channel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rebuild_channel", description="指定チャンネルを削除し再構築します（管理者専用）")
    @app_commands.describe(channel="再構築するチャンネル")
    async def rebuild_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 管理者権限が必要です。", ephemeral=True)
            return

        try:
            # チャンネル情報保存
            name = channel.name
            category = channel.category
            position = channel.position
            topic = channel.topic
            overwrites = channel.overwrites

            # チャンネル削除
            await channel.delete(reason=f"再構築 by {interaction.user}")

            # チャンネル再作成
            new_channel = await interaction.guild.create_text_channel(
                name=name,
                category=category,
                position=position,
                topic=topic,
                overwrites=overwrites
            )

            await interaction.response.send_message(
                f"🔁 チャンネル `{name}` を再構築しました → {new_channel.mention}",
                ephemeral=False
            )

        except Exception as e:
            await interaction.response.send_message(f"❌ エラーが発生しました: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Channel(bot))


