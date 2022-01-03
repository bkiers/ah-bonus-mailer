import time
from datetime import datetime
from supermarktconnector.ah import AHConnector
from mailjet_rest import Client
import os
from dotenv import dotenv_values
import json

config = dotenv_values("secrets.config")


def send_email(file_name, subject, text):
    if os.path.isfile(file_name):
        # An email was already sent for this
        return

    mailjet = Client(auth=(config['MAILJET_API_KEY'], config['MAILJET_API_SECRET']), version='v3.1')

    data = {
        'Messages': [
            {
                "From": {"Email": config['EMAIL_FROM']},
                "To": [{"Email": config['EMAIL_TO']}],
                "Subject": subject,
                "TextPart": text,
                "HTMLPart": text.replace('\n', '<br>')
            }
        ]
    }

    response = mailjet.send.create(data=data)

    if response.status_code == 200:
        with open(file_name, 'w') as f:
            f.write(text)


def notify_for(product):
    start_date = product['bonusStartDate']
    end_date = product['bonusEndDate']
    file_name = f"./emails/{product['webshopId']}_{start_date}_{end_date}.txt"
    title = product['title']
    promotion_type = product['promotionType']
    bonus_mechanism = product['bonusMechanism']

    send_email(
        file_name,
        f"New AH Promotion!",
        f"Product: {title}\nPeriod: {start_date}…{end_date}\nType: {bonus_mechanism} ({promotion_type})")


def load_products():
    with open('products.json') as file:
        return json.loads(file.read())


if __name__ == '__main__':
    print(f"Checking at {datetime.now()}...")

    while True:
        try:
            connector = AHConnector()
            products = load_products()

            for product in products:
                result = connector.search_products(product['query'])
                search_results = result['products']

                if len(search_results) == 0:
                    send_email(
                        f"./emails/no_results_{product['webshopId']}.txt",
                        f"No results for {product['webshopId']}",
                        f"The query '{product['query']}' did not produce any results :("
                    )
                else:
                    for result in search_results:
                        if 'bonusStartDate' in result and product['webshopId'] == f"wi{result['webshopId']}":
                            notify_for(result)
                            break
        except Exception as e:
            print(f"OOPS: {e}")

        # Sleep for a day
        time.sleep(24 * 60 * 60)
