import discord
from discord.ext import commands
from discord import app_commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="指定したユーザーをBANします")
    @app_commands.describe(user="BANするユーザー")
    async def ban_user(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("❌ BAN権限がありません。", ephemeral=True)
            return
        try:
            await user.ban(reason=f"Banned by {interaction.user}")
            await interaction.response.send_message(f"✅ {user.mention} をBANしました。", ephemeral=False)
        except Exception as e:
            await interaction.response.send_message(f"❌ BANに失敗しました: {e}", ephemeral=True)

    @app_commands.command(name="unban", description="指定したユーザーをBAN解除します（IDまたは名前#タグで指定可能）")
    @app_commands.describe(identifier="BAN解除するユーザーのID（例：123456789012345678）または名前#タグ（例：test#1234）")
    async def unban_user(self, interaction: discord.Interaction, identifier: str):
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("❌ BAN解除権限がありません。", ephemeral=True)
            return

        try:
            user_to_unban = None

            
            if identifier.isdigit():
                target_id = int(identifier)
                async for ban_entry in interaction.guild.bans():
                    if ban_entry.user.id == target_id:
                        user_to_unban = ban_entry.user
                        break
            
            elif "#" in identifier:
                name, discriminator = identifier.split("#")
                async for ban_entry in interaction.guild.bans():
                    if (ban_entry.user.name == name) and (ban_entry.user.discriminator == discriminator):
                        user_to_unban = ban_entry.user
                        break
            else:
                await interaction.response.send_message("⚠️ 無効な形式です。IDまたは名前#タグで入力してください。", ephemeral=True)
                return

            if user_to_unban:
                await interaction.guild.unban(user_to_unban, reason=f"Unbanned by {interaction.user}")
                await interaction.response.send_message(
                    f"✅ {user_to_unban.mention}（{user_to_unban.name}#{user_to_unban.discriminator}）のBANを解除しました。",
                    ephemeral=False
                )
            else:
                await interaction.response.send_message("❌ 指定されたユーザーはBANリストに見つかりませんでした。", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"❌ BAN解除中にエラーが発生しました: {e}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Admin(bot))





