import braintree

from flask import Flask, request, render_template, make_response
app = Flask(__name__)

import config

if app.debug:
    logger = app.logger
else:
    import logging as logger
    logger.basicConfig(level=logger.INFO)


braintree.Configuration.configure(braintree.Environment.Sandbox,
                                  merchant_id=config.MERCHANT_ID,
                                  public_key=config.PUBLIC_KEY,
                                  private_key=config.PRIVATE_KEY)

braintree.Configuration.use_unsafe_ssl = True


def check_fields(container, fields):
    for field in fields:
        value = container.get(field, '').strip()
        if not value:
            return field
    return None


@app.route("/")
def form():
    return render_template("braintree.html", plans=config.PLANS)


@app.route("/webhook")
def webhook_register():
    bt_challenge = request.args.get('bt_challenge')
    return braintree.WebhookNotification.verify(bt_challenge)


@app.route("/webhook", methods=["POST"])
def webhook_action():
    logger.info('Webhook params: %s' % dict(request.form).keys())
    signature = request.form.get('bt_signature', type=str)
    payload = request.form.get('bt_payload', type=str)
    if signature and payload:
        hook = braintree.WebhookNotification.parse(signature, payload)
        logger.info('Webhook {kind} - id:{subscription_id} price:{price}'.format(
            kind=hook.kind,
            subscription_id=hook.subscription.id,
            price=hook.subscription.price
        ))
    return unicode(dict(request.form))



@app.route('/plan', methods=["POST"])
def create_customer():
    customer = None
    package = request.form['package']
    customer_id = request.form.get('customer_id')
    if customer_id:
        try:
            customer = braintree.Customer.find(customer_id)
        except Exception as e:
            pass

    if not customer:
        required_fields = ('package','company','email','first_name','last_name','postal_code','number','month','year','cvv')
        not_found = check_fields(request.form, required_fields)
        if not_found:
            return make_response('<h1>Required form field missing: %s</h1>' % not_found, 500)

        customer = {
            "company": request.form['company'],
            "email": request.form['email'],
            "first_name": request.form["first_name"],
            "last_name": request.form["last_name"],
            "credit_card": {
                "billing_address": {
                    "postal_code": request.form["postal_code"]
                },
                "number": request.form["number"],
                "expiration_month": request.form["month"],
                "expiration_year": request.form["year"],
                "cvv": request.form["cvv"]
            }
        }
        if customer_id:
            customer['id'] = customer_id
            customer['credit_card']['token'] = customer_id
        result = braintree.Customer.create(customer)
        if result.is_success:
            customer = result.customer
        else:
            return "<h1>New Customer Error: {0}</h1>".format(result.message)

    payment_method_token = customer.credit_cards[0].token

    result = braintree.Subscription.create({
        'id': customer.id,
        "payment_method_token": payment_method_token,
        "plan_id": package
    })
    if not result.is_success:
        return "<h1>New Subscription Error: {0}</h1>".format(result.message)

    return render_template("response.html",
                           subscription=result.subscription,
                           plans=config.PLANS,
                           package=package,
                           customer=customer)


if __name__ == '__main__':
    app.run(debug=True)
