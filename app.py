import os
from flask import Flask, request, session, redirect, url_for, render_template_string
import requests

app = Flask(__name__)
# تأمين الجلسة (Session)
app.secret_key = os.getenv('SECRET_KEY', 'default_random_key_123')

# جلب رابط الويب هوك من إعدادات Render
DISCORD_WEBHOOK_URL = os.getenv('https://discord.com/api/webhooks/1486930234837176320/YUaF_3uDpGJ5whtPFY3lOhFHekYwK-1wOmH8Gt_5fLj1Th73LnFRBfxUfKnItLDMahbx')

# قائمة المنتجات
PRODUCTS = {
    "1": {"name": "بوت حماية (Protection)", "price": "50 SAR", "desc": "حماية كاملة ضد التخريب."},
    "2": {"name": "بوت ألعاب (Games)", "price": "70 SAR", "desc": "نظام اقتصاد وفعاليات."},
    "3": {"name": "بوت إداري (Admin)", "price": "40 SAR", "desc": "ترحيب وتنظيم رتب."}
}

# --- التصميم البصري (CSS & HTML) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>متجر ديسكورد</title>
    <style>
        :root { --main: #5865F2; --bg: #23272a; --card: #2c2f33; }
        body { background: var(--bg); color: white; font-family: sans-serif; text-align: center; padding: 20px; }
        .card { background: var(--card); border-radius: 10px; padding: 15px; margin: 10px; border: 1px solid #444; display: inline-block; width: 260px; }
        input, textarea { width: 90%; padding: 10px; margin: 10px 0; border-radius: 5px; background: #1e1e1e; color: white; border: 1px solid #444; }
        button { background: var(--main); color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer; width: 100%; font-weight: bold; }
        .success { color: #3ba55c; background: #2d3d33; padding: 15px; border-radius: 10px; }
    </style>
</head>
<body>
    <h1>🚀 متجر برمجة بوتات ديسكورد</h1>
    <hr style="border: 0.5px solid #444; margin-bottom: 30px;">
    
    {% if page == 'login' %}
        <div style="max-width: 350px; margin: auto; background: var(--card); padding: 25px; border-radius: 15px;">
            <h3>تسجيل دخول</h3>
            <form method="POST" action="/login">
                <input type="tel" name="phone" placeholder="أدخل رقم الجوال (05xxxxxxxx)" required>
                <button type="submit">دخول</button>
            </form>
        </div>
    {% elif page == 'store' %}
        <p>مرحباً: <b>{{ phone }}</b> | <a href="/logout" style="color: #ed4245;">خروج</a></p>
        <div>
            {% for id, item in products.items() %}
            <div class="card">
                <h3>{{ item.name }}</h3>
                <p style="font-size: 0.9em; color: #aaa;">{{ item.desc }}</p>
                <h4 style="color: var(--main);">{{ item.price }}</h4>
                <form method="POST" action="/order/{{ id }}">
                    <textarea name="notes" placeholder="ملاحظاتك..."></textarea>
                    <button type="submit">إرسال الطلب ✅</button>
                </form>
            </div>
            {% endfor %}
        </div>
    {% elif page == 'success' %}
        <div class="success">
            <h2>✅ تم إرسال طلبك بنجاح!</h2>
            <p>سنتواصل معك عبر واتساب أو ديسكورد قريباً.</p>
            <a href="/" style="color: white;">العودة للمتجر</a>
        </div>
    {% endif %}
</body>
</html>
"""

# --- المسارات (Routes) ---

@app.route('/')
def index():
    if 'phone' not in session:
        return render_template_string(HTML_TEMPLATE, page='login')
    return render_template_string(HTML_TEMPLATE, page='store', phone=session['phone'], products=PRODUCTS)

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
    notes = request.form.get('notes', 'بدون ملاحظات')
    
    # إرسال الطلب لديسكورد
    if DISCORD_WEBHOOK_URL:
        payload = {
            "embeds": [{
                "title": "📦 طلب جديد من الموقع",
                "color": 5763719,
                "fields": [
                    {"name": "📱 العميل", "value": session['phone'], "inline": True},
                    {"name": "🤖 المنتج", "value": product['name'], "inline": True},
                    {"name": "📝 الملاحظات", "value": notes}
                ]
            }]
        }
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    
    return render_template_string(HTML_TEMPLATE, page='success')

if __name__ == '__main__':
    app.run(debug=True)
