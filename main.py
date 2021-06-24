import os
import discord


class Config:
    command = "Hey Mother, "
    discord_bot_token = os.environ.get("DISCORD_BOT_TOKEN")


config = Config()


class Client(discord.Client):
    async def on_ready(self):
        print(f"Discord client started and logged on as {self.user}!")

    async def on_message(self, message):
        if message.author == self.user:
            return

        data = message.content
        if data.startswith(config.command):
            await message.channel.send("Ook, ook ook.")


def get_intents():
    intents = discord.Intents.default()
    intents.typing = False
    intents.presences = False
    intents.messages = True
    intents.guilds = True
    intents.reactions = True
    return intents


client = Client(intents=get_intents())
client.run(config.discord_bot_token)
