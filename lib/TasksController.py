import time

class TasksController:
    def __init__(self):
        self.generation_start_timestamp = time.time()

        self.check_interval_sec    = 1 #раз в сколько проверять значения статистики
        self.delta_time            = 1

        self.curr_input_flow = []
        self.avg_input_flow  = []

        self.solved_tasks_check_interval = 1

    def send_subtasks_to_queue(self, subtask_array, subtasks_queue, namespace, stop_event):
        while not stop_event.is_set():
            subtasks_copy = list(subtask_array)
            if(len(subtasks_copy) == 0):
                continue                   

            input_flow = 0
            for subtask in subtasks_copy:
                subtask_array.remove(subtask)
                subtask["priority"] = self.get_subtask_priority(subtask)
                subtasks_queue.put(subtask)

                input_flow += subtask['execution_time_sec']
            
            self.curr_input_flow.append(input_flow)
            if(time.time() >= self.generation_start_timestamp + self.delta_time):
                self.avg_input_flow.append(sum(self.curr_input_flow))
                self.curr_input_flow = []

                #Нормируем отрезок (не всегда ровно попадаем)
                norming = time.time() - self.generation_start_timestamp - self.delta_time
                namespace.input_flow = sum(self.avg_input_flow) / (self.delta_time + norming)
                
                self.delta_time += self.check_interval_sec


    def send_failed_subtasks_to_queue(self, failed_subtasks, subtasks_queue, stop_event):
        while not stop_event.is_set():
            while failed_subtasks.qsize() != 0:
                failed_task = failed_subtasks.get()
                #failed_task["priority"] = 0
                subtasks_queue.put(failed_task)               
                

    def get_subtask_priority(self, task):
        if task['execution_time_sec'] < 2:
            return 0
        if task['execution_time_sec'] < 3:
            return 1
        if task['execution_time_sec'] < 5:
            return 2
        if task['execution_time_sec'] < 10:
            return 3
        
        return 4

#Кажыде 300 секунд считам, потом окно
    def calc_productivity(self, solved_tasks, executor_namespace, stop_event):
        accumulation_time_sec = 300  # время, в течение которого копим значения продуктивности
        
        is_accumulation_finished = False #Флаг оконачания накопления продуктивности

        check_time = 10 #раз в сколько узнавать значение продуктивности 

        from lib.Task import Task
        taskExecTimeByType = Task.get_task_exec_time_dict()

        t1 = self.generation_start_timestamp
        t2 = self.generation_start_timestamp + accumulation_time_sec
        while not stop_event.is_set():
            if not is_accumulation_finished:
                is_accumulation_finished = True if time.time() >= self.generation_start_timestamp + accumulation_time_sec else False
                time.sleep(check_time)
                continue
            
            cur_productivity = 0 
            for index, solved_tasks_by_type in enumerate(solved_tasks):
                # Фильтруем задачи, решенные до filter_timestamp
                filtered_tasks = [ts for ts in solved_tasks_by_type if ts >= t1 and ts <= t2]

                # Увеличиваем производительность на основе количества отфильтрованных задач
                cur_productivity += len(filtered_tasks) * taskExecTimeByType[index]
            
            #Смещаем отрезок проверки
            t1 += check_time
            t2 += check_time

            executor_namespace.productivity = cur_productivity
            
            time.sleep(check_time)

    def switch_solved_tasks_checker_flag(self, executor_namespace, stop_event):     
        while not stop_event.is_set():
            time.sleep(self.solved_tasks_check_interval)
            executor_namespace.solved_tasks_checker_flag += 1


    def subtasks_statistic(self, executor_namespace, subtasks_queue, solved_tasks, stop_event):

        tasks_in_queue = []
        while not stop_event.is_set():           
            time.sleep(100) #задержка для проверки статистики

            cur_tasks_count = subtasks_queue.qsize()
            tasks_in_queue.append(cur_tasks_count)

            if len(tasks_in_queue) > 5:
                tasks_in_queue.pop(0)

            avg_tasks_count = int(sum(tasks_in_queue) / len(tasks_in_queue)) if len(tasks_in_queue) != 0 else 0
            
            print(
                "In queue: {}. Avg count: {}. Lefted subtasks: {}. Solved: {} => [{},{},{},{}]. Failed: {} => [{},{},{},{}]. Wasted time: {} => [{},{},{},{}]. Productivity: {}".format(
                    cur_tasks_count,
                    avg_tasks_count,
                    #subtasks_queue.average_wait_time(),
                    subtasks_queue.removed_count(),
                    sum(len(inner_list) for inner_list in solved_tasks),
                    len(solved_tasks[0]),
                    len(solved_tasks[1]),
                    len(solved_tasks[2]),
                    len(solved_tasks[3]),
                    sum(executor_namespace.each_type_failed_subtasks_count),
                    executor_namespace.each_type_failed_subtasks_count[0],
                    executor_namespace.each_type_failed_subtasks_count[1],
                    executor_namespace.each_type_failed_subtasks_count[2],
                    executor_namespace.each_type_failed_subtasks_count[3],
                    sum(len(inner_list) for inner_list in executor_namespace.each_type_wasted_tasks_count),
                    len(executor_namespace.each_type_wasted_tasks_count[0]),
                    len(executor_namespace.each_type_wasted_tasks_count[1]),
                    len(executor_namespace.each_type_wasted_tasks_count[2]),
                    len(executor_namespace.each_type_wasted_tasks_count[3]),
                    executor_namespace.productivity
                )
            )
