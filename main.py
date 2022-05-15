import json
import datetime
import asyncio
import aiohttp
import discord

from discord.utils import get
from discord.ext import commands

from auth import *

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

config = json.loads(
    open('./data/config.json').read()
)

client = commands.Bot(
    command_prefix=config['prefix']
)

@client.event
async def on_ready():
    print('Bot is running - main server')

@client.event
async def on_command_error(ctx, error):
    embed = discord.Embed(
        title="Oops shit happened",
        description=f"Oops error: {error}",
        color=0x7289DA
    )

    await ctx.send(embed=embed)

@client.command()
async def stock(ctx):
    products = []

    async with aiohttp.ClientSession() as session:
        async with session.get(
            'https://autobuy.io/api/Products',
             headers = {'APIKey': config['api_key']}
        ) as response:
            content = await response.json()

        for ids in content['products']:
            products.append(
                f'**Product:** {ids["name"]}\n**Price:** ${ids["price"]}\n**Stock:** {ids["stockCount"]}\n\n'
            )
        
        embed = discord.Embed(
            title="Lists of products",
            description=''.join(products),
            color=0x7289DA
        )

        await ctx.send(embed=embed)


@client.command()
@commands.has_role(config['admin'])
async def remove(ctx, product_id):
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            'https://autobuy.io/api/Product',
            data = 'id=' + product_id,
            headers = {
                'APIKey': config['api_key'],
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        ) as response:
            content = await response.text()
        
        if 'Authorization failed or the product does not exist.' in content:
            embed = discord.Embed(
                title="Could not find product",
                description=f"Could not find product or api key is not valid",
                color=0x7289DA
            )

            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                title="Product has been removed!",
                color=0x7289DA
            )

            await ctx.send(embed=embed)

@client.command()
async def redeem(ctx, order_id):
    role = ctx.guild.get_role(config['customer'])
    result = await check_redeemed(order_id)
    if result == True:
        embed = discord.Embed(
            title="This order id has already been redeemed",
            color=0x7289DA
        )

    else:
        result = await check_order(order_id)

        if result == 'Order not found':
            embed = discord.Embed(
                title="Order id is not valid",
                description=f"Order id {order_id} is not valid.",
                color=0x7289DA
            )

        else:
            await ctx.message.author.add_roles(role)
            await use_orderid(order_id)
            embed = discord.Embed(
                title="Order id found!",
                description=f"Role has been added.",
                color=0x7289DA
            )
        
    await ctx.send(embed=embed)

@client.command()
@commands.has_role(config['admin'])
async def check(ctx, order_id):
    custom_feilds = []
    
    result = await check_order(order_id)

    if result != 'Order not found':

        for feilds in result['customFields']:
            custom_feilds.append(f"{feilds['name']}: {feilds['value']}\n")

        embed = discord.Embed(
            title="Order has been found!",
            color=0x7289DA
        )

        embed.add_field(name="Complete:",value=result['isComplete'],inline=True)
        embed.add_field(name="Cost:",value=result['total'],inline=True)
        embed.add_field(name="Product:",value=result['productName'],inline=False)
        embed.add_field(name="Email:",value=result['email'],inline=True)
        embed.add_field(name="Ip address:",value=result['ipAddress'],inline=True)
        embed.add_field(name="Custom feilds:",value=''.join(custom_feilds),inline=False)
            

    else:
        embed = discord.Embed(
            title=result,
            color=0x7289DA
        )
    
    await ctx.send(embed=embed)

if __name__ == '__main__':
    client.run(config['token'])
