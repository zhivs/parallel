import logging

class Logger:
    _logs_path = "logs/all.log"    
    _tasks_path = "logs/tasks.log"

    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            filename=self._logs_path,
            filemode="a",
            format="%(asctime)s %(levelname)s %(message)s",
            encoding="utf-8",
            # datefmt="%d-%m-%Y %H:%M:%S",
        )

    def task_created(self, task, generator_number):
        logging.info(
            f"Task created. Generator {generator_number}. Task info: timestamp={task.timestamp} type={task.type} execution_time_sec={task.execution_time_sec} subtasks_count={task.subtasks_count}"
        )

    def task_calculated(self, task, executor_number):
        custom_logger = logging.getLogger(self._tasks_path)
        handler = logging.FileHandler(self._tasks_path)
        custom_logger.addHandler(handler)
        custom_logger.setLevel(logging.INFO)

        custom_logger.info(
            f"Subtask calculated. Executor number = {executor_number}. Priority = {task['priority']} Task info timestamp={task['task_timestamp']} solve_exists={task['solve_exists']} type={task['task_type']} execution_time_sec={task['execution_time_sec']}"
        )

        custom_logger.removeHandler(handler)


    def subtask_created(self, task, executor_number):
        custom_logger = logging.getLogger(self._tasks_path)
        handler = logging.FileHandler(self._tasks_path)
        custom_logger.addHandler(handler)
        custom_logger.setLevel(logging.INFO)

        custom_logger.info(
            f"Subtask created. Executor number = {executor_number}. Task info timestamp={task['task_timestamp']} solve_exists={task['solve_exists']} type={task['task_type']} execution_time_sec={task['execution_time_sec']}"
        )

    def task_solved(self, task, executor_number):
        logging.info(
            f"Task solved. Executor number = {executor_number}. Priority = {task['priority']} Task info timestamp={task['task_timestamp']} type={task['task_type']} execution_time_sec={task['execution_time_sec']}"
        )

    def executor_failed(self, task, executor_number):
        logging.error(
            f"Executor failed. Executor number = {executor_number} Subtask info: timestamp={task['task_timestamp']} type={task['task_type']} execution_time_sec={task['execution_time_sec']}"
        )

    def send_task_to_array(self, task, executor_number):
        logging.info(
            f"Subtask sended to array again. Executor number = {executor_number} Subtask info: timestamp={task['task_timestamp']} type={task['task_type']} execution_time_sec={task['execution_time_sec']}"
        )
