from flask import Flask, render_template
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use('Agg')  # без GUI — обязательно для сервера
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import os

# ============================================================
# Создание приложения Flask
# ============================================================
app = Flask(__name__)
app.testing = True
# Секретный ключ для CSRF-защиты форм (может быть любой строкой)
app.config['SECRET_KEY'] = 'secret'

# Настройки капчи reCAPTCHA.
# Ключи получим на шаге 4.5 — пока оставьте заглушки.
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lcm0MotAAAAANevH-H3K2-jc1ys9d4qvC01ssCW'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Lcm0MotAAAAACj61zQq7s2yx0WUOR0vReTx1KGQ'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}

# Подключаем Bootstrap (для красивого оформления форм)
Bootstrap(app)


# ============================================================
# Класс формы
# ============================================================
class NoiseForm(FlaskForm):
    """Форма: загрузка картинки + уровень шума + капча."""
    upload = FileField('Картинка', validators=[
        FileRequired(message='Загрузите файл'),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')
    ])
    noise_level = FloatField(
        'Уровень шума (0..1)',
        validators=[DataRequired(), NumberRange(0, 1)],
        default=0.3
    )
    recaptcha = RecaptchaField()
    submit = SubmitField('Отправить')


# ============================================================
# Вспомогательные функции
# ============================================================
def add_noise(image, level):
    """
    Добавляет равномерный шум к изображению.
    image — numpy-массив формы (H, W, 3) со значениями 0..1.
    level — уровень шума 0..1.
    Возвращает numpy-массив той же формы со значениями 0..1.
    """
    # Случайный шум в диапазоне [-0.5, 0.5], умноженный на level
    noise = (np.random.rand(*image.shape) - 0.5) * level
    noisy = image + noise
    # Нормируем обратно в [0, 1]
    noisy = (noisy - noisy.min()) / (noisy.max() - noisy.min() + 1e-9)
    return noisy


def color_plot(image, title):
    """
    Строит график распределения цветов (гистограмма R, G, B).
    Возвращает base64-строку PNG-изображения.
    """
    fig, ax = plt.subplots(figsize=(5, 3))
    for i, c in enumerate(('r', 'g', 'b')):
        # ravel() превращает 2D-канал в 1D-массив значений
        ax.hist(image[:, :, i].ravel(), bins=50, color=c, alpha=0.5, label=c.upper())
    ax.set_title(title)
    ax.set_xlabel('Интенсивность')
    ax.set_ylabel('Количество пикселей')
    ax.legend()
    # Сохраняем в буфер и кодируем в base64
    buf = BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


# ============================================================
# Маршруты
# ============================================================
@app.route("/")
def hello():
    """Корневая страница — просто проверка."""
    return "<h1>Hello World!</h1>"


@app.route("/noise", methods=['GET', 'POST'])
def noise():
    """Главная страница приложения."""
    form = NoiseForm()
    filename = None
    orig_plot = None
    noisy_plot = None

    if form.validate_on_submit():
        # --- 1. Сохраняем загруженный файл в static ---
        # secure_filename убирает опасные символы из имени
        filename = os.path.join('static', secure_filename(form.upload.data.filename))
        form.upload.data.save(filename)

        # --- 2. Читаем картинку, приводим к 224x224 ---
        img = Image.open(filename).convert('RGB').resize((224, 224))
        img_arr = np.array(img) / 255.0  # значения 0..1

        # --- 3. Зашумляем ---
        noisy = add_noise(img_arr, form.noise_level.data)

        # --- 4. Сохраняем зашумлённую картинку ---
        Image.fromarray((noisy * 255).astype(np.uint8)).save('static/noisy.png')

        # --- 5. Строим графики ---
        orig_plot = color_plot(img_arr, 'Исходная')
        noisy_plot = color_plot(noisy, 'Зашумлённая')

    # Если форма не отправлена — просто показываем пустую форму
    return render_template('noise.html',
                           form=form,
                           filename=filename,
                           orig_plot=orig_plot,
                           noisy_plot=noisy_plot)


# ============================================================
# Точка входа
# ============================================================
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)