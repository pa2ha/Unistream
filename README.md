# Swagger-документация - на http://127.0.0.1:8000/docs

## Докер запускаю командой ```docker compose up --build```

 ## тесты можно запустить следующей командой в терминале
```docker exec -it test_Unistream sh -c "cd /usr/src/app/TESTS && gauge run specs```


В задании не было указано, но реализованна безопасноcть на jwt, с кастомным блеклистом.
Если хотите включить, нужно раскомментить 30 строчку в project/Tasks/router.py


Статусы задач:

    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
