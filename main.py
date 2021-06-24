import os
import discord

import stock_utils


class Config:
    main_command = "Hey Mother, "
    discord_bot_token = os.environ.get("DISCORD_BOT_TOKEN")


class Client(discord.Client):
    async def on_ready(self):
        print(f"Discord client started and logged on as {self.user}!")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith(config.main_command):
            text = message.content.split(config.main_command)[1].strip()

            if text.startswith("gimme"):
                data = text.split("gimme")[1].strip().split(None, 1)
                ticker_symbol = data[0]

                if len(data) > 1:
                    params = data[1]
                    print(params)
                    # TODO: implement different outputs depending on params

                ticker = stock_utils.get_ticker(ticker_symbol)
                last_price = stock_utils.get_last_price(ticker)
                response = f"{last_price}$"

            else:
                response = "Ook, ook ook."

            await message.channel.send(response)


def get_intents():
    intents = discord.Intents.default()
    intents.typing = False
    intents.presences = False
    intents.messages = True
    intents.guilds = True
    intents.reactions = True
    return intents


config = Config()
client = Client(intents=get_intents())
client.run(config.discord_bot_token)
