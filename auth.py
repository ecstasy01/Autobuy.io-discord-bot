import aiohttp
import aiofiles
import random
import asyncio
import json

config = json.loads(
    open('./data/config.json').read()
)

async def check_redeemed(order_id):
    async with aiofiles.open('./data/redeemed.txt', 'r+') as file:
        try:
            lines = await file.readlines()
            for order_id in lines:
                order_id = order_id.replace('\n','')
                if order_id == order_id:
                    valid = True
                    break

                else:
                    valid = False

            return(valid)

        except:
            await file.close()


async def use_orderid(order_id):
    async with aiofiles.open('./data/redeemed.txt', 'a') as file:
        await file.writelines(order_id + '\n')
        await file.close()


async def check_order(order_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            'https://autobuy.io/api/Order/' + order_id,
             headers = {'APIKey': config['api_key']}
        ) as response:
            content = await response.text()

        if '{"id":"' in content:
            data = await response.json()

            return(
                data
            )

        else:
            return(
                'Order not found'
            )

