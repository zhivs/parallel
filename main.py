import configparser

import multiprocessing
import time

from lib.TasksGenerator import TasksGenerator
from lib.TasksExecutor import TasksExecutor
from lib.TasksController import TasksController
from lib.Task import Task

from lib.PriorityQueue import PriorityQueue


if __name__ == "__main__":
    
    config = configparser.ConfigParser() #+
    config.read('settings.ini') #+

    subtasks_queue    = PriorityQueue()  # Очередь подзадач +
        
    proxy = multiprocessing.Manager() #+
    subtask_array    = proxy.list() #+
    
    failed_subtasks  = multiprocessing.Queue() #+
    solved_tasks  = proxy.list([proxy.list() for task_type in Task.get_task_types_list()]) #+
    
    namespace  = proxy.Namespace()  # Общая память #+

    namespace.each_type_created_tasks_count = proxy.list([0,0,0,0])
    
    namespace.input_flow = 0 #Интенсивность входного потока +

    executor_proxy = multiprocessing.Manager()
    executor_namespace = executor_proxy.Namespace()
    
    executor_namespace.solved_tasks_checker_flag = 0 #Флаг проверки уже решенных задач в вычислителях
    executor_namespace.each_type_solved_subtasks_count = executor_proxy.list([0,0,0,0])
    executor_namespace.each_type_failed_subtasks_count = executor_proxy.list([0,0,0,0])
    
    executor_namespace.each_type_wasted_tasks_count    = executor_proxy.list([proxy.list() for task_type in Task.get_task_types_list()])
    
    executor_namespace.actual_task_execution_time = executor_proxy.dict() #Фактическое время выполнения задач каждого типа
    
    executor_namespace.productivity = 0 #Продуктивность

    subtasks_count_in_task_queue = multiprocessing.Queue() #Очередь количества подзадач в задачах
    
    stop_event = multiprocessing.Event()  # События в потоке +

    task_generator = TasksGenerator(subtasks_count_in_task_queue, subtask_array, namespace, subtasks_queue, stop_event,generation_time_sec=int(config['DEFAULT']['GENERATION_TIME_SEC']))  # Генератор задач

    #Запуск параллельной генерации задач
    
    gen_procs = []
    for generator_number in range(1, 5):
        p = multiprocessing.Process(
            target=task_generator.generate_tasks,
            args=(generator_number,)
        )
        p.start()
        gen_procs.append(p)

    taskUtils = TasksController() # Класс со вспомогательными методами

    #Отправка задач в очередь
    priority_manager_proc = multiprocessing.Process(
        target=taskUtils.send_subtasks_to_queue, args=(subtask_array, subtasks_queue, namespace, stop_event)
    )
    priority_manager_proc.start()

    #Отправка зафейленных задач в очередь (сейчас сразу попадают из вычислителя в очередь с максимальным приоритетом)
    # priority_manager_proc1 = multiprocessing.Process(
    #     target=taskUtils.send_failed_subtasks_to_queue, args=(failed_subtasks, subtasks_queue, stop_event)
    # )
    # priority_manager_proc1.start()


    solved_tasks_flag_proc = multiprocessing.Process(
        target=taskUtils.switch_solved_tasks_checker_flag, args=(executor_namespace, stop_event)
    )
    solved_tasks_flag_proc.start()

    #Вычислитель задач
    tasks_executor = TasksExecutor()
    exec_procs = []
    for executor_number in range(1, 33):
        p1 = multiprocessing.Process(target=tasks_executor.execute_tasks, args=(subtasks_queue, solved_tasks, failed_subtasks, executor_namespace, stop_event))
        exec_procs.append(p1)
        p1.start()

    #Статистика в момент работы вычислителей
    tasks_count_in_queue_proc = multiprocessing.Process(
        target=taskUtils.subtasks_statistic, args=(executor_namespace, subtasks_queue, solved_tasks, stop_event)
    )
    tasks_count_in_queue_proc.start()

    # #Статистика в момент работы генераторов
    # tasks_generator_stats_proc = multiprocessing.Process(
    #     target=task_generator.get_generator_stats, args=()
    # )
    # tasks_generator_stats_proc.start()

    #Статистика продуктивности
    tasks_productivity_stats_proc = multiprocessing.Process(
        target=taskUtils.calc_productivity, args=(solved_tasks, executor_namespace, stop_event)
    )
    tasks_productivity_stats_proc.start()

    #График зависимости количества подзадач в задачах от времени
    from lib.plots.SubtasksCountInTaskPlot import SubtasksCountInTaskPlot
    plot = SubtasksCountInTaskPlot()
    plot_proc = multiprocessing.Process(
        target=plot.plot_subtasks_count_in_tasks_by_time,
        args=(subtasks_count_in_task_queue,)
    )
    plot_proc.start()

    #График зависимости количества подзадач в очереди от времени
    from lib.plots.SubtasksCountInQueuePlot import SubtasksCountInQueuePlot
    subtasksCountInQueuePlot = SubtasksCountInQueuePlot()
    subtasksCountInQueuePlot_proc = multiprocessing.Process(
        target=subtasksCountInQueuePlot.plot_subtasks_count_in_queue_by_time,
        args=(subtasks_queue,)
    )
    subtasksCountInQueuePlot_proc.start()
    
    #График интенсивности входного потока от времени
    from lib.plots.InputFlowPlot import InputFlowPlot
    inputFlowPlot = InputFlowPlot()
    inputFlowPlot_proc = multiprocessing.Process(
        target=inputFlowPlot.plot_input_flow,
        args=(namespace,)
    )
    inputFlowPlot_proc.start()

    #График продуктивности от времени
    from lib.plots.ProductivityPlot import ProductivityPlot
    productivityPlot = ProductivityPlot()
    productivityPlot_proc = multiprocessing.Process(
        target=productivityPlot.plot_productivity,
        args=(executor_namespace,)
    )
    productivityPlot_proc.start()

    try:
        while True:
            time.sleep(1)  # Основной поток просто ждет
    except KeyboardInterrupt:
        # флаг остановки
        stop_event.set()

        for i in gen_procs:
            i.terminate()
            i.join()

        #tasks_generator_stats_proc.join()
        tasks_count_in_queue_proc.join()

        priority_manager_proc.join()

        for j in exec_procs:
            j.terminate()
            j.join()

        print("Остановка завершена.")
