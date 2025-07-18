from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'static/music'
COVER_FOLDER = 'static/covers'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['COVER_FOLDER'] = COVER_FOLDER

# ایجاد پوشه‌ها در صورت نیاز
for folder in [UPLOAD_FOLDER, COVER_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# صفحه ورود ادمین
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == '1234':  # رمز ورود قابل تغییر
            session['admin'] = True
            return redirect(url_for('index'))
        else:
            return 'رمز اشتباه است!'
    return render_template('login.html')

# خروج ادمین
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

# صفحه اصلی با قابلیت جستجو
@app.route('/')
def index():
    query = request.args.get('search', '').lower()
    music_files = os.listdir(UPLOAD_FOLDER)
    music_list = []

    for filename in music_files:
        if filename.endswith('.mp3') or filename.endswith('.wav'):
            name = filename.lower()
            if query in name:
                category = 'ریمیکس' if 'remix' in filename.lower() else 'معمولی'
                cover_path = f"{COVER_FOLDER}/{os.path.splitext(filename)[0]}.jpg"
                cover_exists = os.path.exists(cover_path)
                music_list.append({
                    'name': filename,
                    'category': category,
                    'cover': f"/{cover_path}" if cover_exists else None
                })

    return render_template('index.html', music_list=music_list, admin=session.get('admin', False), search=query)

# آپلود آهنگ و کاور (فقط برای ادمین)
@app.route('/upload', methods=['POST'])
def upload_file():
    if not session.get('admin'):
        return 'دسترسی ندارید!'

    music = request.files.get('music')
    cover = request.files.get('cover')

    if music:
        music.save(os.path.join(app.config['UPLOAD_FOLDER'], music.filename))
        if cover:
            base = os.path.splitext(music.filename)[0]
            cover.save(os.path.join(app.config['COVER_FOLDER'], base + '.jpg'))
        return redirect(url_for('index'))

    return 'فایل موسیقی الزامی است.'

# حذف آهنگ (فقط برای ادمین)
@app.route('/delete/<filename>')
def delete_file(filename):
    if not session.get('admin'):
        return 'دسترسی ندارید!'

    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(path):
        os.remove(path)
    # حذف کاور همزمان
    cover_path = os.path.join(app.config['COVER_FOLDER'], os.path.splitext(filename)[0] + '.jpg')
    if os.path.exists(cover_path):
        os.remove(cover_path)
    return redirect(url_for('index'))

# دانلود موزیک
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# اجرای برنامه
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)