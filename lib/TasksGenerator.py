from lib.Task import Task
from lib.Logger import Logger

from random import choice, uniform
import time


class TasksGenerator:
    random_delay_interval = [1, 2]  # Время задержки между созданием задач
    # distribution_law = "normal"  # Закон распределения

    def __init__(self, subtasks_count_in_task_queue, subtask_array, namespace, subtasks_queue, stop_event, generation_time_sec=0):
        self.generation_time_sec = generation_time_sec
        self.subtasks_count_in_task_queue = subtasks_count_in_task_queue
        self.subtask_array = subtask_array
        self.namespace = namespace
        self.subtasks_queue = subtasks_queue
        self.stop_event = stop_event

    def generate_tasks(self, generator_number):
        print("generation started. GENERATOR_NUMBER: {}".format(generator_number))
        
        if self.generation_time_sec > 0:
            generation_start_rime = time.time()
            while time.time() - generation_start_rime < self.generation_time_sec:
                self.generate_task(
                    generator_number)  # В зависимости от номера генератора, создается задача определенного типа
                # self.generate_random_task(generator_number, task_array, namespace) # номер генератора не зависит, создается случайная задача
        else:
            while not self.stop_event.is_set():
                self.generate_task(
                    generator_number)  # В зависимости от номера генератора, создается задача определенного типа
                # self.generate_random_task(generator_number, task_array, namespace) # номер генератора не зависит, создается случайная задача
        
        #print("generation finished. GENERATOR_NUMBER: {}".format(generator_number))

    def generate_task(self, generator_number):
        task_type = generator_number - 1
        task = Task(timestamp=time.time(), type=task_type)

        self.decompose_task(generator_number, task, task_type)

        # номер генератора, интервал (от 0 до N) генерации в секундах
        DELAY_THRESHOLDS = [(1, 14), 
                            (2, 12),
                            (3, 7), 
                            (4, 5)
                            ]
        delay = 2  # Значение по умолчанию
        
        for threshold, count in DELAY_THRESHOLDS:
            if generator_number == threshold:
                delay = count
                break

        time.sleep(uniform(2.3, delay))
        #time.sleep(delay)

    def decompose_task(self, generator_number, task, task_type):
        curTasksCountInQueue = self.subtasks_queue.qsize()

        if curTasksCountInQueue < 100:
            subtasksCount = 30
        elif curTasksCountInQueue >= 100 and curTasksCountInQueue < 200:
            subtasksCount = 23
        elif curTasksCountInQueue >= 200 and curTasksCountInQueue < 300:
            subtasksCount = 18
        elif curTasksCountInQueue >= 300 and curTasksCountInQueue < 400:
            subtasksCount = 12
        elif curTasksCountInQueue >= 400:
            subtasksCount = 8
        
        task.subtasks_count = subtasksCount
        task.generator_number = generator_number
        
        task_execution_time     = task.execution_time_sec
        subtask_execution_time  = task_execution_time / subtasksCount
        subtaskWithSolve_number = choice(range(0, subtasksCount))
        task_timestamp = task.timestamp
        #subtasks = []
        for i in range(subtasksCount):
            solve_exists = True if i == subtaskWithSolve_number else False
            
            subtask = {
                "task_timestamp": task_timestamp,
                "task_type": task_type,
                "execution_time_sec": subtask_execution_time,
                "solve_exists": solve_exists,
                "subtasks_count": subtasksCount,
                "generator_number": generator_number,
                "max_task_execution_time_sec": task_execution_time,
                "wasted_time_sec": 0, #Затраченное время на решение с ошибкой
            }
            
            self.subtask_array.append(subtask)
            #subtasks.append(subtask)
            
        #subtask_array.extend(subtasks)
        
        self.subtasks_count_in_task_queue.put((task_timestamp, subtasksCount))
        self.namespace.each_type_created_tasks_count[task_type] += 1

    def generate_random_task(self, generator_number, task_array):
        task_type = choice(Task.get_task_types_list())
        task = Task(timestamp=time.time(), type=task_type)

        self.decompose_task(generator_number, task, task_type, task_array)

        delay = uniform(
            self.random_delay_interval[0], self.random_delay_interval[1]
        )  # 1.298311670214672 пример задержки

        time.sleep(delay)


    def get_generator_stats(self):
        while not self.stop_event.is_set():
            print(
                "Tasks created: {} => [{}, {}, {}, {}]".format(
                    sum(self.namespace.each_type_created_tasks_count),
                    self.namespace.each_type_created_tasks_count[0],
                    self.namespace.each_type_created_tasks_count[1],
                    self.namespace.each_type_created_tasks_count[2],
                    self.namespace.each_type_created_tasks_count[3],
                )
            )
            
            time.sleep(10)
