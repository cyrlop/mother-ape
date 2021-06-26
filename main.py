import os
import discord

import stock_utils
import reddit_utils


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
        "superstonk": [
            "latest dd",
        ],
    }


class Client(discord.Client):
    async def on_ready(self):
        print(f"Discord client started and logged on as {self.user}!")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith(config.main_command):
            text = message.content.split(config.main_command, 1)[1].strip()

            # Command: gimme --> Stonk data
            if any([text.lower().startswith(c) for c in config.commands["gimme"]]):
                data = text.split(None, 1)[1].strip().split(None, 1)
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

            # Command: superstonk
            elif any([c in text.lower() for c in config.commands["superstonk"]]):
                try:

                    sub = "Superstonk"
                    flair = "DD 👨‍🔬"
                    latest_posts = reddit_utils.get_latest_posts_by_flair(
                        sub=sub, flair=flair, limit=10
                    )
                    embed = discord.Embed(
                        title=f"Latest {flair} on r/{sub}", color=0xB01010
                    )
                    embed.url = f"https://www.reddit.com/r/{sub}"

                    for post in latest_posts:
                        embed_data = reddit_utils.get_post_embed_field_data(
                            post["data"]
                        )
                        embed.add_field(**embed_data)

                    await message.channel.send(embed=embed)
                    return

                except Exception as e:
                    await message.channel.send(f"```{e}```")
                    return

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
