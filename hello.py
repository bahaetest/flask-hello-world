
from flask import Flask, request, redirect, session
import shopify
import traceback
import os
app = Flask(__name__)
import binascii
app.secret_key = 'your_secret_key'

API_KEY = '624716ef243f3b8d43cfa7d2cca3a5ab'
API_SECRET = '17ae93aae4aa6673965467ab332d0585'

@app.route('/install', methods=['GET'])
def install():
  try:  
    shop_url = request.args.get('shop')
    api_version = '2023-04'  # Replace with your desired API version

    # Create a Shopify session
    session['shop_url'] = shop_url
    session['api_version'] = api_version
    session['state'] = binascii.b2a_hex(os.urandom(15)).decode("utf-8")

    # Build the installation URL and redirect the user
    install_url = shopify.Session(shop_url, api_version).create_permission_url(
        scope='read_products',
        redirect_uri=request.host_url + 'install/callback'
    )
    return redirect(install_url)
  except Exception as err:
      return "er1:"+str(traceback.format_exc())
@app.route('/install/callback', methods=['GET'])
def callback():
  try:   
    # Verify the request came from Shopify
    shop_url = session.get('shop_url')
    api_version = session.get('api_version')
    state = session.get('state')
    if not shop_url or not api_version or not state:
        return 'Invalid callback request'

    # Create a Shopify session
    session['state'] = None
    session['access_token'] = shopify.Session(shop_url, api_version).request_token(request.args.to_dict())

    # Save the access token to a file or database
    save_access_token(shop_url, session['access_token'])

    return 'Authentication successful'
  except Exception as err:
      return "er2:"+str(traceback.format_exc())
def save_access_token(shop_url, access_token):
    file_path = f"{shop_url}_access_token.txt"  # Replace with your desired file path

    # Write the access token to a file
    with open(file_path, 'w') as file:
        file.write(access_token)

if __name__ == '__main__':
    shopify.ShopifySession.setup(api_key=API_KEY, secret=API_SECRET)
    app.run(debug=True)
