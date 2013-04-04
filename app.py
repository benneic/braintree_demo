import braintree

from flask import Flask, request, render_template, make_response
app = Flask(__name__)

import config


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
    bt_signature_param = request.args.get('bt_signature_param')
    bt_payload_param = request.args.get('bt_payload_param')
    if bt_signature_param and bt_payload_param:
        hook = braintree.WebhookNotification.parse(bt_signature_param, bt_payload_param)
        app.logger.warning('Webhook {kind} - id:{subscription_id} price:{price}'.format(
            kind=hook.kind,
            subscription_id=hook.subscription.id,
            price=hook.subscription.price
        ))
    return



@app.route('/plan', methods=["POST"])
def create_customer():

    required_fields = ('package','company','email','first_name','last_name','postal_code','number','month','year','cvv')
    not_found = check_fields(request.form, required_fields)
    if not_found:
        return make_response('<h1>Required form field missing: %s</h1>' % not_found, 500)

    customer = None
    package = request.form['package']
    customer_id = request.form.get('customer_id')
    if customer_id:
        customer = braintree.Customer.find(customer_id)
    if not isinstance(customer, braintree.Customer):
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
        result = braintree.Customer.create(customer)
        if result.is_success:
            customer = result.customer
        else:
            return "<h1>New Customer Error: {0}</h1>".format(result.message)

    payment_method_token = customer.credit_cards[0].token

    result = braintree.Subscription.create({
        "payment_method_token": payment_method_token,
        "plan_id": package
    })
    if not result.is_success:
        return "<h1>New Subscription Error: {0}</h1>".format(result.message)

    return render_template("response.html",
                           status=result.subscription.status,
                           plans=config.PLANS,
                           package=package,
                           customer=customer)


if __name__ == '__main__':
    app.run(debug=True)
