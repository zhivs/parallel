import multiprocessing
import time

class FIFOQueue:
    def __init__(self):
        self.queue = multiprocessing.Queue()

        proxy = multiprocessing.Manager()
        self.namespace  = proxy.Namespace()

        self.namespace.start_times = proxy.dict()  # Хранит время добавления элемента
        self.namespace.wait_times = proxy.list() # Времена ожидания для расчета среднего
        
        self.namespace.removed_count = 0    #Количество покинутых элементов
        self.namespace.total_wait_time = 0  #Общее время ожидания

    def put(self, subtask):
            self.queue.put(subtask)

            self.namespace.start_times[subtask['id']] = time.time()  # Запоминаем время добавления элемента


    def get(self):
            subtask = self.queue.get()
            self.namespace.removed_count += 1 # Увеличиваем количество покинутых очередь подзадач

            if subtask['id'] not in self.namespace.start_times:
                return

            wait_time = time.time() - self.namespace.start_times.pop(subtask['id'])
            
            self.namespace.total_wait_time += wait_time
            self.namespace.wait_times.append(wait_time)

            return subtask

    def qsize(self):
        return self.queue.qsize()

    def average_wait_time(self):
        """Возвращает среднее время ожидания подзадач в очереди."""
        return round(self.namespace.total_wait_time / len(self.namespace.wait_times), 5) if self.namespace.wait_times else 0
    
    def removed_count(self):
        """Возвращает количество покинутых подзадач."""
        return self.namespace.removed_count
