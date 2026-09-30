import os

os.chdir(r'c:/Users/fogus/OneDrive/เอกสาร/GitHub/DongPuDee-Main')
import app as webapp

client = webapp.app.test_client()
response = client.get('/page3?checkout=1')
html = response.get_data(as_text=True)
print('status=', response.status_code)
print('payment=', 'ชำระเงิน' in html or 'payment' in html.lower())
print('qr=', 'qr-placeholder' in html or 'static/img/qr-placeholder.svg' in html)
print('checkout=', 'Checkout' in html or 'checkout' in html.lower())
