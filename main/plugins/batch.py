#Tg:MaheshChauhan/DroneBots
#Github.com/Vasusen-code

"""
Plugin for both public & private channels!
"""

import time, os, asyncio

from .. import bot as Drone
from .. import userbot, Bot, AUTH
from .. import FORCESUB as fs
from main.plugins.pyroplug import get_bulk_msg
from main.plugins.helpers import get_link, screenshot

from telethon import events, Button, errors
from telethon.tl.types import DocumentAttributeVideo

from pyrogram import Client 
from pyrogram.errors import FloodWait

from ethon.pyfunc import video_metadata
from ethon.telefunc import force_sub

ft = f"عَزيزي لأستخدام البوت عَليك الاشتراك  @{fs}."

batch = []

@Drone.on(events.NewMessage(incoming=True, from_users=AUTH, pattern='/cancel'))
async def cancel(event):
    if not event.sender_id in batch:
        return await event.reply("No batch active.")
    batch.clear()
    await event.reply("Done.")
    
@Drone.on(events.NewMessage(incoming=True, from_users=AUTH, pattern='/batch'))
async def _batch(event):
    if not event.is_private:
        return
    s, r = await force_sub(event.client, fs, event.sender_id, ft) 
    if s == True:
        await event.reply(r)
        return       
    if event.sender_id in batch:
        return await event.reply("لقد بدأت بالفعل دفعة واحدة، انتظر حتى تكتمل أيها المالك الغبي!")
    async with Drone.conversation(event.chat_id) as conv: 
        if s != True:
            await conv.send_message("أرسل لي رابط الرسالة الذي تريد البدء في الحفظ منه، كرد على هذه الرسالة.", buttons=Button.force_reply())
            try:
                link = await conv.get_reply()
                try:
                    _link = get_link(link.text)
                except Exception:
                    await conv.send_message("No link found.")
                    return conv.cancel()
            except Exception as e:
                print(e)
                await conv.send_message("لا يمكنني الانتظار لفترة أطول لردك!")
                return conv.cancel()
            await conv.send_message("أرسل لي عدد الملفات/النطاق الذي تريد حفظه من الرسالة المعطاة، كرد على هذه الرسالة.", buttons=Button.force_reply())
            try:
                _range = await conv.get_reply()
            except Exception as e:
                print(e)
                await conv.send_message("لا يمكنني الانتظار لفترة أطول لردك!")
                return conv.cancel()
            try:
                value = int(_range.text)
                if value > 100:
                    await conv.send_message("يمكنك فقط الحصول على ما يصل إلى 100 ملف في دفعة واحدة.")
                    return conv.cancel()
            except ValueError:
                await conv.send_message("يجب أن يكون النطاق عددا صحيحا!")
                return conv.cancel()
            batch.append(event.sender_id)
            await run_batch(userbot, Bot, event.sender_id, _link, value) 
            conv.cancel()
            batch.clear()

async def run_batch(userbot, client, sender, link, _range):
    for i in range(_range):
        timer = 60
        if i < 25:
            timer = 5
        if i < 50 and i > 25:
            timer = 10
        if i < 100 and i > 50:
            timer = 15
        if not 't.me/c/' in link:
            if i < 25:
                timer = 2
            else:
                timer = 3
        try: 
            if not sender in batch:
                await client.send_message(sender, "Batch completed.")
                break
        except Exception as e:
            print(e)
            await client.send_message(sender, "Batch completed.")
            break
        try:
            await get_bulk_msg(userbot, client, sender, link, i) 
        except FloodWait as fw:
            if int(fw.x) > 299:
                await client.send_message(sender, "إلغاء الدفعة منذ أن انتظرت أكثر من 5 دقائق.")
                break
            await asyncio.sleep(fw.x + 5)
            await get_bulk_msg(userbot, client, sender, link, i)
        protection = await client.send_message(sender, f"Sleeping for `{timer}` seconds to avoid Floodwaits and Protect account!")
        await asyncio.sleep(timer)
        await protection.delete()
            
