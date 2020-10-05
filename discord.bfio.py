#!/usr/bin/env python3
import discord
import asyncio
import json

# Created By: Whippersnatch Pumpkinpatch#2008, 245592600793317377
# Brainfuck interpreter originally created by megamaz#1020, 604079048758394900
# https://github.com/coolymike https://github.com/megamaz
# Yes, I know this isn't the best, and it doesn't support basically anything.
# Consider this a PoC of sorts. Something to prove it can be done.
# My code is absolutely horrible, with most of it being copy pastes
# and some parts just being embarrasing.
# This was also made in the middle of the night, often around 2-3 AM
# If there's anything that needs more thought, consider
# creating an issue or pull request.

# Pointer **starts at 30k**

# Mem layout:
# 0-~27k blank
# 50 len, 29950-30k flags
# 72 len, 29878-29949 guild channel author message ids in that order
# 36 len, 29806-29878 message author name discriminator
# 100 len, 29706-29806 message channel name
# 100 len, 29606-29706 message guild name
# 2000 len, 27606-29606 message content
# 30000 len, 30k-60k free space

messages = []
bfmem = [0 for _ in range(60000)]
bfstarted = False
pointer = 30000

addresses = {
    "flagsstart": 29951,
    "messagestart": 27606,
    "channelidstart": 29896,
    "channelnamestart": 29706,
    "guildidstart": 29878,
    "guildnamestart": 29606,
    "messageidstart": 29932,
    "authoridstart": 29914,
    "authornamestart": 29806,
    "authordiscstart": 29874,
    "channelidend": 29914,
    "messageend": 29606
    }


def setflags(message):
    global addresses
    flags = ["0" for _ in range(50)]
    for n, i in enumerate([1 if message.author.bot else 0, 1]):
        flags[n] = str(i)
    setbfmem(addresses["flagsstart"], int("".join(flags)))


def setbfmem(index, value):
    isint = isinstance(value, int)
    for n, char in enumerate(str(value)):
        if ord(char) > 255:
            char = chr(8)
        bfmem[n + index] = int(char) if isint else ord(char)


def getmessage(mem):
    global addresses
    finalstr = ""
    for char in mem[addresses["messagestart"]:addresses["messageend"]]:
        if char == 0:
            return finalstr
        finalstr += chr(char)
    return finalstr


def split(word):
    return [char for char in word]


async def startbf(client):
    global messages, bfmem, pointer
    global addresses

    run = 0
    skips = 0
    with open('discordbot.bfio', 'r') as brainfuck:
        code = split(brainfuck.read())

        remove = len(code)
        while remove > 0:
            if code[remove-1] not in split("<>[].,+-"):
                code.remove(code[remove-1])
            remove -= 1
            
        if code == []:
            print('File is blank.')
            return

        opening = []
        while run < len(code):
            # print(code[run], run, bfmem[pointer], pointer)
            # input()
            # <> runners
            if code[run] == "<":
                if pointer == 0:
                    break
                else:
                    pointer -= 1
            elif code[run] == ">":
                if pointer == 60000:
                    print("Memory error: 60000 is limit")
                    break
                else:
                    pointer += 1
                
            # +- runners
            if code[run] == '+':
                if bfmem[pointer] >= 255:
                    bfmem[pointer] = 0
                else:
                    bfmem[pointer] += 1
            elif code[run] == '-':
                if bfmem[pointer] <= 0:
                    bfmem[pointer] = 255
                else:
                    bfmem[pointer] -= 1
            
            # ., runners
            if code[run] == ",":
                setbfmem(addresses["messagestart"], int(''.join(["0" for _ in range(2394)]))) # Clears the entire (used) IO
                try:
                    message = messages[0]
                    messages.pop(0)
                    setbfmem(addresses["messagestart"], message.content)
                    setbfmem(addresses["channelidstart"], message.channel.id)
                    setbfmem(addresses["channelnamestart"], message.channel.name)
                    try:
                        setbfmem(addresses["guildidstart"], message.guild.id)
                        setbfmem(addresses["guildnamestart"], message.guild.name)
                    except: pass
                    setbfmem(addresses["messageidstart"], message.id)
                    setbfmem(addresses["authoridstart"], message.author.id)
                    setbfmem(addresses["authornamestart"], message.author.name)
                    setbfmem(addresses["authordiscstart"], message.author.discriminator)
                    setflags(message)
                except Exception as e:
                    pass
                await asyncio.sleep(0.5)
            if code[run] == ".":
                tmpchannelid = ""
                for item in bfmem[addresses["channelidstart"]:addresses["channelidend"]]:
                    tmpchannelid += str(item)
                tmpchannelid = int(tmpchannelid)
                tmpchannel = await client.fetch_channel(tmpchannelid)
                await tmpchannel.send(getmessage(bfmem))
                

            # [] runners.
            if code[run] == "[":
                for b in range(run+1, len(code)):
                    if code[b] == "[":
                        skips += 1
                        
                    if code[b] == "]":
                        if skips == 0:
                            opening.append((run, b))
                        else:
                            skips -= 1
                if bfmem[pointer] == 0:
                    for a in opening:
                        if a[0] == run:
                            run = a[1]
            
            elif code[run] == "]":
                if bfmem[pointer] != 0:
                    for a in opening:
                        if a[1] == run:
                            run = a[0]
            run += 1


class MyClient(discord.Client):
    
    async def on_message(self, message):
        global messages
        messages.append(message)
    
    async def on_ready(self):
        global bfmem, bfstarted, pointer
        print(f"Ready and logged in as {str(client.user)}")
        if not bfstarted:
            bfstarted = True
            while True:
                try:
                    await startbf(client)
                except Exception as e:
                    print(repr(e))
                bfmem = [0 for _ in range(60000)]
                pointer = 30000

client = MyClient()
client.run("INSERT_TOKEN_HERE")
