import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

img = Image.open('test.jpg').resize((224, 224))
img_arr = np.array(img) / 255.0

fig, ax = plt.subplots(figsize=(6, 4))
colors = ('r', 'g', 'b')
for i, c in enumerate(colors):
    # ravel() разворачивает двумерный канал в одномерный массив значений
    ax.hist(img_arr[:, :, i].ravel(), bins=50, color=c, alpha=0.5, label=c.upper())
ax.set_title('Распределение цветов')
ax.set_xlabel('Интенсивность')
ax.set_ylabel('Количество пикселей')
ax.legend()
fig.savefig('color_plot.png')
print('Сохранено: color_plot.png')