from cgi import parse_qs
from logging import debug
from urllib import quote

from google.appengine.api.urlfetch import *

class PayPalPro():

	endpoint = ''
	paypal_url = ''
	version = '64'
	username = ''
	password = ''
	signature = ''

	def __init__(self, sandbox, username, password, signature):
		if sandbox:
			self.endpoint = 'https://api-3t.sandbox.paypal.com/nvp'
			self.paypal_url = 'https://www.sandbox.paypal.com/webscr?cmd=_express-checkout&token='
		else:
			self.endpoint = 'https://api-3t.paypal.com/nvp'
			self.paypal_url = 'https://www.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token='
		self.username = username
		self.password = password
		self.signature = signature

	def urlencode(self, string):
		return quote(string.encode('utf-8'))

	def call(self, method, params):
		params = 'METHOD=' + self.urlencode(method) + \
			'&VERSION=' + self.urlencode(self.version) + \
			'&USER=' + self.urlencode(self.username) + \
			'&PWD=' + self.urlencode(self.password) + \
			'&SIGNATURE=' + self.urlencode(self.signature) + \
			params
		response = fetch(self.endpoint, payload = params, method = POST)
		response_values = None
		if response:
			debug('raw response: '+str(response.content))
			values = parse_qs(response.content)
			if values:
				for value in values:
					values[value] = values[value][0]
				if values['ACK'] == 'Success':
					response_values = values
		return response_values

	def get_express_checkout_url(self, type, amount, currency, return_url, cancel_url):
		params = '&PAYMENTREQUEST_0_AMT=' + self.urlencode(amount) + \
			'&PAYMENTREQUEST_0_PAYMENTACTION=' + self.urlencode(type) + \
			'&RETURNURL=' + self.urlencode(return_url) + \
			'&CANCELURL=' + self.urlencode(cancel_url) + \
			'&PAYMENTREQUEST_0_CURRENCYCODE=' + self.urlencode(currency)
		response = self.call('SetExpressCheckout', params)
		url = None
		if response:
			if response['TOKEN']:
				url = self.paypal_url + response['TOKEN']
		return url

	def get_express_checkout_details(self, token):
		params = '&TOKEN=' + self.urlencode(token)
		response = self.call('GetExpressCheckoutDetails', params)
		debug('response: '+str(response))
		details = None
		if response:
			details = {}
			details['payer_id']		 = response['PAYERID']
			details['first_name']	 = response['FIRSTNAME']
			details['last_name']	 = response['LASTNAME']
			details['amount']		 = response['PAYMENTREQUEST_0_AMT']
			details['currency']		 = response['PAYMENTREQUEST_0_CURRENCYCODE']
		return details

	def complete_express_checkout(self, token, details = None):
		success = False
		if not details:
			details = self.get_express_checkout_details(token)
		if details:
			params = '&TOKEN=' + self.urlencode(token) + \
				'&PAYERID=' + self.urlencode(details['payer_id']) + \
				'&PAYMENTREQUEST_0_AMT=' + self.urlencode(details['amount']) + \
				'&PAYMENTREQUEST_0_CURRENCYCODE=' + self.urlencode(details['currency'])
			response = self.call('DoExpressCheckoutPayment', params)
			debug('response: '+str(response))
			success = True
		return success

	def direct_payment(self, card_type, card_number,
					   card_expiration, card_cvv2, first_name, last_name,
					   street, city, state, zip, country_code,
					   amount, currency):
		params = '&CREDITCARDTYPE=' + card_type + \
			'&ACCT=' + card_number + \
			'&EXPDATE=' + card_expiration + \
			'&CVV2=' + card_cvv2 + \
			'&FIRSTNAME=' + first_name + \
			'&LASTNAME=' + last_name + \
			'&STREET=' + street + \
			'&CITY=' + city + \
			'&STATE=' + state + \
			'&ZIP=' + zip + \
			'&COUNTRYCODE=' + country_code + \
			'&AMT=' + amount + \
			'&CURRENCYCODE=' + currency
		success = False
		response = self.call('DoDirectPayment', params)
		if response:
			success = True
		return success
