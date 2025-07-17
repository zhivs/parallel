import multiprocessing

class PriorityQueue():
    def __init__(self):
        self.queues = [multiprocessing.Queue(), multiprocessing.Queue(), multiprocessing.Queue(), multiprocessing.Queue(), multiprocessing.Queue()]

        proxy = multiprocessing.Manager()
        self.namespace  = proxy.Namespace()

        self.lock = multiprocessing.Lock()

        #self.namespace.start_times = proxy.dict()  # Хранит время добавления элемента
        self.namespace.wait_times = proxy.list() # Времена ожидания для расчета среднего
        
        self.namespace.lefted_taskcount = 0    #Количество покинутых элементов
        self.namespace.total_wait_time = 0  #Общее время ожидания

    def put(self, subtask):
            #self.namespace.start_times[subtask['id']] = time.time()  # Запоминаем время добавления элемента
            self.queues[subtask['priority']].put(subtask)

    def get(self):
        if not self.queues[0].empty():
            #self.namespace.lefted_taskcount += 1
            return self.queues[0].get()
        
        if not self.queues[1].empty():
            #self.namespace.lefted_taskcount += 1
            return self.queues[1].get() 
        
        if not self.queues[2].empty():
            #self.namespace.lefted_taskcount += 1
            return self.queues[2].get()
        
        if not self.queues[3].empty():
            #self.namespace.lefted_taskcount += 1
            return self.queues[3].get()
        
        if not self.queues[4].empty():
            #self.namespace.lefted_taskcount += 1
            return self.queues[4].get()

    def qsize(self):
        return self.queues[0].qsize() + self.queues[1].qsize() + self.queues[2].qsize() + self.queues[3].qsize() + self.queues[4].qsize()

    def average_wait_time(self):
        
        """Возвращает среднее время ожидания подзадач в очереди."""
        return round(self.namespace.total_wait_time / len(self.namespace.wait_times), 5) if self.namespace.wait_times else 0
    
    def removed_count(self):
        """Возвращает количество покинутых подзадач."""
        return 0#self.namespace.lefted_taskcount
    