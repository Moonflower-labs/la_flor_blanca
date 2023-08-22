import os
from flask import redirect,Blueprint,session,render_template,url_for
from flor_blanca.postDb import save_customer_id, get_user_by_email, get_db
from flor_blanca.auth import login_required
import stripe
from flask import  jsonify, request, redirect,flash



stripe.api_key = os.environ.get('STRIPE_SECRET_KEY') 
bp = Blueprint('stripe', __name__,)



@bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    price_id = request.form.get('price_id') 

    if price_id is not None:
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
            )
       
            return redirect(checkout_session.url, code=303)    
        
        except Exception as e:
            return str(e)
    


@bp.route('/success')
def success():

    return render_template('checkout/success.html')

@bp.route('/cancel')
def cancel():

    return render_template('checkout/cancel.html')


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
        print("Error while decoding event!")
        return jsonify({'error': str(e)})
    
    except stripe.error.SignatureVerificationError as e:
        print("Invalid signature!")
        return jsonify({'error': str(e)})
    

    #* Check  event type: 'checkout.session.completed', 'customer.subscription.updated'
    if event.type == 'checkout.session.completed' :  
        stripe_session = event.data.object

        # Retrieve the customer ID from the completed checkout session
        customer_id = stripe_session['customer']
       
        # Retrieve the customer object from the Stripe API
        customer = stripe.Customer.retrieve(customer_id)
        
        # Retrieve the email from the customer object
        email = customer.email
      
        get_user_by_email(email)
        
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
                
                print(f"Successfully saved {user[1]}'s details.\nsubscription_status: {subscription_status}\nprice_id: {price_id}")


    elif event.type == 'subscription_schedule.canceled':
        stripe_subscription = event.data.object
        customer_id = stripe_subscription['customer']
        price_id = stripe_subscription['phases'][0]['items'][0]['price']
        status = stripe_subscription['status']

     # !  TODO  update users details
        print(customer_id)
        print(price_id)
        print(status)
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE customer_id= %s ', (customer_id,))
        user = cursor.fetchone()
    
        if user is not None:

            pass

        # !  TODO  update users details remove plan and det INACTIVE
        
    return jsonify({'status': 'successfull'})

@bp.route('/customer-portal', methods=['POST'])
@login_required
def customer_portal():
    # Get the user session email
    email = session.get('email')
   

    if email:
        # Retrieve user information
        user = get_user_by_email(email)
       
        if user:
            # Check if user has necessary attributes
            if user[6] and user[8]:
                # Create the customer portal session
                billing_session = stripe.billing_portal.Session.create(
                    customer=user['customer_id'],
                    return_url=url_for('stripe.customer_portal_redirect', _external=True)
                )

                return redirect(billing_session.url)
            else:
                flash("No pudimos encontrar una suscripcion asociada a tu cuenta")

    flash("Debes comprar una suscripción antes de acceder al Customer portal ")
    # If email is missing or user does not have required attributes, handle the error
    return redirect(url_for('index', _anchor='plans'))



    
    
@bp.route('/customer-portal-redirect')
def customer_portal_redirect():
    return redirect(url_for('index')) 



