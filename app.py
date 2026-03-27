import os
from flask import Flask, request, session, redirect, url_for, render_template_string
import requests

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# قراءة الويب هوك من إعدادات Render لزيادة الأمان
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# قائمة المنتجات
PRODUCTS = {
    "1": {"name": "بوت حماية (Protection Bot)", "price": "50 SAR", "desc": "حماية كاملة ضد التخريب والروابط."},
    "2": {"name": "بوت ألعاب (Games Bot)", "price": "70 SAR", "desc": "فعاليات وألعاب اقتصادية متطورة."},
    "3": {"name": "بوت إداري (Admin Bot)", "price": "40 SAR", "desc": "تنظيم الرتب والترحيب التلقائي."}
}

# --- التصميم البصري (CSS & HTML) ---
BASE_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>متجر برمجيات ديسكورد</title>
    <style>
        :root { --discord-blurple: #5865F2; --dark-bg: #23272a; --card-bg: #2c2f33; }
        body { background-color: var(--dark-bg); color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; text-align: center; }
        .container { max-width: 900px; margin: auto; }
        .card { background: var(--card-bg); border-radius: 12px; padding: 20px; margin: 15px; border: 1px solid #444; transition: 0.3s; display: inline-block; width: 250px; vertical-align: top; }
        .card:hover { border-color: var(--discord-blurple); transform: translateY(-5px); }
        input, textarea { width: 90%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #444; background: #1e1e1e; color: white; }
        button { background-color: var(--discord-blurple); color: white; border: none; padding: 12px 25px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 95%; }
        button:hover { background-color: #4752c4; }
        .success-msg { color: #3ba55c; font-weight: bold; background: #2d3d33; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 متجر برمجة بوتات ديسكورد</h1>
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

LOGIN_HTML = """
{% extends "base" %}
{% block content %}
    <div style="max-width: 400px; margin: auto; background: var(--card-bg); padding: 30px; border-radius: 15px;">
        <h3>تسجيل دخول العميل</h3>
        <p>الرجاء إدخال رقم الجوال للمتابعة</p>
        <form method="POST" action="/login">
            <input type="tel" name="phone" placeholder="مثال: 05xxxxxxx" required>
            <button type="submit">دخول</button>
        </form>
    </div>
{% endblock %}
"""

STORE_HTML = """
{% extends "base" %}
{% block content %}
    <p>مرحباً بك: <b>{{ phone }}</b> | <a href="/logout" style="color: #ed4245;">خروج</a></p>
    <div class="products-grid">
        {% for id, item in products.items() %}
        <div class="card">
            <h3>{{ item.name }}</h3>
            <p style="color: #b9bbbe;">{{ item.desc }}</p>
            <h4 style="color: var(--discord-blurple);">{{ item.price }}</h4>
            <form method="POST" action="/order/{{ id }}">
                <textarea name="notes" placeholder="ملاحظات الطلب (اختياري)"></textarea>
                <button type="submit">إتمام الطلب ✅</button>
            </form>
        </div>
        {% endfor %}
    </div>
{% endblock %}
"""

# --- المسارات (Routes) ---

@app.route('/')
def index():
    if 'phone' not in session:
        return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', LOGIN_HTML))
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', STORE_HTML), 
                                phone=session['phone'], products=PRODUCTS)

@app.route('/login', methods=['POST'])
def login():
    session['phone'] = request.form.get('phone')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('phone', None)
    return redirect(url_for('index'))

@app.route('/order/<product_id>', methods=['POST'])
def order(product_id):
    if 'phone' not in session: return redirect(url_for('index'))
    
    product = PRODUCTS.get(product_id)
    notes = request.form.get('notes', 'لا يوجد ملاحظات')
    
    # إرسال البيانات إلى ديسكورد عبر Webhook
    payload = {
        "embeds": [{
            "title": "📦 طلب بوت جديد!",
            "description": f"وصلك طلب جديد من المتجر.",
            "color": 5763719,
            "fields": [
                {"name": "📱 جوال العميل", "value": session['phone'], "inline": True},
                {"name": "🤖 المنتج", "value": product['name'], "inline": True},
                {"name": "💰 السعر", "value": product['price'], "inline": True},
                {"name": "📝 الملاحظات", "value": notes}
            ],
            "footer": {"text": "نظام الطلبات التلقائي"}
        }]
    }
    
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
        return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', 
            '<div class="success-msg">✅ تم إرسال طلبك بنجاح! سنتواصل معك قريباً.</div><br><a href="/" style="color:white;">العودة للمتجر</a>'))
    except Exception as e:
        return f"حدث خطأ أثناء إرسال الطلب: {e}"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
