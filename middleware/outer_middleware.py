import time
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
import logging

logger = logging.getLogger(__name__)

class BaseClass(BaseMiddleware):
    def __init__(self,limit_seconds: float=1.0):
        self.limit_seconds = limit_seconds
        self.users_last_time = {}

        async def __call__(
                self,
                handler: Callable[[Dict[str,Any],TelegramObject],Awaitable[Any]], 
                event: TelegramObject, 
                data: Dict[str,Any]) -> Any:

            user = data.get("event_from_user")

            if user:
                user_id = user.id
                current_time = time.time()

                last_time = self.users_last_time.get(user_id,0)

                if current_time - last_time < self.limit_seconds:
                    logger.info(f"Пользователь заблокирован {user_id}")
                    return

                self.users_last_time[user_id] = current_time 
            return await handler(event,data)



