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
                customer_email=email
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
   
    customer_id = session.get('customer_id')
    cart = request.json['cart']
    line_items = []
    metadata = request.json['metadata']


    for item in cart:
        price_id = item.get('price_id')
        product_quantity = item.get('quantity')
        for key in metadata:
            metadata[key] = str(metadata[key])
       
     
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
                metadata=metadata
                )

            return   jsonify(checkout_session.url)
            # return redirect(checkout_session.url, code=303) 
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
        current_app.logger.warning("Error while decoding event!")
        return jsonify({'error': str(e)})
    
    except stripe.error.SignatureVerificationError as e:
        current_app.logger.warning("Invalid signature!")
        return jsonify({'error': str(e)})
    
    current_app.logger.info(event.type)
   
    if event.type == 'checkout.session.completed' :  
        stripe_session = event.data.object
        
        # Retrieve the customer ID from the completed checkout session
        customer_id = stripe_session['customer']
       
        # Retrieve the customer object from the Stripe API
        customer = stripe.Customer.retrieve(customer_id)
        
        # Retrieve the email from the customer object
        email = customer.email     
        get_user_by_email(email)
        session['customer_id']= customer_id
        
        # Save the customer ID in database
        # save_customer_id(customer_id, email)
        

        metadata = stripe_session.metadata
        
        # addind metadata to payment object
        payment_intent_id = stripe_session.payment_intent

        # Retrieve the payment_intent using payment_intent_id
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        payment_intent.metadata = metadata
        payment_intent.save()

        metadata_info = metadata['info'].split(',')
             
        try:
             #  MAIL ADMIN
            msg = Message('Hola de la Flor Blanca!', sender='admin@thechicnoir.com',
                                  recipients=['alex.landin@hotmail.com'])
            msg.body = f"email: {email},\ncustomer ID : {customer_id},\nmetadata order:\n {metadata_info},\n"
            mail.send(msg)
            current_app.logger.info('email sent to admin')
        except Exception as e:
            return current_app.logger.warning(str(e))
        
    elif event.type == 'customer.created':
        stripe_session = event.data.object
        
        # Retrieve the customer ID from the completed checkout session
        customer_id = stripe_session['customer']
       
        # Retrieve the customer object from the Stripe API
        customer = stripe.Customer.retrieve(customer_id)
        
        # Retrieve the email from the customer object
        email = customer.email     
        get_user_by_email(email)
        session['customer_id'] = customer_id
        
        # Save the customer ID in database
        save_customer_id(customer_id, email)

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
        
        #* if customer_id same as user, add price_id,product_id,subscription_status
        if user is not None:
            if user[5] == customer_id:
                if subscription_status == True:
                    subscription_status = "active"
                else:
                 subscription_status = "inactive"    
                # save the details to DB
                cursor.execute("""UPDATE users SET subscription_status = %s,subscription_plan=%s WHERE customer_id=%s  """,(subscription_status,price_id,customer_id))
                
                current_app.logger.info(f"Successfully saved {user[1]}'s details.\nsubscription_status: {subscription_status}\nprice_id: {price_id}")

    elif event.type == 'payment_intent.succeeded':
        current_app.logger.info(event.data.object)


    elif event.type == 'subscription_schedule.canceled':
        stripe_subscription = event.data.object
        customer_id = stripe_subscription['customer']
        price_id = stripe_subscription['phases'][0]['items'][0]['price']
        status = stripe_subscription['status']

   
        print(customer_id) #  cus_OaC5Zh9VxqAuun  subscription_schedule.canceled
        print(price_id)# price_1Nn1gyAEZk4zaxmwzI8QaVIO
        print(status)# canceled
       
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE customer_id= %s ', (customer_id,))
        user = cursor.fetchone()
    
        if user is not None:
                cursor.execute('UPDATE users SET subscription_plan=%s, subscription_status=%s WHERE customer_id= %s ',("inactive",None,customer_id))
                db.commit()
                current_app.logger.info('Customer subscription canceled, plan succesfully deleted')

       
        
    return jsonify({'status': 'successfull'})

   
@bp.route('/customer-portal', methods=['POST','GET'])
@login_required
def customer_portal():
    # Get the user session email
    email = session.get('email')
   

    if email:
        # Retrieve user information
        user = get_user_by_email(email)
        
        if user:
            customer_id =user[5]
                      
            if customer_id is not None  :

                try:
                
                    # Create the customer portal session
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
    # If email is missing or user does not have required attributes, handle the error
    return redirect(url_for('index', _anchor='plans'))



    
    
@bp.route('/customer-portal-redirect')
def customer_portal_redirect():
    return redirect(url_for('index')) 



