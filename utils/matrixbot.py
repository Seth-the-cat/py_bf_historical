import asyncio
import os
import time
import logging
import threading
from nio import AsyncClient
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

last_notification_time = 0
COOLDOWN_SECONDS = 60 

async def _async_send(message):
    user_id = os.getenv("MATRIX_USER_ID")
    homeserver = os.getenv("MATRIX_HOMESERVER", "https://matrix.org")
    room_id = os.getenv("MATRIX_ROOM_ID")
    token = os.getenv("MATRIX_BOT_TOKEN")

    client = AsyncClient(homeserver, user_id)
    client.access_token = token
    
    try:
        # We use a timeout to ensure the bot doesn't hang forever
        response = await asyncio.wait_for(
            client.room_send(
                room_id=room_id,
                message_type="m.room.message",
                content={"msgtype": "m.text", "body": message}
            ), 
            timeout=10.0
        )
        logger.debug(f"Matrix send response: {response}")
        logger.info("Matrix notification sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send Matrix notification: {e}")
    finally:
        await client.close()

def send_notification(message):
    global last_notification_time
    current_time = time.time()
    if (current_time - last_notification_time) < COOLDOWN_SECONDS:
        return
    
    last_notification_time = current_time

    # FIX: Use a Thread to send the notification.
    # This ensures the notification doesn't get killed when the 
    # main network event loop closes.
    def run_in_thread():
        asyncio.run(_async_send(message))

    threading.Thread(target=run_in_thread, daemon=True).start()