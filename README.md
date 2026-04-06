# 🧠 Home Secretary

---

## 🇬🇧 ENGLISH VERSION

### Overview

Home Secretary is a self-hosted web platform for personal and family organization.

It combines multiple domains into a single system:

- task management (todo)
- calendar planning
- household finance tracking
- document storage with metadata
- notifications (Matrix, web push)

The system is designed to run on a private server and be accessible via the internet for multiple users.

---

### Goals

The main goal is to build a unified digital environment for managing everyday life:

- track tasks and deadlines
- plan events
- manage household finances
- store and search documents
- receive reminders and alerts

---

### Core Principles

- modular monolith architecture
- self-hosted deployment
- multi-user support
- family-oriented model
- security-first approach
- Docker-based infrastructure
- PostgreSQL as primary database

---

### Architecture

The system follows a modular monolith design:

Core modules:

- authentication
- users
- families
- roles and permissions
- audit logs

Business modules:

- tasks
- calendar
- finance
- documents

Infrastructure:

- PostgreSQL
- file storage
- Matrix notifications
- web push notifications
- reverse proxy (HTTPS)
- backup system

---

### Roles

- admin — manages family-level settings and access
- user — manages personal and shared data

---

### Authentication

Authentication is based on JWT.

Flow:

- register with email/password
- login
- receive access and refresh tokens
- refresh access token
- logout
- password reset request
- password reset confirmation

At MVP stage:

- no email confirmation
- no 2FA
- password reset supported

---

### Storage

- PostgreSQL — structured data
- filesystem — uploaded files
- metadata stored in DB

---

### Clients

- desktop browser
- mobile browser

---

### Roadmap

Stage 0 — Project foundation  
Stage 1 — Auth + Users + Families  
Stage 2 — Organizer / Todo  
Stage 3 — Calendar  
Stage 4 — Finance  
Stage 5 — Documents  
Stage 6 — Notifications  
Stage 7 — Security hardening  

---

### Deployment

The system runs in Docker containers:

- backend (FastAPI)
- PostgreSQL
- reverse proxy
- persistent storage for files
- backup service

For the current local test stage, the project already includes a working Docker setup for:

- backend
- PostgreSQL

---

### Security Notes

This system handles sensitive data:

- personal information
- financial data
- documents

Required measures:

- password hashing
- secure token handling
- HTTPS
- access control
- audit logging
- backup strategy

---

### Status

Project is already in implementation, not only in planning.

Current state:

- backend structure is assembled
- FastAPI entrypoint exists
- auth API, schemas, services, repositories, and ORM models are implemented
- env-based configuration is centralized
- Docker-based local test run for backend + PostgreSQL is prepared
- auth core is in stabilization and verification phase

Stage status:

- Stage 0 is effectively completed as a foundation
- Stage 1 is implemented structurally
- Technical Specification 3 is mostly closed on code structure and runtime wiring
- the remaining work is final smoke-testing and closing a few review/recheck items

---

## 🇷🇺 РУССКАЯ ВЕРСИЯ

### Обзор

Home Secretary — это self-hosted веб-платформа для организации личной и семейной жизни.

Система объединяет:

- список дел (todo)
- календарь
- домашнюю бухгалтерию
- хранение документов с метаданными
- систему уведомлений (Matrix, web push)

Проект предназначен для запуска на собственном сервере с доступом через интернет для нескольких пользователей.

---

### Цели проекта

Создать единое цифровое пространство для управления повседневной жизнью:

- контроль задач и дедлайнов
- планирование событий
- учёт финансов
- хранение документов
- получение напоминаний

---

### Основные принципы

- модульный монолит
- self-hosted архитектура
- многопользовательская система
- семейная модель доступа
- безопасность как базовый принцип
- Docker-инфраструктура
- PostgreSQL как основная БД

---

### Архитектура

Система построена как модульный монолит.

Ядро:

- аутентификация
- пользователи
- семьи
- роли и права доступа
- журналирование действий

Бизнес-модули:

- задачи
- календарь
- финансы
- документы

Инфраструктура:

- PostgreSQL
- файловое хранилище
- уведомления через Matrix
- web push
- reverse proxy (HTTPS)
- система резервного копирования

---

### Роли

- admin — управление семьёй и доступами
- user — работа с личными и общими данными

---

### Аутентификация

Используется JWT.

Сценарий:

- регистрация (email + пароль)
- вход
- получение access и refresh токенов
- обновление токена
- logout
- запрос на сброс пароля
- подтверждение сброса пароля

На этапе MVP:

- без подтверждения email
- без 2FA
- восстановление пароля есть

---

### Хранение данных

- PostgreSQL — структурированные данные
- файловая система — документы
- метаданные — в БД

---

### Клиенты

- браузер (ПК)
- браузер (мобильный)

---

### Roadmap

Этап 0 — Подготовка проекта  
Этап 1 — Auth + Users + Families  
Этап 2 — Органайзер  
Этап 3 — Календарь  
Этап 4 — Финансы  
Этап 5 — Документы  
Этап 6 — Уведомления  
Этап 7 — Усиление безопасности  

---

### Развёртывание

Система работает в Docker:

- backend (FastAPI)
- PostgreSQL
- reverse proxy
- файловое хранилище
- сервис резервного копирования

Для текущего локального этапа уже подготовлена рабочая docker-связка как минимум для:

- backend
- PostgreSQL

---

### Безопасность

Система работает с чувствительными данными:

- личные данные
- финансы
- документы

Обязательные меры:

- хеширование паролей
- контроль токенов
- HTTPS
- контроль доступа
- журналирование
- резервное копирование

---

### Статус

Проект уже находится не только в фазе проектирования.

Текущее состояние:

- backend-структура собрана
- FastAPI-приложение существует
- auth API, схемы, сервисы, репозитории и ORM-модели реализованы
- конфигурация централизована через env
- подготовлен Docker-запуск для локального тестирования backend + PostgreSQL
- auth-ядро находится в фазе стабилизации и проверки

Статус этапов:

- Stage 0 фактически закрыт как фундамент
- Stage 1 реализован по структуре
- ТЗ 3 в значительной части закрыто по коду и инфраструктурной обвязке
- до полного закрытия этапа остаются финальные smoke-тесты и несколько review/recheck пунктов
