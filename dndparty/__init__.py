from .dndparty import DndParty

async def setup(bot):
    await bot.add_cog(DndParty(bot))
