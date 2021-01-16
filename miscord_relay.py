#!/usr/local/bin/python3

import os
import discord
from discord import utils
import re
from tinydb import TinyDB, Query
from datetime import datetime

TOKEN_PATH = [d for d in os.listdir() if "TOKEN" in d]
TOKEN = TOKEN_PATH[0].replace("TOKEN", "")

client = discord.Client()

db = TinyDB('./db.json')
User = Query()


def notify_me(message, nick=None):
    if db.search(User.id == message.author.id) and not nick:
        return False
    if db.upsert({'name': message.author.name, 'id': message.author.id, 'nick': nick if nick else ''},
                 User.id == message.author.id):
        return True
    return False


def leave_me_alone(message):
    if db.remove(User.id == message.author.id):
        return True
    return False


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if isinstance(message.channel, discord.DMChannel):
        if "off" in message.content:
            if leave_me_alone(message):
                await message.channel.send("I'm not bothering you anymore.")
            else:
                await message.channel.send("I already know I shouldn't bother you.")
        elif "@" in message.content:
            nick = re.findall(r"@[a-z|A-Z]*", message.content, re.IGNORECASE)[0]
            if notify_me(message, nick.replace('@', '')):
                await message.channel.send(
                    "Ok... Now I'm gonna try to bother you every time someone highlights your discord name or **{nick}** in a .qw!". \
                        format(nick=nick))
        else:
            if notify_me(message):
                await message.channel.send(
                    "Ok... Now I'm gonna try to bother you every time someone highlights you in a .qw!\n" +
                    "You can choose to be poked with a second nickname too - just type @nick.")
            else:
                await message.channel.send(
                    "I can see I'm programmed to bother you already.\n" +
                    "You can choose to be poked with a second nickname too - just type @nick.\n" +
                    "Type `**** off` for me to stop.")

    if message.author.id == 179983238129909760:
        tags = list(set(re.findall(r"@[a-z|A-Z|0-9|_]+", message.content, re.IGNORECASE)))
        for tag in tags:
            user = False
            poked = False
            for item in db:
                if item.get("name", "").lower() == tag.replace("@", "").lower() or item.get("nick",
                                                                                            "").lower() == tag.replace(
                        "@", "").lower():
                    user = client.get_user(item['id'])
                    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " - Poking " + tag.replace("@", "") + "!")
                    await user.send(user.mention + '\n' + message.content, embed=message.embeds[0])
                    poked = True
                else:
                    print('User ' + tag + ' not found.')
            # if '@FORCE' in tags and not poked:
            if not poked:
                members = message.guild.members  # get_member_named(tag.replace("@",""))
                found = []
                for m in members:
                    r = False
                    try:
                        r = m.nick.lower() == tag.replace("@", "").lower()
                        if not r:
                            r = m.name.lower() == tag.replace("@", "").lower()
                    except Exception:
                        try:
                            r = m.name.lower() == tag.replace("@", "").lower()
                        except Exception:
                            r = False
                    if not r and '@FORCE' in tags and len(tag) > 6:
                        try:
                            r = tag.replace("@", "").lower() in m.nick.lower()
                            if not r:
                                r = tag.replace("@", "").lower() in m.name.lower()
                        except Exception:
                            try:
                                r = tag.replace("@", "").lower() in m.name.lower()
                            except Exception:
                                r = False
                    if r:
                        found.append(m)
                for m in found:
                    if not user:
                        user = m
                    elif m.created_at > user.created_at:
                        user = m
                if user:
                    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " - Poking " + tag.replace("@", "") + " (" + user.name + ")" + "!")
                    await user.send(user.mention + '\n' + message.content, embed=message.embeds[0])


@client.event
async def on_ready():
    print("The bot is ready!")
    await client.change_presence(activity=discord.Game(name="Poking people!"))


client.run(TOKEN)

