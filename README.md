# Sample usage

You will receive a username, password and signature when signing up for a PayPal developer account.  Place this info in the get_paypal method.  The transactions are hardcoded for 0.01 USD.

```python
from logging import debug, info, warn, error
from paypal import PayPalPro


class PayPalHandler():

	def get_paypal(self):
		return PayPalPro(
			sandbox = in_sandbox,
			username = your_username,
			password = your_password,
			signature = your_signature
		)


class PayPalExpressHandler(UserRequestHandler):

	def get(self):
		paypal = self.get_paypal()
		checkout_url = paypal.get_express_checkout_url('Order', '0.01', 'USD',
			'http://%s/_paypal/confirm' % self.request.host,
			'http://%s/_paypal/cancel' % self.request.host)
		if checkout_url:
			self.redirect(checkout_url)
		else:
			error('Invalid response from paypal')


class PayPalConfirmHandler(UserRequestHandler):

	def get(self):
	token = self.request.get('token')
	if token:
		paypal = self.get_paypal()
		details = paypal.get_express_checkout_details(token)
		if details:
			debug('details: '+str(details))
		else:
			error('unable to load transaction %s' % token)


class PayPalCancelHandler(UserRequestHandler):

	def get(self):
		debug('user cancelled')


class PayPalCompleteHandler(UserRequestHandler):

	def get(self):
		token = self.request.get('token')
		if token:
			paypal = self.get_paypal()
			success = paypal.complete_express_checkout(token)
			if success:
				debug('order received')
			else:
				error('unable to complete checkout')


class PayPalDirectHandler(UserRequestHandler):

	def post(self):
		first_name	= self.request.get('first_name');
		last_name	= self.request.get('last_name');
		street		= self.request.get('street');
		city		= self.request.get('city');
		state		= self.request.get('state');
		zip			= self.request.get('zip');
		country		= self.request.get('country');
		card_type	= self.request.get('card_type');
		card_number	= self.request.get('card_number');
		card_expiration	= self.request.get('card_expiration');
		card_cvv2	= self.request.get('card_cvv2');
		paypal = self.get_paypal()
		success = paypal.direct_payment(card_type, card_number, card_expiration,
							  card_cvv2, first_name, last_name, street, city,
							  state, zip, country, '0.01', 'USD')
		if success:
			debug('order-received')
		else:
			error('unable to complete checkout')


def main():
	logging.getLogger().setLevel(logging.DEBUG)
	application = WSGIApplication([
		('/_paypal/express', PayPalExpressHandler),
		('/_paypal/confirm', PayPalConfirmHandler),
		('/_paypal/cancel', PayPalCancelHandler),
		('/_paypal/complete', PayPalCompleteHandler),
		('/_paypal/direct', PayPalDirectHandler)
	])
	CGIHandler().run(application)

if __name__ == '__main__':
	main()
```
