token = 'INPUT_T0KEN_HERE'

import discord
from discord.ext import commands
from datetime import datetime, date
import parsedatetime
import re
import asyncio
import os
from time import gmtime, strftime
import numpy as np

bot = commands.Bot(command_prefix='£')
bot.remove_command('help')
client = discord.Client()


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def help(ctx):
    embed = discord.Embed(title="BreadBot", description="Set timers and countdowns.", color=0x0ffd700)
    embed.set_author(name="BreadBot", url="https://www.pikminwiki.com/Breadbug",
                     icon_url="https://pbs.twimg.com/profile_images/1245100132292493313/sgJhjgYE_400x400.jpg")
    embed.add_field(name="£reminder", value="Set a reminder for a specific time. "
                                            "An optional message can be included in triangular brackets. "
                                            "A member or role can be mentioned in the reminder using curly brackets.",
                    inline=False)
    embed.add_field(name="£countdown", value="Start a countdown and receive a reminder when countdown ends. "
                                             "The countdown limit is 24 hours. Only one at a time please (for now).",
                    inline=False)
    embed.add_field(name="£timer", value="Under construction...", inline=False)
    embed.add_field(name="£ping", value="Bruh.", inline=True)

    embed.set_image(url="https://i.redd.it/g1o9bbhxmz411.jpg")
    embed.set_thumbnail(url="https://www.pikminwiki.com/images/thumb/7/7f/Crumbug.png/200px-Crumbug.png")

    await ctx.channel.send(embed=embed)
    return


@bot.command()
async def reminder(ctx, *args):
    """
    Set a reminder for a specific time.
    An optional message can be included in triangular brackets.
    A member or role can be mentioned in the reminder using curly brackets.
    """

    # find the current time
    current_time = datetime.now()
    current_time_secs = current_time.timestamp()

    print('\nNew reminder set by {0} at {1}.'.format(ctx.message.author, current_time))

    # parse user message into time and reminder text
    message = ''
    is_ping = False
    is_message = False
    for i in args:
        if '<' and '>' in i:
            message = re.search('<(.*)>', ' '.join(args)).group(1)
            is_message = True
            print('Message:', message)

        if '{' and '}' in i:
            mention = re.search('{(.*)}', ' '.join(args)).group(1).lower()
            is_ping = True
            print(ctx.channel.guild.get_member_named(name=mention))  # figure out why this doesnt work
            print(ctx.channel.guild.roles)
            ping = discord.utils.find(lambda m: m.name.lower().startswith(mention),
                                      (ctx.channel.guild.roles + ctx.channel.guild.members))

            if ping is None:
                await ctx.channel.send('Who tf u tryna mention bruh? Try again.')
                raise Exception('Error - ping does not exist.')

    time = re.sub(message, '', ' '.join(args))

    # find the reminder time using parsedatetime library
    cal = parsedatetime.Calendar()
    time_struct, parse_status = cal.parse(time)
    reminder_time = datetime(*time_struct[:6])
    await ctx.channel.send('Reminder set by {0.mention} for {1}.'.format(ctx.message.author, reminder_time))
    time_secs = reminder_time.timestamp()
    print('Reminder set for {0}.'.format(reminder_time))

    # find the time difference between the current time and reminder time
    time_diff = time_secs - current_time_secs
    await asyncio.sleep(time_diff)

    # send message at reminder time
    if is_ping and is_message:
        await ctx.channel.send('Reminder for {0.mention}: "{1}"'.format(ping, message))
    elif is_ping:
        await ctx.channel.send('Reminder for {0.mention}'.format(ping))
    elif is_message:
        await ctx.channel.send('Reminder for {0.mention}: "{1}"'.format(ctx.message.author, message))
    else:
        await ctx.channel.send('Reminder for {0.mention}'.format(ctx.message.author))


@bot.command()
async def countdown(ctx, *args):
    """
    Start a countdown and receive a reminder when countdown ends.
    The countdown limit is 24 hours. Only one at a time please (for now).
    """
    num_dict = {'0': ':zero:',
                '1': ':one:',
                '2': ':two:',
                '3': ':three:',
                '4': ':four:',
                '5': ':five:',
                '6': ':six:',
                '7': ':seven:',
                '8': ':eight:',
                '9': ':nine:', }

    clock_dict = {0.08: ':clock1:',
                  0.17: ':clock2:',
                  0.25: ':clock3:',
                  0.33: ':clock4:',
                  0.42: ':clock5:',
                  0.5: ':clock6:',
                  0.58: ':clock7:',
                  0.67: ':clock8:',
                  0.75: ':clock9:',
                  0.83: ':clock10:',
                  0.92: ':clock11:',
                  1.0: ':clock12:', }

    countdown_limit = 60 * 60 * 24
    os.environ['TZ'] = 'Europe/London'

    def time_to_emoji(time_secs):
        duration = ' '.join(str(strftime('%H:%M:%S', gmtime(time_secs))))
        for i in duration:
            if i.isdigit():
                duration = duration.replace(str(i), num_dict[str(i)])

        return duration

    if args == ():
        await ctx.channel.send('No duration provided.')
        raise Exception('No argument provided.')

    duration = ' '.join(args)
    user = ctx.message.author
    print('\nCountdown by {0}'.format(user))

    current_time = datetime.now()
    print('Start:', current_time)
    current_time_secs = current_time.timestamp()

    cal = parsedatetime.Calendar()
    time_struct, parse_status = cal.parse(duration)
    countdown_time = datetime(*time_struct[:6])
    print('End:', countdown_time)
    countdown_time_secs = countdown_time.timestamp()

    time_difference_secs = np.ceil(countdown_time_secs - current_time_secs)
    print('Duration:', time_difference_secs)

    if np.linalg.norm(time_difference_secs) == 0:
        await ctx.channel.send("That's not a proper duration. Try again you numpty.")
        raise TypeError("Argument not recognised.")

    clock_emoji = ':clock12:'
    if time_difference_secs > countdown_limit:
        await ctx.channel.send('Countdown time too long.')
        raise ValueError('Countdown length exceeds limit.')
    else:
        message = await ctx.channel.send(time_to_emoji(time_difference_secs) + '    ' + clock_emoji)

    time_secs = time_difference_secs
    while time_secs > 0:
        await asyncio.sleep(1)
        time_secs -= 1
        fraction = round(1 - (time_secs / time_difference_secs), 2)
        for i in clock_dict:
            if fraction >= i:
                clock_emoji = clock_dict[i]

        await message.edit(content=(time_to_emoji(time_secs) + '    ' + clock_emoji))

    await message.delete(delay=1)
    await ctx.channel.send(content='Countdown for {0.mention} has finished.'.format(user))


@bot.command()
async def timer(ctx):
    """
    Under construction...
    """

    def time_to_emoji(time_secs):
        """Converts time in seconds to emoji form HH:MM:SS"""

        num_dict = {'0': ':zero:',
                    '1': ':one:',
                    '2': ':two:',
                    '3': ':three:',
                    '4': ':four:',
                    '5': ':five:',
                    '6': ':six:',
                    '7': ':seven:',
                    '8': ':eight:',
                    '9': ':nine:', }

        duration = ' '.join(str(strftime('%H:%M:%S', gmtime(time_secs))))
        for i in duration:
            if i.isdigit():
                duration = duration.replace(str(i), num_dict[str(i)])

        return duration

    author = ctx.message.author
    print('\nTimer started by {0}'.format(author))

    # reactions added by others than the bot and the user are removed
    # @bot.event
    # async def on_reaction_add(reaction, user):
    #     bot = reaction.message.author
    #     message = reaction.message
    #
    #     if author == bot:
    #         if user != bot and user != author:
    #             await message.remove_reaction(reaction, user)
    #
    #         if reaction == '⏯':
    #             print('play/pause pressed')
    #             await asyncio.sleep(1)
    #         elif reaction == '⏹':
    #             print('stop pressed')

    time_secs = 0
    timer_message = await ctx.channel.send(content=time_to_emoji(time_secs))
    await timer_message.add_reaction('⏯')
    await timer_message.add_reaction('⏹')

    # await timer_message.edit(content=(time_to_emoji(time)))


#    await timer_message.add_reaction('⏺')


@bot.command()
async def ping(ctx):
    """
    Bruh.
    """
    await ctx.channel.send('bruh')


bot.run(token)
