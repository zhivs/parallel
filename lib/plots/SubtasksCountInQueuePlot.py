import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time

class SubtasksCountInQueuePlot:
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
        self.ax.set_ylabel('Количество подзадач')

        plt.title('Количество подзадач в очереди')

        self.ax.grid()

        self.scatter = self.ax.scatter([], [])

    def update_subtasks_count_in_queue_by_time(self, frame, subtasks_queue):
        current_time = time.time() - self.start_time
        qsize = subtasks_queue.qsize()

        self.xdata.append(current_time)  # Добавляем текущее время
        self.ydata.append(qsize)  # Значение из очереди
        
        # Обновляем данные линий
        self.line.set_data(self.xdata, self.ydata)
        #self.scatter.set_offsets(np.c_[self.xdata, self.ydata])

        # Устанавливаем новые границы по оси X
        self.ax.set_xlim(max(0, current_time - 1500), current_time)
        
        self.ax.set_ylim(0, qsize + 350)
        
        return self.line,

    def plot_subtasks_count_in_queue_by_time(self, subtasks_queue):
        """Запускает анимацию графика."""
        
        ani = FuncAnimation(self.fig, self.update_subtasks_count_in_queue_by_time, fargs=(subtasks_queue,), frames=np.arange(0, 200), interval=100)
        plt.show()