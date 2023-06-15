
from flask import Flask, request, redirect, render_template
from flask_shopify import shopify_webhook
import os
import binascii
import traceback
import json

app = Flask(__name__)

SHOPIFY_API_KEY = '624716ef243f3b8d43cfa7d2cca3a5ab'
SHOPIFY_API_SECRET = '17ae93aae4aa6673965467ab332d0585'
SHOPIFY_SCOPES = ['read_products', 'read_orders']
INSTALL_REDIRECT_URL = 'https://shopify2service.onrender.com/install/callback'
PREFERENCES_URL = 'https://shopify2service.onrender.com/preferences'
REDIRECT_URLS = ['https://shopify2service.onrender.com/callback']

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/install', methods=['GET'])
def install():
    try:  
        shop = request.args.get('shop')
        if shop:
            state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
            auth_url = shopify_webhook.create_permission_url(
                shop.strip(),
                SHOPIFY_SCOPES,
                INSTALL_REDIRECT_URL,
                state,
                SHOPIFY_API_KEY,
                SHOPIFY_API_SECRET
            )
            return redirect(auth_url)
        return 'Shop parameter missing'
    except Exception as err:
        return "er1:" + str(traceback.format_exc())

@app.route('/install/callback', methods=['GET'])
def install_callback():
    try:
        ra = request.args  
        shop = ra.get('shop')
        code = ra.get('code')
        if shop and code:
            access_token = shopify_webhook.request_access_token(
                shop.strip(),
                code,
                INSTALL_REDIRECT_URL,
                SHOPIFY_API_KEY,
                SHOPIFY_API_SECRET
            )
            # Save the access_token to use for API requests

            return redirect(INSTALL_REDIRECT_URL)
        return 'Installation failed'
    except Exception as err:
        return "er2:" + str(traceback.format_exc())

@app.route('/preferences', methods=['GET'])
def preferences():
    return render_template('preferences.html')

@app.route('/save-preferences', methods=['POST'])
def save_preferences():
    name = request.form.get('name')
    email = request.form.get('email')
    notification = request.form.get('notification')
    timezone = request.form.get('timezone')
    language = request.form.get('language')

    # Save the preferences to your database or perform any required operations

    return 'Preferences saved successfully'

@app.route('/callback', methods=['POST'])
@shopify_webhook.handle_webhook(SHOPIFY_API_SECRET)
def callback(data, topic):
    if topic == 'orders/create':
        # Handle order creation event
        order_data = json.loads(data)
        print("Received order event:")
        print(json.dumps(order_data, indent=2))
    
    # Return a response to acknowledge receipt of the webhook
    return 'Webhook received'

if __name__ == '__main__':
    app.run()
