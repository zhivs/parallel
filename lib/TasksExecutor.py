import time
import random

class TasksExecutor:
    executor_error_probability = 0.03#0.01  # 1% ошибка системы на каждой итерации цикла

    executor_recovery_time_sec = 2  # Время восстановления вычислителя
    
    def execute_tasks(self, subtask_queue, solved_tasks, failed_subtasks, executor_namespace, stop_event):
        self.solved_tasks_checker_flag = executor_namespace.solved_tasks_checker_flag
        while not stop_event.is_set():

            task = subtask_queue.get()
            
            #В очереди нет задач
            if task is None:
                continue

            # Задача была уже решена, пропускаем итерацию цикла, берем следующую
            if task["task_timestamp"] in solved_tasks[task["task_type"]]:
                continue
            
            calculated_task_info = self.execute_task(task, solved_tasks, executor_namespace)
            
            #Счетчик всех решенных задач (даже если не было решения)
            #if calculated_task["is_solved"]:
            #    executor_namespace.each_type_solved_subtasks_count[task["task_type"]] += 1

            if task["task_timestamp"] in executor_namespace.actual_task_execution_time:
                executor_namespace.actual_task_execution_time[task["task_timestamp"]] += calculated_task_info["actual_execution_time_sec"]
            else:
                executor_namespace.actual_task_execution_time[task["task_timestamp"]] = calculated_task_info["actual_execution_time_sec"]           
            
            if (executor_namespace.actual_task_execution_time[task["task_timestamp"]] > task['max_task_execution_time_sec']):
                if task['task_timestamp'] not in executor_namespace.each_type_wasted_tasks_count[task["task_type"]]: 
                    executor_namespace.each_type_wasted_tasks_count[task["task_type"]].append(task['task_timestamp'])

            # Задача посчитана и имеет решение
            if calculated_task_info["is_solved"] and task["solve_exists"]:
                # Записываем, что нашли решение задачи
                solved_tasks[task["task_type"]].append(task["task_timestamp"])
                
                #Считаем фактическое время исполнения задачи
                
            # Задача не решена
            if not calculated_task_info["is_solved"]:
                executor_namespace.each_type_failed_subtasks_count[task["task_type"]] += 1

                task['priority'] = 0
                subtask_queue.put(task) #сразу отправляю задачу в очередь с максимальным приоритетом
                
                #failed_subtasks.put(task)

                # Восстанавливаем вычислитель
                time.sleep(random.uniform(0, self.executor_recovery_time_sec))
            

    def execute_task(self, task, solved_tasks, executor_namespace):
        # По умолчанию вычислитель исправен
        health_checked = False #Проверка, что что вычислитель жив
        execution_start_time = time.time()
        execution_time_ends  = execution_start_time + task["execution_time_sec"]
        
        if(task['solve_exists']):
            execution_time_ends  = execution_start_time + random.uniform(0.01, task["execution_time_sec"])
        
        is_solved = True
        while execution_time_ends >= time.time():
            if (self.solved_tasks_checker_flag != executor_namespace.solved_tasks_checker_flag):
                self.solved_tasks_checker_flag = executor_namespace.solved_tasks_checker_flag
                # Задача была решена в другом вычислителе
                if task["task_timestamp"] in solved_tasks[task["task_type"]]:
                    break

            if(not health_checked):
                health_checked = True
                if self.is_executor_failed():
                    is_solved = False
                    execution_time_ends = random.uniform(time.time(), execution_time_ends)
        return {"is_solved": is_solved, 'actual_execution_time_sec': time.time() - execution_start_time}


    def is_executor_failed(self) -> bool:
        """
        Произошла ли ошибка системы  во время вычисления задачи
        """

        return True if self.executor_error_probability >= random.random() else False
