import yookassa as yk
from yookassa import Configuration, Payment
import os
import asyncio
import logging
from config import BOT_TOKEN

Configuration.account_id = "123124"
Configuration.secret_key = os.getenv("SECRET_KEY")
logger = logging.getLogger(__name__)


def _create_payment(order_id:int, user_id: int, description: str,amount: float, idem_key:str) -> tuple[str,str]:
    payment = Payment.create({
        "amount": {"value": f"{amount:.2f}","currency": "RUB"},
        "capture": True,
        "confirmation": {"type": "redirect", "return_url": BOT_TOKEN},
        "description": description,
        "metadata": {"order_id": order_id,"user_id": user_id},
    },idem_key
    )
    return payment.id, payment.confirmation.confirmation_url



async def create_payment(*args,**kwargs):
    try:
        return await asyncio.to_thread(_create_payment,*args,**kwargs)
    except Exception:
        logger.exception("Не удалось создать платёж")
        raise