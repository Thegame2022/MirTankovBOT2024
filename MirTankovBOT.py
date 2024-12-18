import telebot
from g4f.client import Client as G4FClient
import requests
from bs4 import BeautifulSoup

TOKEN = '7610333260:AAFNaYjgBR9r4qhdpg8sgcsVLgKyUCWL5Jc'
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения истории сообщений для каждого пользователя
user_histories = {}

# Список URL для загрузки контента
urls = [
    'https://tanki.su',
    'https://play-tanki-su.turbopages.org/promo/media/play.tanki.su/sekretnye-taktiki-igry-dlia-novichkov-v-mire-tankov-67126c762ac40421f62c1871?flight_id=4560110809479273380&a1=&a2=&a3=&a4=&a5=none&a6=search&a7=1383420750341603327&yclid=1383420750341603327&utm_source=yandex.promopages&utm_medium=article_direct&utm_campaign=WOT%20RU%20Y%20Promopages%20Ong%20ACQ_PP_Secret_tactics_0824&utm_content=Секретные%20тактики%20игры%20для%20новичков%20в%20«Мире%20танков»_66d1c60f597a16168dabb930&utm_term=66d1c60f597a16168dabb930_1_8#',
    'https://tanki.su/ru/news/',
    'https://tanki.su/ru/content/docs/release_notes/',
    'https://tanki.su/ru/tankopedia/#wot&w_m=tanks',
]

def get_page_content(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    else:
        return None


def get_all_pages_content():
    content = []
    for url in urls:
        page_content = get_page_content(url)
        if page_content is not None:
            content.append(page_content)
    return '\n'.join(content)


def get_answer(messages):
    max_attempts = 5
    attempt = 0

    while attempt < max_attempts:
        try:
            client = G4FClient()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            res = response.choices[0].message.content
            return res

        except Exception as e:
            print(f"Ошибка при запросе: {e}")

        attempt += 1

    return "Произошла ошибка при получении ответа."


@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = "Привет! Я бот по Миру Танков. Ты можешь задать мне свой вопрос о танках."
    bot.send_message(message.chat.id, welcome_text)


@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.chat.id

    # Если у пользователя еще нет истории, создаем ее
    if user_id not in user_histories:
        user_histories[user_id] = [{"role": "system", "content": "Вы — эксперт по игре Мир Танков."}]

    # Добавляем сообщение пользователя в историю
    user_histories[user_id].append({"role": "user", "content": message.text})

    all_content = get_all_pages_content()
    if all_content:
        prompt = f"{all_content}\n{user_histories[user_id][-1]['content']}"
        answer = get_answer(user_histories[user_id])

        # Добавляем ответ бота в историю
        user_histories[user_id].append({"role": "assistant", "content": answer})

        bot.reply_to(message, answer)
    else:
        bot.reply_to(message, "Не удалось загрузить страницы.")


bot.polling()