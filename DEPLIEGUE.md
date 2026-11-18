# Flujo de Despliegue — CondominioX v5.1

Este documento es para el informe final. Describe:

- cómo pasa el código de un commit local a producción;
- el pipeline de CI/CD que lo valida;
- la configuración de Render;
- cómo verificar un deploy y cómo revertirlo.

**Última actualización:** 17 de noviembre de 2026

---

## 1. Visión general

CondominioX tiene un **despliegue desacoplado**: frontend y backend están en plataformas distintas, cada uno con su propio disparador, y solo se comunican por HTTP/JSON (REST + JWT).

| Componente | Plataforma | URL | Disparador |
|---|---|---|---|
| Frontend (HTML/CSS/JS estático) | GitHub Pages (rama `main`, raíz `/`) | https://laurarangel.github.io/condominiox-system/ | Merge a `main` |
| Backend (Flask + Gunicorn) | Render Web Service | https://condominiox-system.onrender.com/api | Merge a `main` (o deploy manual) |
| Base de datos | PostgreSQL 18 gestionado por Render | interna | No se redespliega; recibe migraciones idempotentes en cada arranque del backend |
| LLM del asistente | Groq (`openai/gpt-oss-120b`) | api.groq.com | Servicio externo, configurado por variables de entorno |

**Render y GitHub Actions son independientes.** Render observa la rama `main` y redespliega ante cada push, sin esperar a que terminen los workflows. En la práctica no hay riesgo, porque a `main` solo se llega por un PR con los checks en verde (ver 3.1). Render también ofrece el modo *"After CI Checks Pass"* para esperar a los checks, pero es una opción de su configuración.

---

## 2. Pipeline completo: de `git push` a producción

```
Desarrolladora
    │ git push origin <rama-feature>
    ▼
Pull Request hacia `main`
    ├── Tests (tests.yml)
    │     └── Python 3.12 + Postgres 16 como service container
    │     └── pytest --cov=.  →  225 tests (147 unitarias + 78 integración)
    ├── CodeQL (codeql.yml)
    │     └── SAST de Python y JavaScript
    └── Dependency Review (dependency-review.yml)
          └── bloquea si se introduce una dependencia con CVE alto/crítico
    │
    ▼
Ruleset de `main`: exige PR + 1 aprobación
    │
    ▼
Merge a `main`
    ├────────────────────────────┬──────────────────────────────────────┐
    ▼                            ▼                                      │
GitHub Pages                Render detecta el push                      │
publica la raíz             (o deploy manual desde el dashboard)        │
del repo tal cual               │                                       │
    │                        1. Build: pip install -r requirements.txt  │
    ▼                        2. Start: gunicorn importa app.py →        │
Frontend en                     migraciones idempotentes                │
laurarangel.github.io           (app.py + migrations.py)                │
                             3. Gunicorn atiende tráfico                │
                             4. Health check → la nueva instancia       │
                                reemplaza a la anterior                 │
                                 │                                      │
                                 ▼                                      │
                    API en condominiox-system.onrender.com/api          │
                                                                        │
                                       Dependabot corre aparte, ────────┘
                                       cada semana (pip + actions)
```

---

## 3. Detalle por etapa

### 3.1 Validación en el Pull Request (GitHub Actions)

1. **`tests.yml`**: suite de pruebas.
   - Levanta un *service container* `postgres:16` con la base `condominiox_test`.
   - Instala `requirements.txt` + `requirements-dev.txt` sobre Python 3.12.
   - Aplica `backend/schema.sql`, que trae el esquema completo, base + APF3.
   - Corre `pytest --cov=.` con 225 tests:
     - 147 unitarias (`tests/unit/`, sin base de datos): estructuras, dinero, seguridad, pasarelas, RAG, reglas de reserva, cliente LLM, documentos y disponibilidad en el asistente.
     - 78 de integración (`tests/integration/`): Flask `test_client()` contra Postgres real, con auth, propietarios, componentes APF3 y seguridad.
2. **`codeql.yml`**: análisis estático de seguridad (SAST) de Python y JavaScript. También corre cada semana.
3. **`dependency-review.yml`**: análisis de dependencias (SCA). Falla el PR si entra una dependencia con CVE alto o crítico.

**Dependabot** (`.github/dependabot.yml`) abre cada semana PRs de actualización para pip (`/backend`) y GitHub Actions. Esos PRs pasan por los mismos tres checks.

**Protección de `main`:**

- El *ruleset* `rs-branch-master` exige un PR con una aprobación antes del merge.
- Quien hace merge es la dueña del repositorio.
- Para hacer push y abrir PRs con `gh` hay que tener activa la cuenta con permisos de escritura sobre el repositorio.

### 3.2 Despliegue del frontend (GitHub Pages)

- Pages publica la raíz de `main` sin build: HTML, CSS y JS vanilla tal cual.
- `js/config.js` elige la API según el host:
  - en `localhost` o `127.0.0.1` → `http://localhost:5000/api`;
  - en cualquier otro → `https://condominiox-system.onrender.com/api`.
- **Caché:**
  - Los HTML cargan CSS y JS con `?v=AAAAMMDD`. Al cambiar un archivo hay que subir su sufijo en todos los HTML que lo usan.
  - Si aun así no se ven los cambios, recargar con `Cmd/Ctrl + Shift + R`.

### 3.3 Despliegue del backend (Render Web Service)

**Configuración del servicio:**

| Ajuste | Valor |
|---|---|
| Rama | `main` |
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app --workers 1 --timeout 60` |
| Health Check Path (recomendado) | `/api/health` |

Se usa **un solo worker** porque `LimitadorIntentos` (login) y el límite del asistente guardan su estado en memoria del proceso. Con varias instancias, ese estado tendría que pasar a Redis.

**Variables de entorno en Render:**

| Variable | Valor / nota | Requerida |
|---|---|---|
| `DATABASE_URL` | Internal Database URL de la base de Render | Sí |
| `JWT_SECRET` | Aleatoria, 32 caracteres o más | Sí |
| `JWT_EXPIRES_SECONDS` | Ej. `3600` (default) | No |
| `LLM_PROVIDER` | `groq` | Para el asistente |
| `GROQ_API_KEY` | Key de console.groq.com | Para el asistente |
| `LLM_MODEL` | `openai/gpt-oss-120b` | Sí en la práctica (ver 6.2) |
| `CORS_ORIGINS` | Solo si cambia el dominio del frontend (default: GitHub Pages + localhost) | No |
| `LLM_TIMEOUT`, `DIAS_DEUDA_VENCIDA`, `SLOW_QUERY_MS` | Defaults: 12, 30, 200 | No |

**Arranque:** al importar `app.py`, antes de atender tráfico, corren las migraciones:

1. `app.py`: crea `pagos_gastos`, `anuncios` y `lecturas_anuncios` si faltan, y la columna `anuncios.fecha_caducidad`.
2. `migrations.py` (`run_migrations()`):
   - agrega `recibos.monto_reservas`;
   - crea `areas_comunes`, `reservas`, `reserva_invitados`, `transacciones_pago`, `documentos`, `documento_fragmentos` y `consultas_asistente`;
   - siembra las 5 áreas comunes con `ON CONFLICT DO NOTHING`.

Todo es `IF NOT EXISTS` o condicionado, así que correrlo en cada deploy es seguro y no modifica datos existentes.

> **`seed_demo.py` nunca se corre en producción**: modifica los recibos existentes. Es solo para entornos de demo o locales.

**Plan gratuito:** el servicio se duerme sin uso. La primera petición tarda entre 30 y 60 s (*cold start*), y mientras tanto Render puede responder 502/503 **sin cabeceras CORS**. Ver 6.3.

### 3.4 Cambios en la base de datos

Antes de mergear un PR que trae migraciones nuevas:

1. **Backup** con `pg_dump` usando la *External Database URL* de Render (Render → base de datos → Connect):
   ```bash
   # pg_dump debe ser de la misma versión mayor que el servidor o superior (servidor: 18)
   brew install libpq
   /opt/homebrew/opt/libpq/bin/pg_dump "$DATABASE_URL_EXTERNA" -Fc -f backup_$(date +%Y%m%d).dump
   ```
2. Revisar qué tablas o columnas faltan, comparando `\dt` con `schema.sql`.
3. Mergear. Las migraciones corren solas al arrancar el backend.
4. Verificar que las tablas existan, que los datos sigan intactos (conteo de usuarios, propietarios y recibos) y que las áreas estén sembradas.

La URL externa de la base contiene la contraseña: no se versiona ni se comparte. Si se expone, hay que rotarla en Render.

### 3.5 Verificación posterior al deploy (smoke tests)

Esperar a que el deploy figure **Live** en Render y luego:

```bash
API=https://condominiox-system.onrender.com/api

curl -s $API/health                       # {"status":"ok"}
curl -s $API/health/db                    # {"status":"ok","db":"up",...}

# Rutas protegidas sin token → 401
curl -s -o /dev/null -w "%{http_code}\n" $API/areas-comunes
curl -s -o /dev/null -w "%{http_code}\n" $API/pagos/mios

# Cabeceras de seguridad
curl -sI $API/health | grep -iE "x-frame|x-content|strict-transport|content-security"

# CORS: el origen propio se permite, uno ajeno no
curl -sI -X OPTIONS $API/login -H "Origin: https://laurarangel.github.io" \
     -H "Access-Control-Request-Method: POST" | grep -i access-control-allow-origin
curl -sI -X OPTIONS $API/login -H "Origin: https://evil.example" \
     -H "Access-Control-Request-Method: POST" | grep -i access-control-allow-origin   # vacío
```

Después, **un solo login** por rol con credenciales correctas: 5 fallos seguidos bloquean 15 minutos. Con el token:

- Admin: `GET /api/pagos`, `GET /api/reservas` y `GET /api/areas-comunes?todas=1`.
- Propietario: `POST /api/asistente/consulta` con una pregunta. La respuesta debe traer `"modo": "ia"` y `"proveedor": "groq/..."`. Si trae `"respaldo"`, ver 6.2.

### 3.6 Rollback

- **Backend:**
  - Render permite volver a un deploy anterior desde Events → *Rollback*.
  - Lo recomendado es además revertir el PR en `main` (`git revert`), para que el historial y lo desplegado coincidan.
  - Las migraciones solo agregan tablas y columnas, así que el código anterior sigue funcionando con el esquema nuevo.
- **Base de datos:** restaurar el backup con `pg_restore --clean -d "$DATABASE_URL_EXTERNA" backup.dump`. Solo hace falta si se dañaron datos.
- **Frontend:** GitHub Pages sirve siempre el último `main`; el rollback es revertir el commit.

---

## 4. Entornos

| Entorno | Base de datos | Backend | Uso |
|---|---|---|---|
| Local | Postgres 16 en **podman** (`podman run ... -p 5439:5432`) + `.env` / `.env.test` | `flask run` / `python app.py` en `:5000` | Desarrollo y pruebas de integración |
| CI | Postgres 16 *service container* efímero | `test_client()` de Flask | Validación de cada PR |
| Producción | PostgreSQL 18 gestionado por Render | Gunicorn en Render | Usuarios reales |

El entorno local usa **podman**, no Docker: `podman machine start`, `podman run` y `podman exec`.

---

## 5. Resumen de disparadores

| Evento | Consecuencia |
|---|---|
| Push a una rama o PR abierto hacia `main` | Corren `tests.yml`, `codeql.yml` y `dependency-review.yml` |
| PR aprobado y mergeado a `main` | GitHub Pages republica el frontend y Render redespliega el backend |
| Arranque del backend | Migraciones idempotentes y luego el health check habilita el tráfico |
| Semanal | Dependabot abre PRs de actualización y CodeQL hace un escaneo programado |

---

## 6. Lecciones del despliegue APF3 (noviembre 2026)

### 6.1 Historial

| PR | Contenido | Resultado |
|---|---|---|
| #21 | APF3: pasarela, reservas, garantías, asistente IA, documentos y endurecimiento de seguridad | Backup previo; migraciones aplicadas sin pérdida de datos; corrección de 3 alertas de CodeQL antes del merge |
| #22 | PyJWT 2.15.1 y pytest 9.0.3 por alertas de Dependabot | 0 alertas abiertas; login y validación de tokens verificados en producción |
| #23 | El asistente responde la disponibilidad de áreas por fecha y hora | 225 tests en verde |

### 6.2 El asistente responde en "modo respaldo"

- **Síntoma:** el asistente responde en ~1 s con `"modo": "respaldo"`.
- **Causa:** Groq ya no ofrecía `llama-3.3-70b-versatile`, el modelo por defecto de `llm_client.py`, para la organización del proyecto.
- **Solución:** configurar `LLM_MODEL=openai/gpt-oss-120b` en Render.
- **Si vuelve a pasar:**
  - revisar los modelos disponibles en console.groq.com;
  - comprobar que `GROQ_API_KEY` esté cargada.
- Los modelos `llama-prompt-guard-*` son clasificadores de seguridad, no modelos de chat.

### 6.3 "Error de CORS" justo después de un merge

- **Síntoma:** el navegador muestra un error de CORS en el preflight de `/api/pagos`, `/api/documentos`, etc.
- **Causa:** durante un deploy o un *cold start*, Render responde 502/503 sin cabeceras CORS. El backend no tiene un problema de CORS.
- **Solución:** esperar a que el deploy esté *Live* y reintentar.
- **Mejora pendiente:** que `apiFetch` reintente automáticamente ante 502/503.

### 6.4 El merge no disparó el deploy

Si tras el merge Render sigue sirviendo el commit anterior:

1. Lanzar *Manual Deploy → Deploy latest commit*.
2. Confirmar en Events que el commit desplegado es el último de `main`.

### 6.5 Higiene de secretos

- No versionar:
  - `.env` y `.env.test`;
  - `.claude/settings.local.json`;
  - `.venv`, `__pycache__` y `.DS_Store`;
  - entregables generados (`Claude outputs/`).
- Si una credencial se comparte por un canal inseguro, rotarla: contraseña de la base en Render, API key de Groq o contraseñas de usuarios.

---

*Ver también: [README_INTEGRADOR.md](README_INTEGRADOR.md) (documento técnico integrador) y [DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md) (esquema SQL, estructuras, seguridad).*
