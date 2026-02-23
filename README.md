# Habit Tracker API

API для трекера полезных привычек. Проект полностью контейнеризирован и развёрнут в Yandex Cloud с использованием Docker Compose и CI/CD через GitHub Actions.

## 🌐 Деплой

Проект доступен по адресу:  
**http://89.169.166.9/api/**

Документация API (Swagger):  
**http://89.169.166.9/api/docs/** (если настроено)

---

## 🛠 Стек технологий

- **Backend:** Django 5, Django REST Framework, JWT
- **База данных:** PostgreSQL 15
- **Кеш и брокер задач:** Redis 7, Celery
- **Веб-сервер:** Nginx, Gunicorn
- **Контейнеризация:** Docker, Docker Compose
- **Облачная платформа:** Yandex Cloud (Ubuntu 22.04)
- **CI/CD:** GitHub Actions

---

## 🚀 Локальный запуск

### 1. Клонировать репозиторий
```bash
git clone https://github.com/str057/w1.git
cd w1