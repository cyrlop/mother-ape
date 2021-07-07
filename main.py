import os
import discord
import asyncio

import stock_utils
import reddit_utils


class Config:
    discord_bot_token = os.environ.get("DISCORD_BOT_TOKEN")
    main_commands = ["Hey Mother,", "!mum"]

    commands = {
        "help": {
            "description": "Invoke this help.",
            "usage": "Hey Mother, help",
            "examples": [],
        },
        "gimme": {
            "description": (
                "Gives data about a stonk. "
                "You can specify as many Yahoo finance API fields as you want."
            ),
            "usage": "Hey Mother, gimme <TICKER> <FIELDS:optional>",
            "examples": [
                "Hey Mother, gimme GME",
                "Hey Mother, gimme GME dayLow dayHigh",
            ],
        },
        "in_moass": {
            "description": "Ask Mother ape if we are in the MOASS.",
            "usage": "Hey Mother, are we in the MOASS?",
            "examples": [],
        },
        "kirby_god": {
            "description": "Ask something the the Kirby god.",
            "usage": "Hey Mother, ask Kirby: <QUESTION>",
            "examples": ["Hey Mother, ask Kirby: Do you like trains?"],
        },
        "superstonk": {
            "description": "Gather r/Superstonk data",
            "usage": "Hey Mother, <SORTING> <CATEGORY>",
            "examples": ["Hey Mother, latest DD"],
        },
    }

    commands_starts = {
        "help": "help",
        "gimme": "gimme",
        "in_moass": "in_moass",
        "are we in the moass": "in_moass",
        "is the moass happening now": "in_moass",
        "kirby_god": "kirby_god",
        "ask kirby:": "kirby_god",
        "ask god:": "kirby_god",
        "latest dd": "superstonk",
    }

    static_answers = {None: "Ook, ook ook."}

    def set_initial_names(self, client):
        # Store initial bot nickname for each guild
        self.initial_names = {
            guild: guild.get_member(client.user.id).display_name
            for guild in client.guilds
        }


class Client(discord.Client):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.config = Config()

    async def on_ready(self):
        self.config.set_initial_names(self)
        self.loop.create_task(self.update_gme_ticker(sec=10))
        print(f"Discord client started and logged on as {self.user}!")

    async def update_gme_ticker(self, sec):
        while True:
            ticker = stock_utils.get_ticker("GME")
            last_price = stock_utils.get_last_price(ticker)
            for guild in self.guilds:
                member = guild.get_member(self.user.id)
                await member.edit(
                    nick=f"{last_price}$ - {self.config.initial_names[guild]}"
                )
            await asyncio.sleep(sec)

    async def on_message(self, message):
        # Don't respond to her own messages
        if message.author == self.user:
            return

        # Don't respond if not called by a main_command
        for main_command in self.config.main_commands:
            if message.content.startswith(main_command):
                text = message.content[len(main_command) :].strip()
                break
        else:
            return

        # Parse text to find command
        for command_start in self.config.commands_starts:
            if text.lower().startswith(command_start):
                command = self.config.commands_starts[command_start]
                text_command = command_start
                text_rest = text[len(command_start) :].strip()
                break
        else:
            command = None

        # COMMAND: one to one hard coded answers
        if command in self.config.static_answers:
            response = self.config.static_answers[command]
            await message.channel.send(response)
            return

        # COMMAND: help
        elif command == "help":
            embed = discord.Embed(title="Ape mother - Help", color=0x26C0EB)

            commands_md_joined = " / ".join(
                [f"`{c}`" for c in self.config.main_commands]
            )
            embed.add_field(
                name="How to invoke the Mother ape?",
                value=f"Use one of the following commands: {commands_md_joined} followed by a proper trigger and parameters",
                inline=True,
            )

            for command, command_dict in self.config.commands.items():
                commands_starts = [
                    k for k, v in self.config.commands_starts.items() if v == command
                ]

                value = command_dict["description"]
                value += "\nCan be triggered by the following:"
                for command_start in commands_starts:
                    value += f"\n - `{command_start}`"

                value += f"\nUsage: `{command_dict['usage']}`"

                if len(command_dict["examples"]) > 0:
                    value += "\nExamples:"
                    for example in command_dict["examples"]:
                        value += f"\n - `{example}`"

                embed.add_field(
                    name=f"🚩 {command}",
                    value=value,
                    inline=False,
                )
            await message.channel.send(embed=embed)
            return

        # COMMAND: gimme --> Stonk data
        elif command == "gimme":
            data = text_rest.split(None, 1)
            ticker_symbol = data[0]

            if len(data) > 1:
                params = data[1].split()
            else:
                params = ["regularMarketPrice", "dayLow", "dayHigh"]

            # Get data
            ticker = stock_utils.get_ticker(ticker_symbol)

            if len(ticker.info) < 2:
                response = "Ticker symbol not found"
                await message.channel.send(response)
                return

            # Build embed response
            title = f"{ticker.info['symbol']}"
            if ticker.info.get("shortName") is not None:
                title += f" - {ticker.info['shortName']}"

            embed = discord.Embed(title=title, color=0x26C0EB)

            if ticker.info.get("website") is not None:
                embed.url = ticker.info["website"]

            if ticker.info.get("logo_url") is not None:
                embed.set_image(url=ticker.info["logo_url"])

            for param in params:
                if ticker.info.get(param) is not None:
                    embed.add_field(
                        name=stock_utils.camel_to_sentence(param),
                        value=ticker.info.get(param, "Not found"),
                        inline=True,
                    )

            await message.channel.send(embed=embed)
            return

        # COMMAND: in_moass
        elif command == "in_moass":
            ticker = stock_utils.get_ticker("GME")
            last_price = stock_utils.get_last_price(ticker)
            if last_price >= 10000:
                response = f"Yes!"
            else:
                response = f"No."
            await message.channel.send(response)
            return

        # COMMAND: kirby_god
        elif command == "kirby_god":
            response = f"Kirby god: {text_rest}"
            await message.channel.send(response)
            return

        # COMMAND: superstonk
        elif command == "superstonk":
            try:
                sub = "Superstonk"
                if text_command == "latest dd":
                    flair = "DD 👨‍🔬"
                else:
                    flair = "DD 👨‍🔬"
                latest_posts = reddit_utils.get_latest_posts_by_flair(
                    sub=sub, flair=flair, limit=10
                )
                embed = discord.Embed(
                    title=f"Latest {flair} on r/{sub}", color=0xB01010
                )
                embed.url = f"https://www.reddit.com/r/{sub}"

                for post in latest_posts:
                    embed_data = reddit_utils.get_post_embed_field_data(post["data"])
                    embed.add_field(**embed_data)

                await message.channel.send(embed=embed)
                return

            except Exception as e:
                await message.channel.send(f"```{e}```")
                return


def get_intents():
    intents = discord.Intents.default()
    intents.typing = False
    intents.presences = False
    intents.messages = True
    intents.guilds = True
    intents.reactions = True
    return intents


client = Client(intents=get_intents())
client.run(client.config.discord_bot_token)
