import os
import re
import pandas as pd
import requests
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
CSV_PATH = "data.csv"

def parse_push(text):
    amount_search = re.search(r'(\d[\d\s]*[\.,]?\d*)\s*(?:₽|руб)', text, re.IGNORECASE)
    if not amount_search:
        return None
    
    raw_amount = amount_search.group(1).replace(' ', '').replace(',', '.')
    amount = float(raw_amount)
    text_lower = text.lower()
    
    is_income = any(w in text_lower for w in ['пополнение', 'зачисление', 'перевод +', 'поступление', 'входящий'])
    
    if is_income:
        trans_type = "Доход"
        category = "Доход"
    else:
        trans_type = "Расход"
        if any(w in text_lower for w in ['додо', 'вкусно', 'бургер', 'кфс', 'kfc', 'кафе', 'ресторан', 'фастфуд', 'кофе']):
            category = "LEAK"
        elif any(w in text_lower for w in ['такси', 'yandex go', 'uber', 'самокат', 'whoosh', 'юрент']):
            category = "LEAK"
        elif any(w in text_lower for w in ['пятёрочка', 'магнит', 'перекресток', 'ашан', 'продукты']):
            category = "LIFE"
        else:
            category = "WANT"
            
    return {
        "Date": datetime.now().strftime("%Y-%m-%d"),
        "Type": trans_type,
        "Amount": amount,
        "Category": category,
        "Raw": text
    }

def process_telegram_updates():
    if not TOKEN:
        print("Ошибка: BOT_TOKEN не найден.")
        return
        
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    res = requests.get(url).json()
    
    if not res.get("ok") or not res.get("result"):
        print("Нет новых сообщений.")
        return

    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
    else:
        df = pd.DataFrame(columns=["Date", "Type", "Amount", "Category", "Raw"])

    new_rows = []
    max_update_id = 0

    for update in res["result"]:
        max_update_id = max(max_update_id, update["update_id"])
        message = update.get("message", {}).get("text", "")
        if not message:
            continue
            
        parsed = parse_push(message)
        if parsed:
            new_rows.append(parsed)
            print(f"Добавлено: {parsed}")

    if new_rows:
        new_df = pd.DataFrame(new_rows)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_csv(CSV_PATH, index=False)
        print("Файл data.csv успешно обновлен!")

    requests.get(f"{url}?offset={max_update_id + 1}")

if __name__ == "__main__":
    process_telegram_updates()
