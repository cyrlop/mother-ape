import os
import discord

import stock_utils


class Config:
    discord_bot_token = os.environ.get("DISCORD_BOT_TOKEN")
    main_command = "Hey Mother, "
    commands = {
        "gimme": ["gimme"],
        "in_moass": ["are we in the moass", "is the moass happening now"],
        "kirby_god": [
            "ask kirby:",
            "ask god:",
            "demande à kirby :",
            "demande à dieu :",
        ],
    }


class Client(discord.Client):
    async def on_ready(self):
        print(f"Discord client started and logged on as {self.user}!")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith(config.main_command):
            text = message.content.split(config.main_command)[1].strip()

            # Command: gimme
            if any([text.lower().startswith(c) for c in config.commands["gimme"]]):
                data = text.split()[1].strip().split(None, 1)
                ticker_symbol = data[0]

                if len(data) > 1:
                    params = data[1]
                    print(params)
                    # TODO: implement different outputs depending on params

                ticker = stock_utils.get_ticker(ticker_symbol)
                last_price = stock_utils.get_last_price(ticker)
                response = f"{last_price}$"

            # Command: in_moass
            elif any([c in text.lower() for c in config.commands["in_moass"]]):
                ticker = stock_utils.get_ticker("GME")
                last_price = stock_utils.get_last_price(ticker)
                if last_price >= 10000:
                    response = f"Yes!"
                else:
                    response = f"No."

            # Command: kirby_god
            elif any([c in text.lower() for c in config.commands["kirby_god"]]):
                kirby_question = text.split(":", 1)[1].strip()
                response = f"Kirby god: {kirby_question}"

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
