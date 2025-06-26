from discord.ext import commands
from discord import Member
import discord

class RulesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        try:
            embed = discord.Embed(
                title="📚 Welcome to the Reading Group!",
                description="Here are the rules and how to use the bot:",
                color=discord.Color.teal()
            )

            embed.add_field(
                name="🔷 Core Rules",
                value=(
                    "➤ No belittling — Mocking/discouraging others = instant ban.\n"
                    "➤ Stay on topic — No spam or off-topic posts.\n"
                    "➤ All books welcome — Except comics/manga/webtoons.\n"
                    "➤ No time pressure — Read at your own pace.\n"
                    "➤ Post summaries + ratings when done.\n"
                    "➤ No NSFW content — zero tolerance."
                ),
                inline=False
            )

            embed.add_field(
                name="🤖 Using BookTrackerBot",
                value=(
                    "Use `/add_book` to log a book.\n"
                    "`/update_book`, `/shelf_book`, `/unshelf_book` to track progress.\n"
                    "`/progress` to see your reading stats.\n"
                    "`/genres` to see valid genres.\n"
                    "Admins: `/progress *`, `/download_log`, `/gsheet_sync`"
                ),
                inline=False
            )

            embed.add_field(
                name="⚠️ Spoiler Policy",
                value=(
                    "❌ No intentional spoilers — kick on sight.\n"
                    "✅ Use spoiler tags: `||spoiler||`\n"
                    "✅ Add book title above the spoiler.\n"
                    "💬 Only post spoilers in the spoiler channel."
                ),
                inline=False
            )

            embed.set_footer(text="Let the reading begin! 📖✨")

            await member.send(embed=embed)
        except Exception as e:
            print(f"Failed to send welcome DM to {member}: {e}")

async def setup(bot):
    await bot.add_cog(RulesCog(bot))
