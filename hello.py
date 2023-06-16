
from datetime import date

from flask import Flask, request, redirect, render_template
import shopify
import os
app = Flask(__name__)
import binascii
import traceback
import datetime
import random
SHOPIFY_API_KEY = '624716ef243f3b8d43cfa7d2cca3a5ab'
SHOPIFY_API_SECRET = '17ae93aae4aa6673965467ab332d0585'
SHOPIFY_SCOPES = ['read_products', 'read_orders']
INSTALL_REDIRECT_URL = 'https://shopify2service.onrender.com/install/callback'
PREFERENCES_URL = 'https://shopify2service.onrender.com/preferences'
REDIRECT_URLS = ['https://shopify2service.onrender.com/callback']
#sesion=None
@app.route('/old', methods=['GET'])
def index():
    return render_template('index.html')
def generate_mock_orders(num_orders):
    orders = []
    for _ in range(num_orders):
        order_number = random.randint(1000, 9999)
        created_at = datetime.datetime.now().isoformat()
        total_price = round(random.uniform(10, 100), 2)
        orders.append({
            'order_number': order_number,
            'created_at': created_at,
            'total_price': total_price
        })
    return orders
# Retrieve orders from the Shopify API
def get_orders():
    # Retrieve the current date
    current_date = date.today().isoformat()

    # GraphQL query to fetch orders by created_at
    query = '''
    query GetOrdersByDate($date: Date!) {
        orders(query: "created_at:>=$date") {
            edges {
                node {
                    id
                    createdAt
                    totalPrice
                }
            }
        }
    }
    '''
   # store_url = session.get('shopify_store_url')
   # shopify.ShopifyResource.set_site(store_url)
   
    #shopify.ShopifyResource.activate_session(session)
    # Execute the GraphQL query
    result = shopify.GraphQL().execute(
        query=query,
        variables={"date": current_date},
        operation_name="GetOrdersByDate"
    )

    # Process the result and return the orders
    #orders = result['data']['orders']['edges']
    if 'data' in result and result['data'] is not None:
        orders = result['data']['orders']['edges']
        return orders
    else:
        # Handle the case where there are no orders
        return []
    return orders
def get_orders_current_day():
    # Retrieve the current date
    current_date = date.today().isoformat()

    # GraphQL query to fetch orders by created_at
    query = '''
    query GetOrdersByDate($date: Date!) {
        orders(query: "created_at:>=$date") {
            edges {
                node {
                    orderNumber: order_number
                    createdAt: created_at
                    totalPrice: total_price
                    # Add other fields you need
                }
            }
        }
    }
    '''

    # Execute the GraphQL query
    result = shopify.GraphQL().execute(
        query=query,
        variables={"date": current_date},
        operation_name="GetOrdersByDate"
    )

    # Check if there are orders in the result
    if 'data' in result and result['data'] is not None:
        orders = result['data']['orders']['edges']

        # Process the result and format it as a list of dictionaries
        formatted_orders = [
            {
                'order_number': order['node']['orderNumber'],
                'created_at': order['node']['createdAt'],
                'total_price': order['node']['totalPrice']
            }
            for order in orders
        ]

        return formatted_orders
    else:
        # Handle the case where there are no orders
        return []
@app.route('/')
def home():
    return '''
    <html>
    <head>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script>
            function processOrder(orderNumber, createdAt, totalPrice) {
                $.ajax({
                    type: "POST",
                    url: "/process_order",
                    data: JSON.stringify({
                        "order_number": orderNumber,
                        "created_at": createdAt,
                        "total_price": totalPrice
                    }),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function(response) {
                        console.log("Order processed successfully");
                    }
                });
            }
        </script>
    </head>
    <body>
        '''+ get_buttons_html() + '''
    </body>
    </html>
    '''

def get_buttons_html():
 try:   
    # Retrieve the orders
    orders = get_orders()+generate_mock_orders(5)

    buttons_html = ""
    for order in orders:
        order_number = order.order_number
        created_at = order.created_at
        total_price = order.total_price

        button_html = f'<button onclick="processOrder(\'{order_number}\', \'{created_at}\', {total_price})">'
        button_html += f'Order Number: {order_number}<br>'
        button_html += f'Created At: {created_at}<br>'
        button_html += f'Total Price: {total_price}</button><br><br>'

        buttons_html += button_html
    return buttons_html
 except Exception as t:
    return "<h1>"+str(traceback.format_exc())+"</h1"

@app.route('/process_order', methods=['POST'])
def process_order():
    order_data = request.json
    order_number = order_data['order_number']
    created_at = order_data['created_at']
    total_price = order_data['total_price']

    # Call your custom function with the order data
    custom_function(order_number, created_at, total_price)

    response = {"status": "success"}
    return jsonify(response)

def custom_function(order_number, created_at, total_price):
    # Replace with your custom logic
    print("Processing Order Number:", order_number)
    print("Created At:", created_at)
    print("Total Price:", total_price)

@app.route('/install', methods=['GET'])
def install():
  global session      
  try:  
    shop = request.args.get('shop')
    if shop:
        shopify.Session.setup(api_key=SHOPIFY_API_KEY, secret=SHOPIFY_API_SECRET)
        session = shopify.Session(shop.strip(),'2023-04')
        

        state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
        auth_url = session.create_permission_url(SHOPIFY_SCOPES,INSTALL_REDIRECT_URL,state)
        print(auth_url)
        return redirect(auth_url)
    return 'Shop parameter missing'
  except Exception as err:
      return "er1:"+str(traceback.format_exc())
@app.route('/install/callback', methods=['GET'])
def install_callback():
  try:
    ra=request.args  
    shop = ra.get('shop')
    code = ra.get('code')
    if shop and code:
        shopify.Session.setup(api_key=SHOPIFY_API_KEY, secret=SHOPIFY_API_SECRET)
        session = shopify.Session(shop.strip(), '2023-04')
        token = session.request_token(ra)
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
