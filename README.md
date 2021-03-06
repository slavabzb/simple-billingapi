# simple-billingapi

Веб-приложение простой платежной системы.

## Требования

1) Каждый клиент в системе имеет один "кошелек", содержащий денежные средства.
2) Сохраняется информация о кошельке и остатке средств на нем.
3) Клиенты могут делать друг другу денежные переводы.
4) Сохраняется информация о всех операциях на кошельке клиента.
5) Проект представляет из себя HTTP API, содержащее основные операции по
"кошелькам":
    1) создание клиента с кошельком;
    2) зачисление денежных средств на кошелек клиента;
    3) перевод денежных средств с одного кошелька на другой.
6) Весь проект, со всеми зависимостями должен разворачиваться командой
docker-compose up.

Для упрощения, все переводы и зачисления выполняются без комиссии.

Предполагается что клиенты будут активно использовать данное АПИ для совершения
большого количества транзакций. Необходимо гарантировать высокую
производительность АПИ и консистентность данных в любой момент времени.
В системе одна валюта - USD.

## Деплой

Выполнить

      git clone https://github.com/slavabezborodov56/simple-billingapi.git
      cd simple-billingapi
      docker-compose up

Если все прошло хорошо, то health check запрос вернет код 200

      curl --location --request GET 'http://localhost/ping/'

Создать пользователя по номеру телефона

      curl --location --request POST 'http://localhost/public/v1/create-user/' \
      --header 'Idempotency-Key: 515dcc4b-9f6d-43fb-83b4-7f256d1e7240' \
      --header 'Content-Type: application/json' \
      --data-raw '{
          "phone": "+79194071066"
      }'

Начислить ему баланс

      curl --location --request POST 'http://localhost/public/v1/credit-funds/' \
      --header 'Idempotency-Key: 786706b8-ed80-443a-80f6-ea1fa8cc1b57' \
      --header 'Content-Type: application/json' \
      --data-raw '{
          "user_id": 1,
          "amount": 10
      }'

Перевести средства другому пользователю

      curl --location --request POST 'http://localhost/public/v1/transfer-funds/' \
      --header 'Idempotency-Key: 786706b8-ed80-443a-80f6-ea3fa8cc2b99' \
      --header 'Content-Type: application/json' \
      --data-raw '{
        "sender_user_id": 1,
        "receiver_user_id": 2,
        "amount": 10
      }'

## Комментарии и пояснения

PostgreSQL был выбран в качестве подсистемы хранения, обеспечивающей надежность
и консистентность данных в смысле ACID-преобразований. Первичный ключ лога
операций рассчитан на большое количество записей (тип bigint). Лог хранится
в той же базе, со временем при увеличении объемов транзакций к ней можно
применить партиционирование. Также можно выгружать лог в Kafka.

Средства пользователей хранятся без валюты в минимально возможной единице в
виде целого числа, чтобы избежать ошибок округления.

Модифицирующие операции используют низко гранулярные блокировки для обеспечения
высокой производительности OLTP-приложений и поддерживают механизм ключей
идемпотентности для обработки таймаутов и других сетевых проблем.
Предполагается, что клиент будет новый ключ идемпотентности для каждой новой
операции, а при таймаутах передавать тот же самый ключ.

Все HTTP-методы требуют обязательный заголовок X-Request-Id, который передается
дальше по цепочки другим HTTP-вызовам. Заголовок пишется в логи, обеспечивая
тем самым возможность распределенной трассировки запросов. Такой заголовок
нельзя проставить извне – для каждой операции он генерируется на внутреннем
NGINX.

## Развертывание для локальной разработки

      ln -s .envrc.example .envrc
