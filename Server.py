import grpc
from concurrent import futures
import time
import random
from datetime import datetime
from enum import Enum
import taskMeneger_pb2
import taskMeneger_pb2_grpc

class TaskStatus(Enum):
    PENDING = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    BLOCKED = 3

class Priority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    URGENT = 3

class TaskManagerServicer(taskMeneger_pb2_grpc.TaskManagerServicer):
    def init(self):
        # Генерируем тестовые данные
        self.users = ["user_001", "user_002", "user_003", "user_004"]
        self.tasks = self._generate_sample_tasks()
    
    def _generate_sample_tasks(self):
        """Генерирует тестовые задачи для демонстрации"""
        tasks = []
        task_titles = [
            "Разработать новый функционал",
            "Исправить баг в модуле авторизации",
            "Написать документацию API",
            "Провести code review",
            "Оптимизировать производительность",
            "Добавить unit тесты",
            "Обновить зависимости",
            "Создать дашборд аналитики",
            "Интегрировать с внешним API",
            "Рефакторинг legacy кода"
        ]
        
        task_descriptions = [
            "Необходимо реализовать новый модуль для обработки платежей",
            "Пользователи не могут войти в систему после обновления",
            "Документировать все endpoints gRPC сервиса",
            "Проверить PR #154 на соответствие code style",
            "Увеличить скорость ответа API на 30%",
            "Покрыть тестами критичные модули системы",
            "Обновить все пакеты до последних версий",
            "Визуализировать метрики использования системы",
            "Подключиться к сервису нотификаций",
            "Улучшить читаемость и поддерживаемость кода"
        ]
        
        tags = ["backend", "frontend", "devops", "database", "security", "ui/ux", "testing", "documentation"]
        
        for i in range(100):
            user_id = random.choice(self.users)
            status = random.choice(list(TaskStatus))
            priority = random.choice(list(Priority))
            
            task_tags = random.sample(tags, random.randint(1, 3))
            
            created_ts = int(time.time()) - random.randint(0, 30*24*3600)  # до 30 дней назад
            updated_ts = created_ts + random.randint(0, 7*24*3600)  # обновлено в течение недели
            
            tasks.append({
                "task_id": f"task_{i:03d}",
                "title": random.choice(task_titles),
                "description": random.choice(task_descriptions),
                "status": status,
                "assignee": user_id,
                "created_at": created_ts,
                "updated_at": updated_ts,
                "priority": priority,
                "tags": task_tags
            })
        
        return tasks
    
    def GetTasksForUser(self, request, context):
        """Server streaming RPC - возвращает поток задач для пользователя"""
        user_id = request.user_id
        print(f"Запрос задач для пользователя: {user_id}")
        
        # Фильтруем задачи по пользователю
        user_tasks = [task for task in self.tasks if task["assignee"] == user_id]
        
        if not user_tasks:
            print(f"Пользователь {user_id} не найден или не имеет задач")
            # Можно отправить пустой stream или вызвать context.abort()
            return
        
        print(f"Найдено {len(user_tasks)} задач для пользователя {user_id}")
        
        # Отправляем задачи потоком
        for task in user_tasks:
            # Имитируем задержку для демонстрации streaming
            time.sleep(0.5)
            
            # Конвертируем в protobuf message
            task_proto = taskMeneger_pb2.Task(
                task_id=task["task_id"],
                title=task["title"],
                description=task["description"],
                status=task["status"].value,
                assignee=task["assignee"],
                created_at=task["created_at"],
updated_at=task["updated_at"],
                priority=task["priority"].value,
                tags=task["tags"]
            )
            
            print(f"Отправка задачи: {task['task_id']} - {task['title']}")
            yield task_proto
        
        print(f"Все задачи для пользователя {user_id} отправлены")
    
    def GetUserStats(self, request, context):
        """Unary RPC - возвращает статистику по пользователю"""
        user_id = request.user_id
        print(f"Запрос статистики для пользователя: {user_id}")
        
        user_tasks = [task for task in self.tasks if task["assignee"] == user_id]
        
        if not user_tasks:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Пользователь {user_id} не найден")
        
        # Считаем статистику
        total = len(user_tasks)
        pending = len([t for t in user_tasks if t["status"] == TaskStatus.PENDING])
        completed = len([t for t in user_tasks if t["status"] == TaskStatus.COMPLETED])
        in_progress = len([t for t in user_tasks if t["status"] == TaskStatus.IN_PROGRESS])
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        stats = taskMeneger_pb2.UserStats(
            user_id=user_id,
            total_tasks=total,
            pending_tasks=pending,
            completed_tasks=completed,
            in_progress_tasks=in_progress,
            completion_rate=round(completion_rate, 2)
        )
        
        print(f"Статистика для {user_id}: {completed}/{total} завершено ({completion_rate:.1f}%)")
        return stats

def serve():
    """Запускает gRPC сервер"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    taskMeneger_pb2_grpc.add_TaskManagerServicer_to_server(TaskManagerServicer(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    
    print("Сервер TaskManager запущен на порту 50053")
    print("Доступные пользователи: user_001, user_002, user_003, user_004")
    print("Ожидаем запросы...")
    
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
        print("Сервер остановлен")

if name == 'main':
    serve()