# Braintree demo

## Sign up

Get an account for the Braintree Sandbox:

[https://sandbox.braintreegateway.com/]

Add some recurring billing plans

## Config

Export your Braintree Sandbox API Keys as environment vars

    export MERCHANT_ID="your_merch_key" PUBLIC_KEY="your_pub_key" PRIVATE_KEY="you_priv_key" CLIENT_SIDE_ENCRYPTION_KEY="your_encryt_key"

Update the PLANS in config.py with the plans you created

    PLANS = {
        'PLAN_1' : 'Mega Package',
        'PLAN_2' : 'Migo Package',
    }

## Run

Run the flask app

    pip install -r requirements
    python app.py

Open http://0.0.0.0:5000/ in your browser



