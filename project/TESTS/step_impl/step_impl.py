import requests
from getgauge.python import step, data_store


BASE_URL = "http://localhost:8000"


@step("Очистить базу данных")
def clear():
    """
    Очищает базу данных.
    """
    url = f"{BASE_URL}/api/tasks_delete_all"

    try:
        response = requests.delete(url, timeout=5)
        if response.status_code != 200:
            assert False, "Не смогли очистить базу данных"
    except requests.RequestException as e:
        assert False, f"Ошибка при создании задачи: {str(e)}"


@step("Создать задачу с title <title>, description <description> и статусом <status>")
def create_task_with_data(title, description, status):
    """
    Создает задачу с указанными параметрами.
    """
    url = f"{BASE_URL}/api/tasks/"
    task_data = {
        "title": title,
        "description": description,
        "status": status
    }

    try:
        response = requests.post(url, json=task_data, timeout=5)
        data_store.scenario["response"] = response
        if response.status_code == 200:
            data_store.scenario["created_task"] = response.json()
    except requests.RequestException as e:
        assert False, f"Ошибка при создании задачи: {str(e)}"


@step("Создать тестовую задачу")
def create_test_task():
    """
    Создает тестовую задачу с фиксированными данными.
    """
    create_task_with_data("Test Task", "Test Description", "CREATED")


@step("Проверить что статус ответа равен <status_code>")
def check_status_code(status_code):
    """
    Проверяет, что статус ответа равен ожидаемому.
    """
    response = data_store.scenario["response"]
    assert response.status_code == int(status_code), f"Ожидался статус {status_code}, получен {response.status_code}"


@step("Проверить что в ответе есть поле <field>")
def verify_field_exists(field):
    """
    Проверяет, что указанное поле присутствует в ответе.
    """
    response = data_store.scenario["response"]
    try:
        task_data = response.json()
    except ValueError:
        assert False, "Ответ не является валидным JSON"
    assert field in task_data, f"Поле '{field}' не найдено в ответе"


@step("Проверить что title равен <expected_title>")
def verify_title_equals(expected_title):
    """
    Проверяет, что title в ответе равен ожидаемому.
    """
    response = data_store.scenario["response"]
    try:
        task_data = response.json()
    except ValueError:
        assert False, "Ответ не является валидным JSON"
    assert task_data["title"] == expected_title, f"Ожидался title '{expected_title}', получен '{task_data['title']}'"


@step("Проверить что status равен <expected_status>")
def verify_status_equals(expected_status):
    """
    Проверяет, что status в ответе равен ожидаемому.
    """
    response = data_store.scenario["response"]
    try:
        task_data = response.json()
    except ValueError:
        assert False, "Ответ не является валидным JSON"
    assert task_data["status"] == expected_status, f"Ожидался status '{expected_status}', получен '{task_data['status']}'"


@step("Создать 3 тестовые задачи")
def create_three_test_tasks():
    """
    Создает три тестовые задачи с разными статусами.
    """
    tasks = [
        {"title": "Task 1", "description": "Desc 1", "status": "CREATED"},
        {"title": "Task 2", "description": "Desc 2", "status": "IN_PROGRESS"},
        {"title": "Task 3", "description": "Desc 3", "status": "COMPLETED"}
    ]

    for task_data in tasks:
        try:
            response = requests.post(f"{BASE_URL}/api/tasks/", json=task_data, timeout=5)
            assert response.status_code == 200, f"Не удалось создать задачу: {response.text}"
        except requests.RequestException as e:
            assert False, f"Ошибка при создании задачи: {str(e)}"


@step("Перейти по URL <url>")
def go_to_url(url):
    """
    Выполняет GET-запрос по указанному URL.
    """
    full_url = f"{BASE_URL}{url.replace('<uuid>', data_store.scenario.get('task_uuid', ''))}"
    try:
        response = requests.get(full_url, timeout=5)
        data_store.scenario["response"] = response
    except requests.RequestException as e:
        assert False, f"Ошибка при запросе к {full_url}: {str(e)}"


@step("Проверить что в ответе <count> задачи")
def verify_response_contains_n_tasks(count):
    """
    Проверяет, что в ответе содержится указанное количество задач.
    """
    response = data_store.scenario["response"]
    try:
        tasks = response.json()
    except ValueError:
        assert False, "Ответ не является валидным JSON"
    assert len(tasks) == int(count), f"Ожидалось {count} задач, получено {len(tasks)}"


@step("Проверить что у каждой задачи есть <field1> и <field2>")
def verify_all_tasks_have_fields(field1, field2):
    """
    Проверяет, что каждая задача содержит указанные поля.
    """
    response = data_store.scenario["response"]
    try:
        tasks = response.json()
    except ValueError:
        assert False, "Ответ не является валидным JSON"

    for task in tasks:
        assert field1 in task, f"Задача {task} не содержит поле '{field1}'"
        assert field2 in task, f"Задача {task} не содержит поле '{field2}'"


@step("Сохранить UUID созданной задачи")
def save_created_task_uuid():
    """
    Сохраняет UUID созданной задачи из ответа.
    """
    response = data_store.scenario["response"]
    try:
        task_data = response.json()
    except ValueError:
        assert False, "Ответ не является валидным JSON"
    data_store.scenario["task_uuid"] = task_data["uuid"]


@step("Проверить что uuid совпадает с сохраненным")
def verify_uuid_matches_saved():
    """
    Проверяет, что UUID в ответе совпадает с сохраненным.
    """
    response = data_store.scenario["response"]
    saved_uuid = data_store.scenario.get("task_uuid")
    try:
        task_data = response.json()
    except ValueError:
        assert False, "Ответ не является валидным JSON"

    assert saved_uuid, "Сохраненный UUID не найден"
    assert task_data["uuid"] == saved_uuid, f"Ожидался UUID '{saved_uuid}', получен '{task_data['uuid']}'"


@step("Обновить задачу с новыми данными")
def update_task_with_new_data():
    """
    Обновляет задачу с новыми данными.
    """
    task_uuid = data_store.scenario["task_uuid"]
    url = f"{BASE_URL}/api/tasks/{task_uuid}"

    update_data = {
        "title": "Updated Title",
        "description": "Updated Description",
        "status": "IN_PROGRESS"
    }

    try:
        response = requests.put(url, json=update_data, timeout=5)
        data_store.scenario["response"] = response
    except requests.RequestException as e:
        assert False, f"Ошибка при обновлении задачи: {str(e)}"


@step("Проверить что title обновился")
def verify_title_updated():
    """
    Проверяет, что title обновился до ожидаемого значения.
    """
    response = data_store.scenario["response"]
    try:
        task_data = response.json()
    except ValueError:
        assert False, "Ответ не является валидным JSON"
    assert task_data["title"] == "Updated Title", f"Ожидался title 'Updated Title', получен '{task_data['title']}'"


@step("Проверить что status обновился")
def verify_status_updated():
    """
    Проверяет, что status обновился до ожидаемого значения.
    """
    response = data_store.scenario["response"]
    try:
        task_data = response.json()
    except ValueError:
        assert False, "Ответ не является валидным JSON"
    assert task_data["status"] == "IN_PROGRESS", f"Ожидался status 'IN_PROGRESS', получен '{task_data['status']}'"


@step("Удалить задачу по UUID")
def delete_task_by_uuid():
    """
    Удаляет задачу по сохраненному UUID.
    """
    task_uuid = data_store.scenario["task_uuid"]
    url = f"{BASE_URL}/api/tasks/{task_uuid}"
    try:
        response = requests.delete(url, timeout=5)
        data_store.scenario["response"] = response
    except requests.RequestException as e:
        assert False, f"Ошибка при удалении задачи: {str(e)}"


@step("Попытаться получить удаленную задачу")
def try_get_deleted_task():
    """
    Пытается получить удаленную задачу по UUID.
    """
    task_uuid = data_store.scenario["task_uuid"]
    url = f"{BASE_URL}/api/tasks/{task_uuid}"
    try:
        response = requests.get(url, timeout=5)
        data_store.scenario["response"] = response
    except requests.RequestException as e:
        assert False, f"Ошибка при запросе удаленной задачи: {str(e)}"


@step("Создать задачи: 2 CREATED, 1 COMPLETED")
def create_tasks_with_statuses():
    """
    Создает задачи с указанными статусами.
    """
    tasks = [
        {"title": "Created 1", "description": "Desc", "status": "CREATED"},
        {"title": "Created 2", "description": "Desc", "status": "CREATED"},
        {"title": "Completed 1", "description": "Desc", "status": "COMPLETED"}
    ]

    for task_data in tasks:
        try:
            response = requests.post(f"{BASE_URL}/api/tasks/", json=task_data, timeout=5)
            assert response.status_code == 200, f"Не удалось создать задачу: {response.text}"
        except requests.RequestException as e:
            assert False, f"Ошибка при создании задачи: {str(e)}"
