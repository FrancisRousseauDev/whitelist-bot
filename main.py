import psycopg2
import os
from discord.ext import commands
import discord
from time import sleep

TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')
client = discord.Client()


@client.event
async def on_message(message):
    if message.guild:
        if not str('923579001010794527') in str(message.author.id) and str(message.channel.id) == '927245506130878504':
            if message.content == '!!help':
                await message.channel.send(getHelpMessage())
            elif message.content == '!!info':
                await message.channel.send(getInfoMessage())
            elif message.content == '!!check':
                result = readDatabase('check', message.author.id, message.content)
                if len(result) > 0:
                    await message.channel.send('Your address is set: ' + str(result[0][0]))
                    sleep(10)
                    await message.channel.purge(limit=1000000)
                    await message.channel.send(getHelpMessage())
                else:
                    await message.channel.send('No address set yet.')
            elif str('!!set') in message.content:
                await message.channel.send('Sorry! Whitelist is currently closed.')
                sleep(7)
                await message.channel.purge(limit=1000000)
                await message.channel.send(getHelpMessage())
                #result = readDatabase('check', message.author.id, message.content)
                #token = message.content.replace('!!set ', '')
                #if len(result) == 1:
                #    await message.channel.send('Sorry! There is already set an address for this user.')
                #    sleep(10)
                #    await message.channel.purge(limit=1000000)
                #    await message.channel.send(getHelpMessage())
                #else:
                #    if len(token) > 25:
                #        await message.channel.purge(limit=1)
                #        readDatabase('set', message.author.id, token)
                #        await message.channel.send('Address is set! Use **!!check** to verify!')
                #       sleep(7)
                #       await message.channel.purge(limit=1000000)
                #        await message.channel.send(getHelpMessage())
                #    else:
                #       await message.channel.send('Not a valid token address!')

            elif str('!!update') in message.content:
                result = readDatabase('check', message.author.id, message.content)
                token = message.content.replace('!!update ', '')
                if len(result) == 0:
                    await message.channel.send('Sorry! There is no address for this account yet.')
                else:
                    if len(token) > 25:
                        readDatabase('update', message.author.id, token)
                        await message.channel.send('Address is updated! Use **>>check** to verify!')
                        sleep(5)
                        await message.channel.purge(limit=1000000)
                        await message.channel.send(getHelpMessage())
                    else:
                        await message.channel.send('Not a valid token address!')

def getHelpMessage():
    welcomeMessage = f"\nWelcome to the Whitelist bot!\n" \
                     "**Commands**\n" \
                     "```!!info                  : why is this BOT here?\n" \
                     "!!check                 : will return the current address saved for your current discord ID\n" \
                     "!!set <address>         : whitelist is closed\n" \
                     "!!update <address>      : will update your address\n```"

    return welcomeMessage


def getInfoMessage():
    infoMessage = f"```This bot is made to set all whitelist addresses so you can get access to our presale of the VeeParrots-NFT collection.\n" \
                  "If you don't set a valid address, you will not be able to mint NFT's in our presale.```"
    return infoMessage


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


def readDatabase(type, value, value2):
    global connection
    try:
        connection = psycopg2.connect(user=os.getenv('USER'),
                                      password=os.getenv('PASSWORD'),
                                      host=os.getenv('HOST'),
                                      port=5432,
                                      database=os.getenv('DATABASE'))
        cursor = connection.cursor()

        result = ''

        if type == 'check':
            query = 'SELECT address, name FROM public.whitelists w where name = \'' + str(value) + '\''
            cursor.execute(query)
            result = cursor.fetchall()

        if type == 'set':
            postgres_insert_query = """ INSERT INTO public.whitelists(address, name) VALUES (%s, %s)"""
            record_to_insert = (value2, value)
            cursor.execute(postgres_insert_query, record_to_insert)
            connection.commit()
            result = cursor.rowcount
        if type == 'update':
            postgres_insert_query = """ UPDATE public.whitelists SET address=(%s), name=(%s) WHERE name = (%s);"""
            record_to_insert = (value2, value, str(value))
            cursor.execute(postgres_insert_query, record_to_insert)
            connection.commit()
            result = cursor.rowcount

        print('res', result)
        return result


    except (Exception, psycopg2.Error) as error:
        print(error)
        return str(error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()


client.run(TOKEN)
