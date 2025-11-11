import asyncio

from ..channels.sender import ValarChannelSender
import traceback


async def execute_channel(method, sender: ValarChannelSender):
    thread = asyncio.to_thread(__execute__, method, sender)
    asyncio.create_task(thread)


def __execute__(method, sender: ValarChannelSender):
    sender.start()
    try:
        response = method(sender)
        sender.done(response)
        sender.stop()
    except Exception as e:
        traceback.print_exc()
        sender.error(str(e))
