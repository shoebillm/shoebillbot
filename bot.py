import random
import asyncio
import urllib3
import certifi
import re
import os
import aiohttp
import json
import discord
import youtube_dl
import pytz 
from youtube_search import YoutubeSearch
import requests

from datetime import datetime
from discord import Game
from discord.ext.commands import Bot
from discord.ext import commands,tasks
from bs4 import BeautifulSoup
from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
import matplotlib.dates as mdates



BOT_PREFIX = ("!")
# TOKEN = ""  # Get at discordapp.com/developers/applications/me

intents = discord.Intents().all()
client = commands.Bot(command_prefix="!", intents=intents)
# TENOR_API_KEY = ''

def get_crypto(currency):
    global ERROR_READ
    global coin_price
    url = f'https://www.worldcoinindex.com/coin/{currency}'
    page = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where()).request('GET', url)
    soup = BeautifulSoup(page.data, 'html.parser')
    try:
        coin_price = soup.find('div', attrs={'class': 'col-md-6 col-xs-6 coinprice'}).text
        coin_price = re.sub("[^0-9.,$]", "", coin_price)
        print(coin_price)
        coin_change = soup.find('div', attrs={'class': 'col-md-6 col-xs-6 coin-percentage'}).text
        coin_change = re.sub("[^0-9.,%\-+]", "", coin_change)
        print(coin_change)
        return f"The current {currency} price is: USD {coin_price}, and the change is: {coin_change} \n {currency}的现价是{coin_price}美元，涨/跌幅是{coin_change}"
    except AttributeError:
        return ERROR_READ

def get_stock(stock, day):
    key = "NJS7BCZ71GXPBCO7"
    ts = TimeSeries(key, output_format='pandas')
    data, meta_data = ts.get_intraday(symbol=stock, interval='1min', outputsize='full')
    if data.loc[day].empty:
        return f"There's no available price for today, please input another date. \n本日美股休市，请输入其他日期。"
    else:
        opn = data.loc[day]["1. open"].values[-1]
        close = data.loc[day]["4. close"].values[0]
        high = data.loc[day]["2. high"].max()
        low = data.loc[day]["3. low"].min()
        change = round((close - opn)/opn * 100, 2)
        plt.clf()
        data.loc[day]['4. close'].plot(color="blue")
        plt.gcf().autofmt_xdate()
        myFmt = mdates.DateFormatter('%H:%M')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.title(f'Times Series for the {stock} stock price on {day}')
        plt.grid()
        plt.savefig("fig.png", dpi=150)
        #plt.show()
    
        text = f"{stock} on {day}: \nCurrent/Close price: USD${close}\nOpen price: USD${opn}\nHigh: USD${high}, Low: USD${low}"
        return text

    

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="with Shoebill"))
    print("Logged in as " + client.user.name)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    quotes = [
        '咕呱咕呱',
        'Peakaboo!',
        '我反手就是一个好家伙',
        'Shoebill最可爱🧸🧸🧸',
        '你瞅啥？',
        'OMO OMO😨😨',
        'SUGOIIIIIII~~~'
        
    ]

    if 'shoebill' in message.content.lower():
        response = random.choice(quotes)
        await message.channel.send(response)
    if "你瞅啥" in message.content:
        await message.channel.send("瞅你咋地！🤬")
    if "pusheen69" in message.content.lower():
        await message.channel.send("pusheen69大坏蛋")
    
    await client.process_commands(message)
        
@client.command(pass_context=True)
async def intro(ctx):
    text = " Hi there! I was built by Shoebill.\n Right now I have limited features but I am learning🤓\n To view more, type !features 🤖 \n \n 你好， 我是书比尔的笨蛋机器人 \n 我现在啥也不会但我有在好好学习🤓\n 输入 !features 看看我能干嘛叭🤖"
    
    await ctx.send(text)

@client.command(pass_context=True)
async def features(ctx):
    text = "You can type/你可以试试输入:\n shoebill\n 你瞅啥\n pusheen69\n !time [city_name]            e.g. !time Shanghai \n!crypto [cryptocoin_name] [number_coin]               e.g. !crypto dogecoin 0.2\n !stock [stock_abbrev] [date]     e.g. !stock AAPL 2021-04-28"
    
    await ctx.send(text)
    
    
@client.command(pass_context=True)
async def piggy(ctx):
    message = "Oink Oink 🐷🐷"
    await ctx.send(message)
    await ctx.send(file=discord.File('piggy.png'))

    
# get the current cryptocoin price in USD and the change and get the total price of given crypto currency and number of coins
@client.command(pass_context=True)
async def crypto(ctx, currency="bitcoin", number=1.0):

    get_crypto(currency)
    total_price = float(coin_price.strip('$').replace(',', '')) * number
    message = get_crypto(currency) + f"\n{number} {currency} is USD$ {total_price}.\n{number} {currency}的价格是{total_price}美元"
    
    await ctx.send(message)
    

    
# Get stock price and trend
@client.command(pass_context=True)
async def stock(ctx, stock="TSLA", day=datetime.now().strftime('%Y-%m-%d')):
    stock = stock.upper()
    message = get_stock(stock, day)
    await ctx.send(message)
    await ctx.send(file=discord.File('fig.png'))
    os.remove('fig.png')
    
    
# Get the local time of the input city        
@client.command(pass_context=True)
async def time(ctx, query="Vancouver"):
    if query == "温哥华":
        query = "Vancouver"
    
    query = query.capitalize()
    if query == "Beijing" or query == "China":
        query = "Shanghai"
    
    for country, cities in pytz.country_timezones.items():
        for city in cities:
            if query in city:
                tz = pytz.timezone(city)
                
    localFormat = "%Y-%m-%d %H:%M:%S"
    utcmoment_naive = datetime.utcnow()
    utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
    local_time = utcmoment.astimezone(tz).strftime(localFormat)
    message = f"The local time in {query} is {local_time}.\n现在{query}的时间是{local_time}"
    
    await ctx.send(message)

    

@client.command(pass_context=True)
async def meme(ctx, query):
    print(ctx.message.content[6:])
    
    lmt = 1
    try:
        response = requests.get("https://g.tenor.com/v2/search?q=%s&key=%s&limit=%s&media_formats=gif" % (ctx.message.content[6:], TENOR_API_KEY, lmt))
        if response.status_code == 200:
            
            # load the GIFs using the urls for the smaller GIF sizes
            gif = json.loads(response.content)['results'][0]['media_formats']['mediumgif']['url']

            await ctx.send(gif)

        else:
            return
        
    except:
        print("An error occurred in Tenor API!")
        return 



@client.command(pass_context=True)
async def video(ctx, query):
    print(ctx.message.content[7:])

    try: 
        results = YoutubeSearch(ctx.message.content[7:], max_results=1).to_json()
        url_suffix = json.loads(results)['videos'][0]['url_suffix']
        await ctx.send(f"https://www.youtube.com{url_suffix}")
    
    except:
        print("An error occurred in YouTube searching!")
        return 


    
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f"Hi {member.name}, welcome to Shoebill's server! 你终于了来啦我等你很久啦！")



client.run(TOKEN)
