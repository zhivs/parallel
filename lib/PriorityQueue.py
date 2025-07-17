import multiprocessing

class PriorityQueue():
    def __init__(self):
        self.queue = multiprocessing.Queue()

        proxy = multiprocessing.Manager()
        self.namespace  = proxy.Namespace()

        self.lock = multiprocessing.Lock()

        self.namespace.start_times = proxy.dict()  # время добавления элемента
        self.namespace.wait_times = proxy.list() # время ожидания задачи в очереди для расчета среднего
        
        self.namespace.removed_count = 0    #Количество покинутых задач
        self.namespace.total_wait_time = 0  #Общее время ожидания

    def put(self, subtask):
            with self.lock:
            # Вставляем элемент в очередь с приоритетом
                self.queue.put(subtask)
                #self.namespace.start_times[subtask['id']] = time.time()  # Запоминаем время добавления элемента

    def get(self):
        with self.lock:
        # Извлекаем все элементы, чтобы найти наивысший приоритет
            subtasks = []
            while not self.queue.empty():
                subtasks.append(self.queue.get())

            # Сортируем элементы по приоритету (наименьший приоритет - наивысший)

            sorted_subtasks = sorted(subtasks, key=lambda x: x['priority'])
            
            # Извлекаем элемент с наивысшим приоритетом
            highest_priority_subtask = sorted_subtasks[0] if len(sorted_subtasks) != 0 else None

            if highest_priority_subtask is None:
                return 
        
            # Возвращаем остальные элементы обратно в очередь
            for subtask in sorted_subtasks[1:]:
                self.queue.put(subtask)

            #self.namespace.removed_count += 1

            #wait_time = 0# time.time() - self.namespace.start_times.pop(highest_priority_subtask['id'])
            
            #self.namespace.total_wait_time += wait_time
            #self.namespace.wait_times.append(wait_time) # Увеличиваем количество покинутых подзадач

            return highest_priority_subtask

    def qsize(self):
        with self.lock:
            return self.queue.qsize()

    def average_wait_time(self):
        with self.lock:
            """Возвращает среднее время ожидания подзадач в очереди."""
            return round(self.namespace.total_wait_time / len(self.namespace.wait_times), 5) if self.namespace.wait_times else 0
    
    def removed_count(self):
        with self.lock:
            """Возвращает количество покинутых подзадач."""
            return self.namespace.removed_count
    