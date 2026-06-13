from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import requests

BOT_TOKEN = "8939149901:AAH_wuqce_HEt2btGRXNgoZnG3P2XQonN2c"
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.strip()

        # Calculator အတွက် သင်္ချာလက္ခဏာများ
        calc_ops = ['+', '-', '*', '/', '÷']
        is_calculation = any(op in text for op in calc_ops)

        # Space ခြားထားတဲ့ စာသား
        parts = text.split()

        # ML Account Check
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit() and not is_calculation:
            user_id = parts[0]
            zone_id = parts[1]

            if len(user_id) >= 4 and len(zone_id) >= 3:
                await check_ml_account(update, user_id, zone_id)
                return

        # Calculator
        if is_calculation:
            await calculate(update, text)
            return

    except Exception as e:
        print(f"Error: {e}")


async def check_ml_account(update: Update, user_id: str, zone_id: str):
    try:
        url = "https://www.smile.one/merchant/mobilelegends/checkrole"
        data = {
            "user_id": user_id,
            "zone_id": zone_id,
            "pid": "25",
            "checkrole": "1",
            "pay_method": "",
            "channel_method": ""
        }

        r = requests.post(url, data=data, timeout=10)
        result = r.json()

        if result.get("code") == 200:
            await update.message.reply_text(
                f"✅ Account Found\n\n"
                f"👤 Name: {result['username']}\n"
                f"🆔 ID: <code>{user_id}</code>\n"
                f"🌐 Zone: <code>{zone_id}</code>\n\n"
                f"📌 Press and hold on the ID or Zone to copy\n\n"
                f"📌 Or copy both:\n"
                f"<code>{user_id} {zone_id}</code>",
                parse_mode="HTML"
            )
        else:
            pass
    except Exception as e:
        print(f"Check account error: {e}")


async def calculate(update: Update, expression: str):
    try:
        original = expression

        # ÷ ကို / ပြောင်းမယ်
        expression = expression.replace('÷', '/')

        # ခွင့်ပြုထားတဲ့ characters တွေပဲရှိရမယ်
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return

        # တွက်ချက်မယ်
        result = eval(expression)

        # ရလဒ်ကို integer ဖြစ်ရင် .0 မပါအောင်
        if result == int(result):
            result = int(result)
        else:
            result = round(result, 2)

        # Markdown အစား plain text နဲ့ပြမယ် (parse_mode မပါ)
        await update.message.reply_text(
            f"🧮 {original} = {result}"
        )
    except ZeroDivisionError:
        await update.message.reply_text("❌ Cannot divide by zero!")
    except Exception as e:
        print(f"Calculate error: {e}")


# Bot application စတင်ခြင်း
app = Application.builder().token(BOT_TOKEN).build()

# Message handler
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 Bot is running...")
print("Usage:")
print("  - ML Check: 1220968187 8948")
print("  - Calculator: 5+3, 10*2, 20/4, 100-50")

app.run_polling()
