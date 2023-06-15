

from flask import Flask, request, redirect, render_template
import shopify
import os
app = Flask(__name__)
import binascii
import traceback
SHOPIFY_API_KEY = '8b3b1f4f0e024b14b9eb367a94792475'
SHOPIFY_API_SECRET = '0a05ec43f208cee37e92e7922af8f43b'
SHOPIFY_SCOPES = ['read_products', 'write_products']
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
        shopify.Session.setup(api_key=SHOPIFY_API_KEY, secret=SHOPIFY_API_SECRET)
        session = shopify.Session(shop.strip(),'2023-04')
        state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
        auth_url = session.create_permission_url(SHOPIFY_SCOPES,INSTALL_REDIRECT_URL, state)
        return redirect(auth_url)
    return 'Shop parameter missing'
  except Exception as err:
      return "er1:"+str(traceback.format_exc())
@app.route('/install/callback', methods=['GET'])
def install_callback():
  try:      
    shop = request.args.get('shop')
    code = request.args.get('code')
    if shop and code:
        shopify.Session.setup(api_key=SHOPIFY_API_KEY, secret=SHOPIFY_API_SECRET)
        session = shopify.Session(shop.strip(), '2023-04')
        token = session.request_token(code)
        shopify.ShopifyResource.activate_session(session)
        return redirect(PREFERENCES_URL)
    return 'Installation failed'
  except Exception as err:
      return "er2:"+str(traceback.format_exc())
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

@app.route('/callback', methods=['GET'])
def callback():
    return 'Callback handler'

if __name__ == '__main__':
    app.run()

