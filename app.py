from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)

# Sowix API URL
SOWIX_API_URL = "https://api.sowixvip.xyz/sowixapi/tcpro.php?tc="

# İkinci API URL (OnlineLbs API)
ONLINELBS_API_URL = "http://95.0.185.19:64428/online-web/onlinelbs/checkLogin.html"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rapor')
def rapor():
    tc_no = request.args.get('tc')

    if not tc_no:
        return "TC Kimlik No girilmedi!", 400
    
    # Sowix API'ye istek atma
    try:
        response = requests.get(SOWIX_API_URL + tc_no)
        response_data = response.json()

        if not response_data['success']:
            return "TC Kimlik No geçersiz!", 400
        
        # Doğum tarihi formatı
        dogum_tarihi = response_data['data']['DOGUMTARIHI']
        dogum_tarihi_obj = datetime.strptime(dogum_tarihi, '%Y-%m-%d')
        dogum_tarihi_str = dogum_tarihi_obj.strftime('%d.%m.%Y')

        # OnlineLbs API'ye istek atma
        payload = {
            'recaptchaRes': 'dummyRecaptchaResponse',
            'OnlineLbsTcNo': tc_no,
            'OnlineLbsDogumTarihi': dogum_tarihi_str,
            'OnlineLbsDosyaNo': '',
            'OnlineLbsSonucNo': ''
        }

        online_response = requests.post(ONLINELBS_API_URL, data=payload)
        online_response_data = online_response.text

        return render_template('rapor.html', 
                               data=response_data['data'], 
                               online_response=online_response_data)

    except requests.RequestException as e:
        return f"Bir hata oluştu: {e}", 500


if __name__ == '__main__':
    app.run(debug=True)
