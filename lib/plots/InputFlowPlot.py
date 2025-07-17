import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time

class InputFlowPlot:
    def __init__(self):
        self.start_time = time.time()
        
        # Настройка графика
        self.fig, self.ax = plt.subplots()

        plt.rcParams.update({
            'font.size': 14,          # Основной размер шрифта
            'axes.titlesize': 16,     # Размер заголовка графика
            'axes.labelsize': 14,     # Размер подписей осей
            'xtick.labelsize': 14,    # Размер меток по оси X
            'ytick.labelsize': 14,    # Размер меток по оси Y
            'legend.fontsize': 12     # Размер шрифта в легенде (если будет)
        })

        self.xdata = []
        self.ydata = []

        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_xlim(0, 1500)  #границы по оси X
        self.ax.set_ylim(0, 1500)  #границы по оси Y

        self.ax.set_xlabel('Время генерации, с.')
        self.ax.set_ylabel('Значение интенсивности')

        plt.title('Средняя интенсивность входного потока')
        self.ax.grid()

        self.scatter = self.ax.scatter([], [])

    def update_input_flow(self, frame, namespace):       
        current_time = time.time() - self.start_time

        self.xdata.append(current_time)  # Добавляем текущее время
        self.ydata.append(namespace.input_flow)  # Значение из очереди
        
        self.line.set_data(self.xdata, self.ydata)

        # Устанавливаем новые границы по оси X
        self.ax.set_xlim(max(0, current_time - 1500), current_time)
        
        self.ax.set_ylim(0, namespace.input_flow + 50)

        return self.ax,

    def plot_input_flow(self, namespace):
        """Запускает анимацию графика."""

        ani = FuncAnimation(self.fig, self.update_input_flow, fargs=(namespace,), frames=np.arange(0, 200), interval=100)
        plt.show()
