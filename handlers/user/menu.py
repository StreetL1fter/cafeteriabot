from aiogram import F,Router,types,Bot
from aiogram.filters import Command
from aiogram.types import LoginUrl
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile
from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from states.Orderstate import OrderState
from data.menu_main import MENU_DATA
from pathlib import Path
from config import ADMIN_ID, BARISTA_ID
from database.models import save_user
from database.models import save_orders
from database.models import get_all_sum,get_all_users,get_all_count,get_user_by_id,show_orders
import json
from datetime import datetime
import sqlite3
import asyncio
from database.models import DB_NAME


now = datetime.now().strftime("%d.%m.%Y %H:%M")



router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="Сделать заказы", callback_data="take_orders")
    builder.button(text="Мои бонусы", callback_data="my_gifts")
    builder.button(text="Наш адрес", callback_data="our_address")
    await message.answer(f"Здорово, {message.from_user.first_name}! 🤝. \nУ нас тут не просто кофе, а топливо для твоих свершений.\n Никакой воды — только мощный вкус и качество. \n"
                         "Готов сделать заказ? Жми «Сделать заказ» и не тормози. \nМы уже разогреваем оборудование.",reply_markup=builder.as_markup())

@router.callback_query(F.data == "take_orders")
async def take_orders(callback: types.CallbackQuery):
    await callback.answer()
    builder2 = InlineKeyboardBuilder()
    builder2.button(text="Капучино 0.2", callback_data="buy_cap_02")
    builder2.button(text="Капучино 0.4", callback_data="buy_cap_04")
    builder2.button(text="Американо 0.2",callback_data="buy_americ_02")
    builder2.button(text="Американо 0.4", callback_data="buy_americ_04")
    builder2.button(text="⬅️ Назад", callback_data="back_to_menu")
    builder2.adjust(2) 
    await callback.message.edit_text(
        "Выберите объем напитка:", 
        reply_markup=builder2.as_markup()
    )

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.answer()
    builder = InlineKeyboardBuilder()
    builder.button(text="Сделать заказы", callback_data="take_orders")
    builder.button(text="Мои бонусы", callback_data="my_gifts")
    builder.button(text="Наш адрес", callback_data="our_address")
    await callback.message.edit_text(f"Здорово, {callback.from_user.first_name}! 🤝.У нас тут не просто кофе, а топливо для твоих свершений. Никакой воды — только мощный вкус и качество. "
                             "Готов сделать заказ? Жми «Сделать заказ» и не тормози. Мы уже разогреваем оборудование.",reply_markup=builder.as_markup())
    


@router.callback_query(F.data.startswith("buy_"))
async def buy_coffee(callback: types.CallbackQuery,state: FSMContext):
    await callback.answer()

    item_key = callback.data.removeprefix("buy_")

    item_info = MENU_DATA[item_key]
    name = item_info["name"]
    size = item_info["size"]

    data = await state.get_data()
    cart = data.get("cart",{})

    cart[item_key] = cart.get(item_key,0) + 1

    await state.update_data(cart=cart)

    builder = InlineKeyboardBuilder()
    builder.button(text="Добавить еще", callback_data="take_orders")
    builder.button(text="Перейти в корзину", callback_data="view_cart")
    builder.adjust(1)
        
    text = f"{name} {size} добавлен в корзину!\nВ вашей корзине сейчас: {sum(cart.values())} шт."

    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: types.CallbackQuery,state: FSMContext):
    await callback.answer()

    await state.update_data(cart={})

    builder = InlineKeyboardBuilder()
    builder.button(text="Сделать заказ", callback_data="take_orders")

    await callback.message.edit_text("Ваша корзина пуста. Добавьте ещё что-нибудь из меню",reply_markup=builder.as_markup())



@router.callback_query(F.data == "view_cart")
async def buy_cap_04(callback: types.CallbackQuery,state: FSMContext):
    data_get = await state.get_data()
    cart = data_get.get("cart",{})
    if not cart:
        await callback.message.answer("Ваша корзина пуста")
        return

    text = "Ваша корзина: \n"
    total_price = 0

    for item_key,qty in cart.items():
        item_info = MENU_DATA.get(item_key)
        
        if item_info:
            name = item_info["name"]
            size = item_info["size"]
            price = item_info["price"]
            
            item_total = price * qty
            total_price += item_total
            
            text += f"• {name} {size} — {qty} шт. × {price} ₽ = {item_total} ₽\n"
    
    text += f"\n**Итого к оплате: {total_price} ₽**"

    builder = InlineKeyboardBuilder()
    builder.button(text="Оформить заказ", callback_data="checkout")
    builder.button(text="Очистить корзину", callback_data="clear_cart")
    builder.button(text="⬅️ Назад", callback_data="take_orders")
    builder.adjust(1)

    await callback.message.edit_text(
        text, 
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )



@router.callback_query(F.data == "checkout")
async def checkout(callback:types.CallbackQuery,state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    cart = data.get("cart",{})

    if not cart:
        await callback.answer("Ваша корзина пуста",show_alert=True)
        return

    await state.set_state(OrderState.waiting_for_name)

    await callback.message.edit_text(
        "Отлично! Давайте оформим заказ.\n\n"
        "Как вас зовут? (Напишите имя в чат)"
    )

@router.message(OrderState.waiting_for_name, F.text)
async def waiting_for_name(message: types.Message,state: FSMContext):
    
    user_name = message.text
    
    await state.update_data(user_name=user_name)

    await state.set_state(OrderState.waiting_for_phone)
    await message.answer(f"Приятно познакомиться, {user_name}! Теперь отправьте ваш номер телефона (или нажмите кнопку ниже)",)




@router.message(OrderState.waiting_for_phone, F.text)
async def waiting_for_phone(message: types.Message,state: FSMContext):

    phone_number = message.text
    
    await state.update_data(phone=phone_number)

    data = await state.get_data()
    cart = data.get("cart",{})

    user_name = data.get("user_name")

    if not cart:
        await message.answer("Ваша корзина пуста: \n")
        return

    text = "Ваша корзина: \n"
    total_price = 0

    order_details = []
    
    for item_key,qty in cart.items():
        item_info = MENU_DATA.get(item_key)
            
        if item_info:
            name = item_info["name"]
            size = item_info["size"]
            price = item_info["price"]
                
            item_total = price * qty
            total_price += item_total
                
            text += f"• {name} {size} — {qty} шт. × {price} ₽ = {item_total} ₽\n"
            order_details.append(f"• {name} {size} — {qty} шт.\n")
        
    text += f"\n<b>Итого к оплате: {total_price} ₽</b>\nВыберите форму оплаты: "
    
    builder_button = InlineKeyboardBuilder()
    builder_button.button(text="ЮКасса 💳",callback_data="youkassa")
    builder_button.button(text="Telegram Stars ⭐",callback_data="telegram_stars")
    builder_button.button(text="СБП📞",callback_data="system_of_payments")
    builder_button.button(text="⬅️ Назад", callback_data="take_orders")
    builder_button.adjust(3)
    await message.answer(text, reply_markup=builder_button.as_markup(),parse_mode="HTML")
    barista_text = (
        f"🔔 <b>НОВЫЙ ЗАКАЗ!</b>\n\n"
        f"👤 Имя: {user_name}\n"
        f"📞 Тел: {phone_number}\n\n"
        f"🛒 <b>Состав:</b>\n{''.join(order_details)}"
        f"\n<b>Итого: {total_price} ₽</b>"
    )
    save_user(message.from_user.id,user_name,phone_number)

    cart_items = json.dumps(cart,ensure_ascii=False)
    order_id = save_orders(message.from_user.id,cart_items,total_price)
    button_builder = InlineKeyboardBuilder()
    button_builder.button(text="✅ Заказ готов", callback_data=f"order_done_{order_id}")
    await message.bot.send_message(chat_id=BARISTA_ID[0], text=barista_text, parse_mode="HTML",reply_markup=button_builder.as_markup())
    await state.clear()
    



@router.callback_query(F.data.startswith("order_done_"))
async def order_done(callback: types.CallbackQuery,state: FSMContext):
    await callback.answer()

    order_id_str = callback.data.removeprefix("order_done_")
    order_id = int(order_id_str)
    
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE orders SET status = 'done' WHERE order_id = ?",(order_id,))
        conn.commit()


    client_id = get_user_by_id(order_id)
    if client_id:
        await callback.bot.send_message(chat_id=client_id, text="☕ Ваш заказ готов! Ждем вас на кассе.")


    await callback.message.edit_text(
    text=f"{callback.message.text}\n\n✅ <b>ЗАКАЗ ВЫПОЛНЕН</b>", 
    parse_mode="HTML",
    reply_markup=None
    )




@router.message(Command("sum"))
async def get_allsum(message: types.Message):
    sum = get_all_sum()
    count = get_all_count()
    users_count = get_all_users()
    text = (f"Статистика <b>📊 Статистика Monti Coffee Bot за {now}</b>.\n\n"
            f"Выручка: <b>{sum} ₽</b>.\n\n"
            f"📦 Количество заказов:<b>{count}</b>.\n\n"
            f"Клиенты: 👥 Клиентов: <b>{len(users_count)}</b>\n\n"
    )
    await message.bot.send_message(chat_id=BARISTA_ID[0],text=text,parse_mode="HTML")
