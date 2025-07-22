import discord
from redbot.core import commands
from redbot.core.bot import Red
from discord.ui import View, Button


class PartyView(View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Join Party", style=discord.ButtonStyle.green, custom_id="join_party", row=0)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        user_id = user.id

        if user_id in self.cog.party:
            await interaction.response.send_message("You're already in the party, chill.", ephemeral=True)
        elif len(self.cog.party) >= self.cog.party_limit:
            await interaction.response.send_message("Sorry, party is full. Try again later. Or eliminate someone.", ephemeral=True)
        else:
            self.cog.party[user_id] = user
            embed = self.cog.generate_party_embed(interaction.guild)
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Abandon Party", style=discord.ButtonStyle.red, custom_id="abandon_party", row=0)
    async def abandon(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        user_id = user.id

        if user_id in self.cog.party:
            del self.cog.party[user_id]
            embed = self.cog.generate_party_embed(interaction.guild)
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message("You weren’t even in the party... nice try, shadow-dweller.", ephemeral=True)


class DndParty(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.party = {}
        self.party_limit = 6

    def generate_party_embed(self, guild):
        embed = discord.Embed(
            title=f"DND Party: {len(self.party)}/{self.party_limit}",
            description="Current adventurers:",
            color=discord.Color.dark_purple()
        )
        if self.party:
            for member in self.party.values():
                avatar_url = member.display_avatar.url
                embed.add_field(
                    name=member.display_name,
                    value=f"[View Avatar]({avatar_url})",
                    inline=True
                )
        else:
            embed.description = "No one has joined the party yet..."
        return embed

    @commands.hybrid_command(name="createparty")
    @commands.guild_only()
    async def createparty(self, ctx: commands.Context, size: int = 6):
        """Creates the party sign-up message with buttons.
        Use /createparty size:<number> to set the max size (default: 6).
        """
        if size < 1 or size > 20:
            await ctx.send("Party size must be between 1 and 20. Don’t get greedy.")
            return

        self.party.clear()
        self.party_limit = size
        view = PartyView(self)
        embed = self.generate_party_embed(ctx.guild)
        await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(name="clearparty")
    @commands.guild_only()
    async def clearparty(self, ctx: commands.Context):
        """Clears the current party list."""
        self.party.clear()
        await ctx.send("The party has been cleared. Time to assemble a new crew.")
