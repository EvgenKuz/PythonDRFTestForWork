# PythonDRFTestForWork
Python DRF test task for job apllication.
Requirements from [repo](https://github.com/sdobrimutrom/python_test).

# Installation and start
1. Install [Python 3.11](https://www.python.org/)
2. Install [Poetry](https://python-poetry.org/docs/#installation)
3. Install [Docker](https://docs.docker.com/get-docker/)

## Just start the project
4. Run `docker compose up -d`
5. Server is now available at `localhost:8080\swagger`

## Development
4. Run `docker compose up -d redis`
5. Run `poetry install --with development`
6. Now you can develop)

# python_test
MMVS Python Test

Python backend developer test. Необходимо сделать API для сервиса хранения видеофайлов с возможностью менять разрешение. В качестве фреймворка использовать Django или Django Rest (на Ваше усмотрение). Конвертация должна происходить с помощью ffmpeg (В качестве обертки нужно использовать https://github.com/kkroening/ffmpeg-python).

## HTTP API

### Методы

#### `POST /file/`
Тело запроса: видеофайл в формате MP4.

В теле ответа возвращается 
```
{
  id: UUID — идентификатор , например: `876b8335-3279-4f59-9718-570f37f076ea`.
}
``` 

Код ответа: `200 Ok`.

#### `PATCH /file/{id}/`
Начать изменение разрешения видео используя ffmpeg. Ответ должен возвращаться независимо от завершения процесса обработки (обработка не должна блокировать запрос) 

Тело запроса:

```
{
  width: int,  - Чётное число больше 20
  height: int,  - Чётное число больше 20
}
```

В теле ответа возвращается 
```
{
  success: Boolean
}
``` 
Код ответа: `200 Ok`.

#### `GET /file/{id}/`
Получить информацию о файле и статусе его обработки

Тело ответа:

```
{
  id: uid,
  filename: string,
  processing: Boolean - идёт ли процесс обработки
  processingSuccess: null | true | false  - отображает успешность последней операции над видео. Дефолтное значение null.
}
```
Код ответа: `200 Ok`.


#### `DELETE /file/{id}/`
Удалить файл

В теле ответа возвращается 
```
{
  success: Boolean
}
``` 
Код ответа: `200 Ok`.


### Обработка ошибок
При возникновении ошибок необходимо возвращать ошибку в json формате
```
{
  error: string
}
```

## Дополнительно
Будет плюсом если:
 - есть автодокументация API 
 - есть система логирования
 - сервис завёрнут в docker контейнер
 - наличие юнит тестов
