# UNTverse — Production Environment Variables Checklist

> Этот документ содержит **полный список** environment variables, необходимых для production деплоя UNTverse.

---

## 🗄️ Database

| Переменная | Обязательна | Описание | Пример |
|---|---|---|---|
| `DATABASE_URL` | ✅ Да | PostgreSQL connection string. Railway предоставляет автоматически. Формат `postgres://` будет преобразован в `postgresql+asyncpg://` автоматически. | `postgresql+asyncpg://user:pass@host:5432/unt_informatics` |
| `NEWS_INGESTION_SECRET` | ✅ Да | Секрет для ежедневного internal endpoint сбора новостей НЦТ. Минимум 32 случайных байта; не использовать JWT secret. | `python -c "import secrets; print(secrets.token_urlsafe(48))"` |

---

## 🔐 Security & JWT

| Переменная | Обязательна | Описание | Пример |
|---|---|---|---|
| `JWT_SECRET` | ✅ Да | Секретный ключ для подписи JWT токенов. **Минимум 64 символа**, криптографически случайная строка. Генерация: `python -c "import secrets; print(secrets.token_hex(64))"` | `a3f8b2c1d4e5...` (128 hex символов) |
| `JWT_ALGORITHM` | ❌ Нет | Алгоритм подписи JWT. По умолчанию `HS256`. | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ Нет | Время жизни access token в минутах. В production рекомендуется **15 минут**. | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | ❌ Нет | Время жизни refresh token в днях. По умолчанию **30 дней**. | `30` |

---

## 🔑 Google OAuth 2.0 PKCE

| Переменная | Обязательна | Описание | Пример |
|---|---|---|---|
| `GOOGLE_CLIENT_ID` | ✅ Да | Client ID из Google Cloud Console → APIs & Services → Credentials. | `123456789.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | ✅ Да | Client Secret из Google Cloud Console. **Никогда** не коммитить в репозиторий! | `GOCSPX-xxxxxxxxxxxxx` |
| `GOOGLE_REDIRECT_URI` | ✅ Да | OAuth callback URL. Должен совпадать с настройками в Google Console. | `https://untverse-backend.up.railway.app/api/v1/auth/oauth/google/callback` |

---

## 🌐 URLs & CORS

| Переменная | Обязательна | Описание | Пример |
|---|---|---|---|
| `FRONTEND_URL` | ✅ Да | URL фронтенда (Vercel). Используется для редиректов после OAuth. **Без trailing slash!** | `https://untverse.vercel.app` |
| `BACKEND_CORS_ORIGINS` | ✅ Да | JSON-массив разрешённых CORS origins. Должен включать URL фронтенда. | `["https://untverse.vercel.app", "https://unt-informatics.kz"]` |

---

## 🍪 Cookie Configuration

| Переменная | Обязательна | Описание | Пример |
|---|---|---|---|
| `AUTH_COOKIE_DOMAIN` | ❌ Нет | Домен для cookie. `None` = автоматически. Для кастомного домена — указать корневой домен. | `.unt-informatics.kz` |
| `AUTH_COOKIE_SECURE` | ❌ Нет | Отправлять cookie только через HTTPS. **В production обязательно `true`!** | `true` |
| `AUTH_COOKIE_SAMESITE` | ❌ Нет | SameSite policy для cookie. По умолчанию `lax`. | `lax` |

---

## ⚙️ Application

| Переменная | Обязательна | Описание | Пример |
|---|---|---|---|
| `ENVIRONMENT` | ✅ Да | Режим работы приложения. **В production строго `production`.** | `production` |
| `PORT` | ❌ Нет | Порт сервера. Railway задаёт автоматически. По умолчанию `8000`. | `8000` |

---

## 🖥️ Frontend (Vercel)

| Переменная | Обязательна | Описание | Пример |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | ✅ Да | Публичный URL бэкенда для API вызовов. | `https://untverse-backend.up.railway.app/api/v1` |
| `BACKEND_INTERNAL_URL` | ❌ Нет | Внутренний URL бэкенда для SSR rewrites. Если не задан, используется `NEXT_PUBLIC_API_URL`. | `https://untverse-backend.up.railway.app` |

---

## 📋 Checklist перед деплоем

- [ ] `JWT_SECRET` сгенерирован с помощью `python -c "import secrets; print(secrets.token_hex(64))"` (≥128 символов)
- [ ] `GOOGLE_CLIENT_ID` и `GOOGLE_CLIENT_SECRET` настроены в [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
- [ ] `GOOGLE_REDIRECT_URI` добавлен в Authorized redirect URIs в Google Console
- [ ] `FRONTEND_URL` указывает на production Vercel URL
- [ ] `BACKEND_CORS_ORIGINS` включает production frontend URL
- [ ] `AUTH_COOKIE_SECURE` = `true`
- [ ] `ENVIRONMENT` = `production`
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` = `15` (а не dev-значение 1440)
- [ ] `DATABASE_URL` указывает на Railway PostgreSQL (не SQLite!)
- [ ] `NEWS_INGESTION_SECRET` задан в Railway и в GitHub Actions secrets
- [ ] Все секреты добавлены через Railway Dashboard / Vercel Dashboard, а **НЕ** в `.env` файлы

---

## 🚀 Где задавать переменные

| Платформа | Где | Переменные |
|---|---|---|
| **Railway** (Backend) | Dashboard → Service → Variables | `DATABASE_URL`, `JWT_SECRET`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`, `FRONTEND_URL`, `BACKEND_CORS_ORIGINS`, `AUTH_COOKIE_DOMAIN`, `AUTH_COOKIE_SECURE`, `AUTH_COOKIE_SAMESITE`, `ENVIRONMENT`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS` |
| **Vercel** (Frontend) | Dashboard → Project → Settings → Environment Variables | `NEXT_PUBLIC_API_URL`, `BACKEND_INTERNAL_URL` |
| **Railway** (PostgreSQL) | Автоматически через Railway Plugin | `DATABASE_URL` (Railway задаёт автоматически при подключении PostgreSQL addon) |
