import grpc
import time
from datetime import datetime
import taskMeneger_pb2
import taskMeneger_pb2_grpc

class TaskManagerClient:
    def init(self, host='localhost', port=50053):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = taskMeneger_pb2_grpc.TaskManagerStub(self.channel)
    
    def timestamp_to_datetime(self, ts):
        """Конвертирует timestamp в читаемую дату"""
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    
    def get_status_name(self, status_value):
        """Возвращает название статуса"""
        status_map = {
            0: " PENDING",
            1: " IN_PROGRESS", 
            2: " COMPLETED",
            3: "BLOCKED"
        }
        return status_map.get(status_value, "UNKNOWN")
    
    def get_priority_name(self, priority_value):
        """Возвращает название приоритета"""
        priority_map = {
            0: " LOW",
            1: " MEDIUM",
            2: " HIGH", 
            3: " URGENT"
        }
        return priority_map.get(priority_value, "UNKNOWN")
    
    def get_tasks_for_user(self, user_id):
        """Получает поток задач для пользователя"""
        print(f"\nЗапрашиваем задачи для пользователя: {user_id}")
        print("=" * 60)
        
        try:
            request = taskMeneger_pb2.UserRequest(user_id=user_id)
            tasks_stream = self.stub.GetTasksForUser(request)
            
            task_count = 0
            start_time = time.time()
            
            for task in tasks_stream:
                task_count += 1
                
                print(f"\n Задача #{task_count}")
                print(f"   ID: {task.task_id}")
                print(f"   Title: {task.title}")
                print(f"   Status: {self.get_status_name(task.status)}")
                print(f"   Priority: {self.get_priority_name(task.priority)}")
                print(f"   Created: {self.timestamp_to_datetime(task.created_at)}")
                print(f"   Updated: {self.timestamp_to_datetime(task.updated_at)}")
                print(f"   Tags: {', '.join(task.tags) if task.tags else 'No tags'}")
                print(f"   Description: {task.description[:100]}...")
                print("-" * 40)
            
            elapsed_time = time.time() - start_time
            print(f"\n Получено {task_count} задач за {elapsed_time:.2f} секунд")
            
        except grpc.RpcError as e:
            print(f" Ошибка gRPC: {e.details()}")
        except Exception as e:
            print(f" Неожиданная ошибка: {str(e)}")
    
    def get_user_stats(self, user_id):
        """Получает статистику по пользователю"""
        print(f"\nЗапрашиваем статистику для пользователя: {user_id}")
        
        try:
            request = taskMeneger_pb2.UserRequest(user_id=user_id)
            stats = self.stub.GetUserStats(request)
            
            print("=" * 40)
            print(f" User ID: {stats.user_id}")
            print(f" Total Tasks: {stats.total_tasks}")
            print(f" Pending: {stats.pending_tasks}")
            print(f" In Progress: {stats.in_progress_tasks}")
            print(f"Completed: {stats.completed_tasks}")
            print(f" Completion Rate: {stats.completion_rate}%")
            print("=" * 40)
            
        except grpc.RpcError as e:
            print(f" Ошибка gRPC: {e.details()}")
        except Exception as e:
            print(f" Неожиданная ошибка: {str(e)}")

def main():
    """Основная функция клиента"""
    print("===  gRPC Task Manager Client ===")
    
    client = TaskManagerClient()
    
    while True:
        print("\nВыберите действие:")
        print("1. Получить задачи пользователя")
        print("2. Получить статистику пользователя")
        print("3. Выход")
        
        choice = input("Введите номер действия: ").strip()
        
        if choice == '3':
            print("Выход из программы...")
            break
        
        user_id = input("Введите User ID (user_001, user_002, user_003, user_004): ").strip()
        
        if not user_id:
print("User ID не может быть пустым")
            continue
        
        if choice == '1':
            client.get_tasks_for_user(user_id)
        elif choice == '2':
            client.get_user_stats(user_id)
        else:
            print("Неверный выбор")

if name == 'main':
    main()