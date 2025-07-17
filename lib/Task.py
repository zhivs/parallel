from pydantic import BaseModel, Field, computed_field


class Task(BaseModel):
    timestamp: float = Field(description="Время создания задачи")
    type: int = Field(description="Тип задачи, от него зависит время исполнения задачи")

    subtasks_count: int = Field(0, description="Количество подзадач в задаче")
    generator_number: int = Field(0, description="Номер генератора задачи")
    
    #is_heterogeneous: bool = Field(True, description="Задача гетерогенная")
    #execution_time_delta_range : list = Field([1, 200]) #Диапазон значений для случайного изменения времени исполнения задачи

    @computed_field
    def execution_time_sec(self) -> int:
        return self.set_execution_time()
    
    def set_execution_time(self) -> int:
        return Task.get_execution_time_by_type(self.type)

    @staticmethod
    def get_execution_time_by_type(type) -> int:
        match type:
            case 0:
                return 160
            case 1:
                return 100
            case 2:
                return 64
            case 3:
                return 32
            case _:
                return 3

    @staticmethod
    def get_task_types_list():
        return [0, 1, 2, 3]
    
    @staticmethod
    def get_task_exec_time_dict() -> dict:
        return {
            0: Task.get_execution_time_by_type(0),
            1: Task.get_execution_time_by_type(1),
            2: Task.get_execution_time_by_type(2),
            3: Task.get_execution_time_by_type(3)
        }
