from data.menu_main import MENU_DATA

def build_cart(cart: dict)-> tuple[str,int]:
    lines,total = [],0
    for key,qty in cart.items():
        item = MENU_DATA.get(key)
        if not item:
            continue
        item_total = item["price"] * qty
        total += item_total
        lines.append(
            f"• {item['name']} {item['size']} — {qty} шт. × {item['price']} ₽ = {item_total} ₽"
        )

    return "\n".join(lines),total