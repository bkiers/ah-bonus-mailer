import time
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from mailjet_rest import Client
import os
import re
from dotenv import dotenv_values
import json

config = dotenv_values("secrets.config")


class BonusProduct:

    def __init__(self, week, line):
        self.week = week
        self.line = re.sub('[\\s\\d.]+$', '', line)

    def matches(self, pattern):
        return pattern.lower() in self.line.lower()

    def __repr__(self):
        return f'{self.line}'


def send_email(email, file_name, subject, text):
    if os.path.isfile(file_name):
        # An email was already sent for this
        return

    mailjet = Client(auth=(config['MAILJET_API_KEY'], config['MAILJET_API_SECRET']), version='v3.1')

    data = {
        'Messages': [
            {
                "From": {"Email": config['EMAIL_FROM']},
                "To": [{"Email": email}],
                "Subject": subject,
                "TextPart": text,
                "HTMLPart": text.replace('\n', '<br>')
            }
        ]
    }

    response = mailjet.send.create(data=data)

    if response.status_code == 200:
        with open(file_name, 'w') as f:
            print(f"Sent message to {email}: {text}")
            f.write(text)


def bonus_products():
    res = requests.get('https://www.ah.nl/bonus')
    soup = BeautifulSoup(res.text, 'html.parser')
    week_infos = soup.findAll('span', {'class': re.compile('period-toggle_periodLabel__.*')})
    products = []

    if len(week_infos) == 0:
        print('No week info found!')
    else:
        week = week_infos[0].getText()
        bonus_tiles = soup.findAll('a', {'class': re.compile('card_root__.*')})

        for bonus_tile in bonus_tiles:
            products.append(BonusProduct(week, bonus_tile.get_text(separator=' ')))

    return products


def notify_for(bonus_product, email, pattern):
    week_id = re.sub('\\W', '_', bonus_product.week)
    file_name = f"./emails/{email}_{week_id}_{pattern}.txt"

    send_email(email, file_name, "New AH Promotion!", f"{bonus_product.line}\nPeriod: {bonus_product.week}")


def load_products():
    with open('products.json') as file:
        return json.loads(file.read())


if __name__ == '__main__':
    print(f"Checking at {datetime.now()}...")

    while True:
        try:
            products = load_products()
            bonus_products = bonus_products()

            for product in products:
                for bonus_product in bonus_products:
                    if bonus_product.matches(product['pattern']):
                        notify_for(bonus_product, product['email'], product['pattern'])
        except Exception as e:
            print(f"OOPS: {e}")

        # Sleep for a day
        time.sleep(24 * 60 * 60)
