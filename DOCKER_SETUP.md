# Настройка Docker

## Проблема: Permission denied

Если вы видите ошибку `Permission denied` при запуске `docker-compose`, это означает, что ваш пользователь не имеет прав доступа к Docker socket.

## Решение 1: Добавить пользователя в группу docker (рекомендуется)

```bash
# Добавить текущего пользователя в группу docker
sudo usermod -aG docker $USER

# Применить изменения (нужно выйти и войти заново, или использовать newgrp)
newgrp docker

# Проверить, что работает
docker ps
```

**Важно:** После выполнения `usermod` нужно:
- Выйти из системы и войти заново, ИЛИ
- Выполнить `newgrp docker` в текущей сессии

## Решение 2: Использовать sudo (временное решение)

Если не хотите добавлять пользователя в группу, можно использовать sudo:

```bash
sudo docker-compose up -d
sudo docker-compose logs -f
sudo docker-compose down
```

**Недостаток:** Файлы, созданные контейнерами, будут принадлежать root, что может вызвать проблемы.

## Проверка

После настройки проверьте:

```bash
# Проверить, что Docker работает
docker ps

# Проверить, что docker-compose работает
docker-compose --version
```

## Если Docker не установлен

Если Docker вообще не установлен:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Запустить Docker сервис
sudo systemctl start docker
sudo systemctl enable docker
```
