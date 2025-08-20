Swagger-документация - на http://127.0.0.1:8000/docs

Докер запускаю командой docker compose up --build

После запуска контейнеров тесты можно запустить следующей командой в терминале

docker exec -it test_Unistream sh -c "cd /usr/src/app/TESTS && gauge run specs"


В задании не было указано, но реализованна безопасноcть на jwt, даже с блеклистом.
Если хотите включить, нужно раскоментить 30 строчку в Tasks/router.py