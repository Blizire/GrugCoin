# name = grugcoin.py
# auth = Trenton Stiles
# desc = Interactive discord tool that gives you currency based
#        on how long you've been in the server. The currency
#        can allow you to buy perms to disconnect, mute and or
#        even kick members of the server.

# username = await ref_client.fetch_user(fin_miner)
# flask run --host=0.0.0.0

import discord
import asyncio
from tinydb import TinyDB, Query
from tinydb.operations import add, subtract
from random import uniform, choice
from math import floor
from edict import loader


config_settings = loader("conf.txt")
client_token = config_settings["client_token"]


def get_mining_members(client_ref):
    member_maps = []
    members = []
    for channel in client_ref.get_all_channels():
        if isinstance(channel, discord.VoiceChannel):
            if len(channel.voice_states.keys()) > 0:
                member_maps.append(channel.voice_states.keys())

    for member_map in member_maps:
        [members.append(x) for x in member_map]

    return members


def gen_coin_value():
    return uniform(0.0001, 0.0009)


def user_exists(userid):
    db = TinyDB('db.json')
    cursor = Query()
    res = db.search(cursor.userid == userid)
    if len(res) > 0:
        return True
    else:
        return False


async def give_coin(userid, coin_value=gen_coin_value()):
    db = TinyDB('db.json')
    cursor = Query()
    if user_exists(userid):
        db.update(add("wallet", coin_value), cursor.userid == userid)
    else:
        db.insert({"userid": userid, "wallet": coin_value})


async def take_coin(userid, coin_value=0.1):
    db = TinyDB('db.json')
    cursor = Query()
    if user_exists(userid):
        db.update(subtract("wallet", coin_value), cursor.userid == userid)
    else:
        db.insert({"userid": userid, "wallet": coin_value})


async def mining(ref_client):
    mining_length = 60
    print("mining active")
    while True:
        miners = get_mining_members(ref_client)
        await asyncio.sleep(mining_length)
        for fin_miner in get_mining_members(ref_client):
            if fin_miner in miners:
                await give_coin(fin_miner)


class MyClient(discord.Client):

    async def on_ready(self):
        print("Discord client started")
        self.loop.create_task(mining(self))

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        else:
            pass

        if message.author.id == 820669662999478292:
            pass

        if message.content == "gwallet":
            db = TinyDB('db.json')
            cursor = Query()
            userid = message.author.id
            nick = message.author.display_name
            wallet = "0"
            if user_exists(userid):
                wallet = str(db.get(cursor.userid == userid)["wallet"])
            else:
                await give_coin(userid, coin_value=0.000001)
                wallet = str(db.get(cursor.userid == userid)["wallet"])
            msg = "{name} has {val}gc".format(name=nick, val=wallet)
            await message.channel.send(msg)

        if message.content == "gbook":
            # gbook command allows to the ability for users to print
            # everybodys crypto wallet value
            db = TinyDB('db.json')
            msg = ""
            for obj in db.all():
                userid = obj["userid"]
                wallet = obj["wallet"]
                user = await self.fetch_user(userid)
                msg += "```{user} : {wallet}gc```\n".format(user=user, wallet=wallet)
                # this is to protect messages from being to big
                # to send. discord.py will handle rate limiting
                # issues.
                if len(msg) >= 2000:
                    times_to_split = floor(len(msg) / 2000)
                    for x in range(times_to_split):
                        if x == 0:
                            await message.channel.send(msg[0:1999])
                        start_index = 2000
                        end_index = 3999
                        if end_index > len(msg):
                            end_index = len(msg) - 1
                            await message.channel.send(msg[start_index:end_index])
                            return
                        await message.channel.send(msg[start_index:end_index])
                        start_index += 2000
                        end_index += 2000
                    return
            await message.channel.send(msg)

        """
        if "ggamble" in message.content:
            msg = ""
            try:
                msg = message.content.split()
                msg_len = len(msg)
                if msg_len < 2 or msg_len > 2:
                    await message.channel.send("ggamble\ncommand to play the bot in rock paper scissors to win 0.15gc or lose 0.1gc\nexample:\nggamble rock")
                    return
        
            except:
                return
            msg = message.content.split()
            plays = ["rock", "paper", "scissors"]
            bot_choice = choice(plays)
            player_choice = msg[1]
            userid = message.author.id
            if player_choice not in plays:
                await message.channel.send("Your choice must be rock paper or scissors!!!")
            else:
                if player_choice == "rock":
                    if bot_choice == "rock":
                        await message.channel.send("YOU TIE")
                    if bot_choice == "paper":
                        await message.channel.send("YOU LOSE")
                        await take_coin(userid, 0.1)
                    if bot_choice == "scissors":
                        await give_coin(userid, 0.15)
                        await message.channel.send("YOU WIN")
                if player_choice == "paper":
                    if bot_choice == "paper":
                        await message.channel.send("YOU TIE")
                    if bot_choice == "scissors":
                        await take_coin(userid, 0.1)
                        await message.channel.send("YOU LOSE")
                    if bot_choice == "rock":
                        await give_coin(userid, 0.15)
                        await message.channel.send("YOU WIN")
                if player_choice == "scissors":
                    if bot_choice == "scissors":
                        await message.channel.send("YOU TIE")
                    if bot_choice == "rock":
                        await take_coin(userid, 0.1)
                        await message.channel.send("YOU LOSE")
                    if bot_choice == "paper":
                        await give_coin(userid, 0.15)
                        await message.channel.send("YOU WIN")
                await message.channel.send("Bot picked {choice}".format(choice=bot_choice))
        """



client = MyClient()
client.run(client_token)

