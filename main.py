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
from gbook_html import GBookHtml

config_settings = loader("conf.txt")
client_token = config_settings["client_token"]
mining_length = int(config_settings["mining_length"])

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
    global mining_length
    print("mining active")
    while True:
        miners = get_mining_members(ref_client)
        await asyncio.sleep(mining_length)
        for fin_miner in get_mining_members(ref_client):
            if fin_miner in miners:
                await give_coin(fin_miner)


async def message_splitting(bot_msg, origin_msg):
    if len(bot_msg) >= 2000:
        times_to_split = floor(len(bot_msg) / 2000)
        for x in range(times_to_split):
            if x == 0:
                await origin_msg.channel.send(bot_msg[0:1999])
            start_index = 2000
            end_index = 3999
            if end_index > len(bot_msg):
                end_index = len(bot_msg) - 1
                await origin_msg.channel.send(bot_msg[start_index:end_index])
                return
            await origin_msg.channel.send(bot_msg[start_index:end_index])
            start_index += 2000
            end_index += 2000
        return


class MyClient(discord.Client):
    async def on_ready(self):
        print("Discord client started")
        self.loop.create_task(mining(self))
        self.loop.create_task(GBookHtml(self, mining_length).run())

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

        # debating on taking this command out and just use web server
        # to display every ones results
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
                await message_splitting(msg, message)
            await message.channel.send(msg)

        if "gbuy" in message.content:
            db = TinyDB('db.json')
            cursor = Query()
            userid = message.author.id
            guild = self.get_guild(799810866966298685)
            current_currency = 0

            try:
                store_product = message.content.split()[1]
                store_product_name = message.content.split()[2]
            except:
                pass

            try:
                current_currency = float(db.get(cursor.userid == userid)["wallet"])
            except:
                await message.channel.send("Do you even have a wallet?")

            # buying a custom role
            # enforces only one role per user ( strips all roles and applys the bought one. )
            if store_product == "role":
                if ( current_currency < 3  ):
                    await message.channel.send("Insufficient funds.")
                role = await guild.create_role(name=store_product_name, hoist=True)

                if len(message.author.roles) > 1:
                    for pre_existing_roles in message.author.roles[1:]:
                        await message.author.remove_roles(pre_existing_roles)

                await message.author.add_roles(role)
                return

            if store_product == "color":
                if ( current_currency < 7 ):
                    await message.channel.send("Insufficient funds.")
                role = message.author.roles[1]
                await role.edit(colour=discord.Colour(int(store_product_name, 0)))
                return

            if store_product == "menu":
                await message.channel.send("``` menu:\n\tgbuy role [custome name] - seperates you from other users and get a custom name than you can color. WARNING you will lose original color and will have to buy again\n\tgbuy color [0x00FF00] - set your username color to anything in a 3 byte hex value```")    
                return
                
            await message.channel.send("command gbuy\n\tex: gbuy menu\n\tex: gbuy role MYCUSTOMROLE\n\tex: gbuy color 0xFF00FF")
            
client = MyClient()
client.run(client_token)

