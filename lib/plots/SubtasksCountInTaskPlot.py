import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time 

class SubtasksCountInTaskPlot:
    def __init__(self):
        self.start_time = time.time()

        plt.rcParams.update({
            'font.size': 14,          # Основной размер шрифта
            'axes.titlesize': 16,     # Размер заголовка графика
            'axes.labelsize': 14,     # Размер подписей осей
            'xtick.labelsize': 14,    # Размер меток по оси X
            'ytick.labelsize': 14,    # Размер меток по оси Y
            'legend.fontsize': 12     # Размер шрифта в легенде (если будет)
        })
        
        # Настройка графика
        self.fig, self.ax = plt.subplots()
        self.xdata = []
        self.ydata = []

        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_xlim(0, 1500)  #границы по оси X
        self.ax.set_ylim(0, 1500)  #границы по оси Y
        
        self.ax.set_xlabel('Время генерации, с.')
        self.ax.set_ylabel('Количество подзадач')

        plt.title('Количество подзадач в задачах')

        self.ax.grid()


    def update_subtasks_count_in_tasks_by_time(self, frame, subtasks_count_in_task_queue):
        while not subtasks_count_in_task_queue.empty():
            task = subtasks_count_in_task_queue.get()  # Получаем новое значение из очереди
            
            current_time = task[0] - self.start_time
            subtask_count = task[1]

            self.xdata.append(current_time)  # Добавляем текущее время
            self.ydata.append(subtask_count)  # Значение из очереди
            
            # Обновляем данные линий
            self.line.set_data(self.xdata, self.ydata)

            # Устанавливаем новые границы по оси X
            self.ax.set_ylim(0, subtask_count + 20)
            self.ax.set_xlim(max(0, current_time - 1500), current_time)
            
        return self.line

    def plot_subtasks_count_in_tasks_by_time(self, task_array):
        """Запускает анимацию графика."""
        
        ani = FuncAnimation(self.fig, self.update_subtasks_count_in_tasks_by_time, fargs=(task_array,), frames=np.arange(0, 200), interval=100)
        plt.show()
