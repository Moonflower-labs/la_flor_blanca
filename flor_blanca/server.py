import os
from flask import redirect,Blueprint,session,render_template,url_for,current_app
from flor_blanca.postDb import save_customer_id, get_user_by_email, get_db
from flor_blanca.auth import login_required,required_basic
import stripe
from flask import  jsonify, request, redirect,flash
from flask_mail import Message
from flor_blanca.extensions import mail



stripe.api_key = os.environ.get('STRIPE_SECRET_KEY') 
bp = Blueprint('stripe', __name__,)



@bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    price_id = request.form.get('price_id') 
    email = session.get('email')
    user = get_user_by_email(email)
    customer_id =user[5]
    
   
    if customer_id is not None and price_id is not None:
        try:
       
            return  redirect(url_for('stripe.customer_portal')) 
        
        except Exception as e:
            return str(e)
    else:
        email = session.get('email')
        try:
              
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {                 
                    'price': price_id, 
                    'quantity': 1,
                    }
                ],
                mode='subscription',
                success_url=url_for('stripe.success', _external=True) ,
                cancel_url=url_for('stripe.cancel', _external=True),
                customer_email=email,
                shipping_address_collection={'allowed_countries':[ 'AC', 'AD', 'AE', 'AF', 'AG', 'AI', 'AL', 'AM', 'AO', 'AQ', 'AR', 'AT', 'AU', 'AW', 'AX', 'AZ', 'BA', 'BB', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BL', 'BM', 'BN', 'BO', 'BQ', 'BR', 'BS', 'BT', 'BV', 'BW', 'BY', 'BZ', 'CA', 'CD', 'CF', 'CG', 'CH', 'CI', 'CK', 'CL', 'CM', 'CN', 'CO', 'CR', 'CV', 'CW', 'CY', 'CZ', 'DE', 'DJ', 'DK', 'DM', 'DO', 'DZ', 'EC', 'EE', 'EG', 'EH', 'ER', 'ES', 'ET', 'FI', 'FJ', 'FK', 'FO', 'FR', 'GA', 'GB', 'GD', 'GE', 'GF', 'GG', 'GH', 'GI', 'GL', 'GM', 'GN', 'GP', 'GQ', 'GR', 'GS', 'GT', 'GU', 'GW', 'GY', 'HK', 'HN', 'HR', 'HT', 'HU', 'ID', 'IE', 'IL', 'IM', 'IN', 'IO', 'IQ', 'IS', 'IT', 'JE', 'JM', 'JO', 'JP', 'KE', 'KG', 'KH', 'KI', 'KM', 'KN', 'KR', 'KW', 'KY', 'KZ', 'LA', 'LB', 'LC', 'LI', 'LK', 'LR', 'LS', 'LT', 'LU', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME', 'MF', 'MG', 'MK', 'ML', 'MM', 'MN', 'MO', 'MQ', 'MR', 'MS', 'MT', 'MU', 'MV', 'MW', 'MX', 'MY', 'MZ', 'NA', 'NC', 'NE', 'NG', 'NI', 'NL', 'NO', 'NP', 'NR', 'NU', 'NZ', 'OM', 'PA', 'PE', 'PF', 'PG', 'PH', 'PK', 'PL', 'PM', 'PN', 'PR', 'PS', 'PT', 'PY', 'QA', 'RE', 'RO', 'RS', 'RU', 'RW', 'SA', 'SB', 'SC', 'SE', 'SG', 'SH', 'SI', 'SJ', 'SK', 'SL', 'SM', 'SN', 'SO', 'SR', 'SS', 'ST', 'SV', 'SX', 'SZ', 'TA', 'TC', 'TD', 'TF', 'TG', 'TH', 'TJ', 'TK', 'TL', 'TM', 'TN', 'TO', 'TR', 'TT', 'TV', 'TW', 'TZ', 'UA', 'UG', 'US', 'UY', 'UZ', 'VA', 'VC', 'VE', 'VG', 'VN', 'VU', 'WF', 'WS', 'XK', 'YE', 'YT', 'ZA', 'ZM', 'ZW',  'ZZ']}

            )
           
            return redirect(checkout_session.url, code=303)    
        
        except Exception as e:
            return str(e)



@bp.route('/success')
def success():
   
        return render_template('checkout/success.html')
  
@bp.route('/purchase_success')
def purchase_success():

    return render_template('products/success.html')

@bp.route('/cancel')
def cancel():

    return render_template('checkout/cancel.html')




@bp.route('/products')
@login_required
@required_basic
def products():
    products = []
    has_more_products = True
    starting_after_product = None
   
    while has_more_products:
        product_list = stripe.Product.search(
                query="active:'true' AND metadata['app']:'florblanca'",
                limit=100
        )
        products.extend(product_list.data)
        has_more_products = product_list.has_more
        if has_more_products:
            starting_after_product = product_list.data[-1].id

    
    prices = []
    has_more_prices = True
    starting_after = None

    while has_more_prices:
        price_list = stripe.Price.list(limit=100, active=True, starting_after=starting_after)
        prices.extend(price_list.data)
        has_more_prices = price_list.has_more
        if has_more_prices:
            starting_after = price_list.data[-1].id

    skus = {}
    for product in products:
        skus[product.id] = [price for price in prices if price.product == product.id]



    return render_template('products/shop.html', products=products, skus=skus)




@bp.route('/shop_checkout', methods=['POST'])
def shop_checkout():
   
    shipping_raw_data = stripe.ShippingRate.list(
               
                active=True,
                limit=50
        )
    shipping_data = shipping_raw_data['data']
    shipping_options = []

    for item in shipping_data :
        if item.metadata =={ "app": "florblanca"}:
            item = {"shipping_rate": item.id}
            shipping_options.append(item)
  
  
    customer_id = session.get('customer_id')
    cart = request.json
    line_items = []
   


    for item in cart:
        price_id = item.get('price_id')
        product_quantity = item.get('quantity')
        
          
        line_item = {
            'price': price_id,
            'quantity': product_quantity,           
        }
        line_items.append(line_item)
   
    try:
        
            checkout_session = stripe.checkout.Session.create(
                line_items=line_items,
                mode='payment',
                success_url=url_for('stripe.purchase_success', _external=True),
                cancel_url=url_for('stripe.cancel', _external=True),
                customer=customer_id,
                shipping_options=shipping_options,
               
            )

            return   jsonify(checkout_session.url)
            
    except Exception as e:
            return jsonify({'error': str(e)})
        
  


@bp.route('/webhook', methods=['POST'])
def webhook_received():
    payload = request.data.decode("utf-8")
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET') 
   
    
   
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        current_app.logger.warning(" Error while decoding event!")
        return jsonify({'error': str(e)})
    
    except stripe.error.SignatureVerificationError as e:
        current_app.logger.warning(" Invalid signature!")
        return jsonify({'error': str(e)})
    

    event_id = event.id 
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT event_id FROM webhooks WHERE event_id = %s', (event.id,))
    stored_event = cursor.fetchone()
   

    if stored_event :
        current_app.logger.info(" Event has already been processed.")
        return jsonify(success=True)
    else:
        cursor.execute('INSERT INTO webhooks(event_id) VALUES (%s)',(event_id,))
        current_app.logger.info(" New event saved.")
        current_app.logger.info(event.type)
   
        if event.type == 'checkout.session.completed' :  
             checkout_session = event.data.object     
             
             customer_id = checkout_session['customer']       
              
             customer = stripe.Customer.retrieve(customer_id)       
              
             email = customer.email     
             get_user_by_email(email)
             session['customer_id']= customer_id
        
                # Save the customer ID in database
               # save_customer_id(customer_id, email)

             retrieved_session = stripe.checkout.Session.retrieve(
                checkout_session.id,
                expand=["line_items"],
                )
             shipping_address = retrieved_session.custom_text.shipping_address 
             print(f"shipping_address :{shipping_address}")
             line_items = retrieved_session.line_items
             formatted_order =[]
             for item in line_items:
                metadata =[]
                raw_meta = item.price.metadata
                for key,value in raw_meta.items():
                    meta = {key: value}
                    metadata.append(meta)
                item = {"Id" : item.price.id,"price" : item.price.unit_amount/100 ,"quantity" : item.quantity,"metadata" : metadata}
                formatted_order.append(item)
       
                 #  EMAIL ADMIN
             try:     
             
                 msg = Message('Nuevo pedido para Flor Blanca!', sender='admin@thechicnoir.com',
                                  recipients=['alex.landin@hotmail.com','admin@thechicnoir.com'])
           
           
                 formatted_order_string = '\n'.join(str(item) for item in formatted_order)
                 formatted_order_string = formatted_order_string.replace("'", "").replace("{", "").replace("}", "")
                 msg.body = f"email: {email}\nCustomer ID: {customer_id}\n{formatted_order_string}"
           
                 mail.send(msg)
                 current_app.logger.info(' Email sent to admin')

             except Exception as e:
                 
                 return current_app.logger.warning(str(e))
        
        elif event.type == 'customer.created':
            customer = event.data.object     
            customer_id = customer['id']
            email = customer.email    

            user = get_user_by_email(email)
            if user:
                if user[5] is not None and user[5] == customer_id:
                    current_app.logger.info(' User and Customer ID already in the system')
                else:
                    # Save the customer ID in database
                    save_customer_id(customer_id, email)

            else:
                current_app.logger.info(' unkown customer!')
        elif event.type == 'customer.subscription.updated':
            stripe_subscription = event.data.object

            # Retrieve the subscription ID, cus id, price id, prod id
            subscription_id = stripe_subscription['id']
            customer_id = stripe_subscription['customer']
            price_id = stripe_subscription['items']['data'][0]['plan']['id']
            product_id = stripe_subscription['items']['data'][0]['plan']['product']
            subscription_status = stripe_subscription['items']['data'][0]['plan']['active']
            # Retrieve the customer object from the Stripe API
            customer = stripe.Customer.retrieve(customer_id)       
            # Retrieve the email from the customer object
            email = customer.email
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM users WHERE customer_id = %s ',(customer_id,))
            user = cursor.fetchone()
            
            
            if user is not None:
                if user[5] == customer_id:
                    if subscription_status == True:
                        subscription_status = "active"
                    else:
                        subscription_status = "inactive"    
                           
                        cursor.execute("""UPDATE users SET subscription_status = %s,subscription_plan=%s WHERE customer_id=%s  """,(subscription_status,price_id,customer_id))
                    
                        current_app.logger.info(f" Successfully saved {user[1]}'s details.\nsubscription_status: {subscription_status}\nprice_id: {price_id}")

        elif event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
        


        elif event.type == 'subscription_schedule.canceled':
            stripe_subscription = event.data.object
            customer_id = stripe_subscription['customer']
            price_id = stripe_subscription['phases'][0]['items'][0]['price']
            status = stripe_subscription['status']

    
        
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM users WHERE customer_id= %s ', (customer_id,))
            user = cursor.fetchone()
        
        
            if user is not None:
                    cursor.execute('UPDATE users SET subscription_plan=%s, subscription_status=%s WHERE customer_id= %s ',("inactive",None,customer_id))
                    db.commit()
                    current_app.logger.info(' Customer subscription canceled, plan succesfully deleted')

        
        
    return jsonify(success=True)

   
@bp.route('/customer-portal', methods=['POST','GET'])
@login_required
def customer_portal():
    email = session.get('email')
   
    if email:
        user = get_user_by_email(email)
        
        if user:
            customer_id = user[5]
                      
            if customer_id is not None:

                try:
                
                     billing_session = stripe.billing_portal.Session.create(
                        customer=customer_id,
                        return_url=url_for('stripe.customer_portal_redirect', _external=True)
                    )

                     return redirect(billing_session.url)
            
                except Exception as e:
                    return str(e)
            else:
                flash("No pudimos encontrar una suscripcion asociada a tu cuenta")

    flash("Debes comprar una suscripción antes de acceder al Customer portal ")
   
    return redirect(url_for('index', _anchor='plans'))



    
    
@bp.route('/customer-portal-redirect')
def customer_portal_redirect():
    return redirect(url_for('index')) 



