import disnake
from disnake.ext import commands

def setup(bot):
    bot.add_cog(ExampleCog(bot))
    bot.logger.info("ExampleCog загружен!")

class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="ping", description="Проверка бота на работоспособность")
    async def ping(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(f"Понг! {round(self.bot.latency * 1000)}мс")