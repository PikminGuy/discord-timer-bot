token = 'Njk1OTY2Mjg5MDg4NDc5Mjky.XuEyJg.N_uti5l7j1nmrichXkki-Am_gUA'

import discord
from discord.ext import commands
from datetime import datetime
import parsedatetime
import re
import asyncio

bot = commands.Bot(command_prefix='£')
client = discord.Client()


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def reminder(ctx, *args):
    """
    Set a reminder for a specific time.
    An optional message can be included in triangular brackets.
    """

    # find the current time
    current_time = datetime.now()
    current_time_secs = current_time.timestamp()

    print("\nNew reminder set by {0} at {1}.".format(ctx.message.author, current_time))

    # parse user message into time and reminder text
    message = ''
    is_message = False
    for i in args:
        if '<' and '>' in i:
            message = re.search('<(.*)>', ' '.join(args)).group(1)
            is_message = True
            print("Message:", message)

    time = re.sub(message, '', ' '.join(args))

    # find the reminder time using parsedatetime library
    cal = parsedatetime.Calendar()
    time_struct, parse_status = cal.parse(time)
    reminder_time = datetime(*time_struct[:6])
    await ctx.channel.send('Reminder set by {0.mention} for {1}.'.format(ctx.message.author, reminder_time))
    time_secs = reminder_time.timestamp()
    print("Reminder set for {0}.".format(reminder_time))

    # find the time difference between the current time and reminder time
    time_diff = time_secs - current_time_secs
    await asyncio.sleep(time_diff)

    # send message at reminder time
    if is_message:
        await ctx.channel.send('Reminder for {0.mention}: "{1}"'.format(ctx.message.author, message))
    else:
        await ctx.channel.send('Reminder for {0.mention}'.format(ctx.message.author, message))


@bot.command()
async def ping(ctx):
    await ctx.channel.send('bruh')


bot.run(token)
