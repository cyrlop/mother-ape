import os
import discord

import stock_utils
import reddit_utils


class Config:
    discord_bot_token = os.environ.get("DISCORD_BOT_TOKEN")
    main_commands = ["Hey Mother, ", "!mum"]

    commands_starts = {
        "gimme": "gimme",
        "are we in the moass": "in_moass",
        "is the moass happening now": "in_moass",
        "ask kirby:": "kirby_god",
        "ask god:": "kirby_god",
        "latest dd": "superstonk",
    }

    static_answers = {None: "Ook, ook ook."}


class Client(discord.Client):
    async def on_ready(self):
        print(f"Discord client started and logged on as {self.user}!")

    async def on_message(self, message):
        # Don't respond to her own messages
        if message.author == self.user:
            return

        # Don't respond if not called by a main_command
        for main_command in config.main_commands:
            if message.content.startswith(main_command):
                text = message.content[len(main_command):].strip()
                break
        else:
            return

        # Parse text to find command
        for command_start in config.commands_starts:
            if text.lower().startswith(command_start):
                command = config.commands_starts[command_start]
                text_command = command_start
                text_rest = text[len(command_start) :].strip()
                break
        else:
            command = None

        # COMMAND: one to one hard coded answers
        if command in config.static_answers:
            response = config.static_answers[command]
            await message.channel.send(response)
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
            kirby_question = text_rest.split(":", 1)[1].strip()
            response = f"Kirby god: {kirby_question}"
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


config = Config()
client = Client(intents=get_intents())
client.run(config.discord_bot_token)
