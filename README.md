# AH Bonus mailer

A small Python script that uses [SupermarktConnector](https://github.com/bartmachielsen/SupermarktConnector/pull/14/files)
to search a list of products from Albert Heijn and will send an email when one 
of these products are promoted ("In de bonus" in Dutch).

You can run this script on, say, a Raspberry Pi or some other small server that
is always up. The script will query the Albert Heijn once a day.

## Getting started

Create a new virtual environment:

```
python3 -m venv ./venv
```

and activate it:

```
source ./venv/bin/activate
```

Install all required packages:

```
pip install -r ./requirements.txt
```

Copy `secrets_example.json` to `secrets.json` and replace the `TODO`s in 
`secrets.json` with your own [Mailjet](https://www.mailjet.com) API key and secret.

Copy `products_example.json` to `products.json` and fill it with the products
you'd like to be notified of. For example, if you want to be notified when broccoli
and oranges are promoted, which URLs are:

```
https://www.ah.nl/producten/product/wi4177/ah-broccoli
https://www.ah.nl/producten/product/wi67896/ah-handsinaasappelen
```

then `products.json` should look like this:

```json
[
  { "webshopId": "wi4177", "query":  "broccoli", "email": "me@something.tld" },
  { "webshopId": "wi67896", "query":  "handsinaasappelen", "email": "you@something.tld" }
]
```

As you can see, the `email` field can differ per product. That way, you can
help out a friend that doesn't run a small server (yet).