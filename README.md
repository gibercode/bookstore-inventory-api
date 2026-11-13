# Bookstore Inventory API

API REST para gestionar el inventario de una librería (Django + DRF + PostgreSQL).

## Levantar con Docker

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec api python manage.py seed_categories
```

La API queda en <http://localhost:8000>:

- Health check: <http://localhost:8000/api/v1/health/>
- Swagger: <http://localhost:8000/api/docs/>

## Comandos útiles

```bash
docker compose logs -f api   # ver logs
docker compose down          # parar (conserva los datos)
docker compose down -v       # parar y borrar la base de datos
```
