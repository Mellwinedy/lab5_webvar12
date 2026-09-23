import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')  # без графического окна
import matplotlib.pyplot as plt

# 1. Загружаем картинку и приводим к 224x224
img = Image.open('test.jpg').resize((224, 224))
print('Форма массива:', np.array(img).shape)  # (224, 224, 3)

# 2. Приводим к диапазону [0, 1]
img_arr = np.array(img) / 255.0
print('Мин/макс до шума:', img_arr.min(), img_arr.max())

# 3. Зашумляем
level = 0.3
noise = (np.random.rand(*img_arr.shape) - 0.5) * level
noisy = img_arr + noise

# 4. Нормируем обратно в [0, 1]
noisy = (noisy - noisy.min()) / (noisy.max() - noisy.min() + 1e-9)
print('Мин/макс после шума:', noisy.min(), noisy.max())

# 5. Сохраняем результат для просмотра
Image.fromarray((noisy * 255).astype(np.uint8)).save('noisy_test.png')
print('Сохранено: noisy_test.png')