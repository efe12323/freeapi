from flask import Flask, request
import requests
from datetime import datetime

app = Flask(__name__)

# Sowix API URL
SOWIX_API_URL = "https://api.sowixvip.xyz/sowixapi/tcpro.php?tc="

# İkinci API URL (OnlineLbs API)
ONLINELBS_API_URL = "http://95.0.185.19:64428/online-web/onlinelbs/checkLogin.html"

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TC Sorgu</title>
    </head>
    <body>
        <h1>TC Kimlik No ile Sorgu</h1>
        <form action="/rapor" method="get">
            <label for="tc">TC Kimlik No:</label>
            <input type="text" id="tc" name="tc" required>
            <button type="submit">Sorgula</button>
        </form>
    </body>
    </html>
    '''

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

        return f'''
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>TC Sorgu Raporu</title>
        </head>
        <body>
            <h1>TC Sorgu Sonucu</h1>

            <h2>API Yanıtı</h2>
            <p><strong>Ad:</strong> {response_data['data']['AD']}</p>
            <p><strong>Soyad:</strong> {response_data['data']['SOYAD']}</p>
            <p><strong>Doğum Tarihi:</strong> {response_data['data']['DOGUMTARIHI']}</p>
            <p><strong>Adres:</strong> {response_data['data']['ADRESIL']} / {response_data['data']['ADRESILCE']}</p>
            <p><strong>Cinsiyet:</strong> {response_data['data']['CINSIYET']}</p>

            <h2>OnlineLbs API Yanıtı</h2>
            <pre>{online_response_data}</pre>

            <a href="/">Geri Dön</a>
        </body>
        </html>
        '''

    except requests.RequestException as e:
        return f"Bir hata oluştu: {e}", 500


if __name__ == '__main__':
    app.run(debug=True)
