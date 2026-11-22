import asyncio
import json
import logging
from html import escape

from aiogram import Router, types
from aiogram.filters import BaseFilter, Command

from config import ADMIN_ID
from config import BARISTA_ID
from data.menu_main import MENU_DATA
from database.models import show_orders,get_all_count,get_all_sum,get_all_users,get_user_by_id
from datetime import datetime


logger = logging.getLogger(__name__)
TG_LIMIT = 4000 


class IsAdmin(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id in ADMIN_ID


class IsBarista(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id in BARISTA_ID


router_admin = Router()
router_admin.message.filter(IsAdmin())
router_barista = Router()
router_barista.message.filter(IsBarista())



def format_items(items_json: str) -> str:
    try:
        items = json.loads(items_json)
    except json.JSONDecodeError:
        logger.exception("Битый JSON в заказе: %s", items_json)
        return "  ⚠️ Не удалось прочитать состав\n"

    lines = []
    for key, qty in items.items():
        info = MENU_DATA.get(key)
        if info:
            name = escape(f"{info['name']} {info['size']}")
        else:
            name = f"неизвестный товар ({escape(str(key))})"
        lines.append(f"  - {name}: {qty} шт.")
    return "\n".join(lines) + "\n"


def format_order(user_id: int, items_json: str, total_price: int) -> str:
    return (
        f'👤 Клиент: <a href="tg://user?id={user_id}">{user_id}</a>\n'
        f"🛒 Состав:\n{format_items(items_json)}"
        f"💰 Сумма: {total_price} ₽\n"
        "➖➖➖➖➖➖➖➖\n"
    )


@router_admin.message(Command("show_orders"))
async def cmd_show_orders(message: types.Message):
    orders = await asyncio.to_thread(show_orders)
    logger.debug("show orders вернул -", repr(orders))
    if not orders:
        await message.answer("Заказов нет.")
        return

    chunk = "<b>Последние заказы:</b>\n"
    for user_id, items_json, total_price in orders:
        block = format_order(user_id, items_json, total_price)
        if len(chunk) + len(block) > TG_LIMIT:
            await message.answer(chunk, parse_mode="HTML")
            chunk = ""
        chunk += block
    if chunk:
        await message.answer(chunk, parse_mode="HTML")


# @router_barista.message(Command("sum"))
# async def get_allsum(message: types.Message):
#     now = datetime.now().strftime("%d.%m.%Y %H:%M") 
#     revenue = (await asyncio.to_thread(get_all_sum)) or 0
#     users = await asyncio.to_thread(get_all_users)
#     orders_count = await asyncio(get_all_count)

#     await message.answer(
#         f"📊 <b>Monti Coffee Bot, статистика на {now}</b>\n\n"
#         f"💰 Выручка: <b>{revenue} ₽</b>\n"
#         f"📦 Заказов: <b>{orders_count}</b>\n"
#         f"👥 Клиентов: <b>{users}</b>",
#         parse_mode="HTML",
#     )
    
