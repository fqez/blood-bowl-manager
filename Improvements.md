# Blood Bowl Manager — Backend Roadmap

Tareas pendientes ordenadas por prioridad. Cada tarea incluye descripción del endpoint/lógica a implementar y qué archivos afecta.

---

## 🔐 1. Autenticación real

**Estado:** ✅ Completada (11/04/2026)
**Prioridad:** Alta — bloquea todo lo multiusuario

Autenticación segura con JWT + bcrypt + refresh token rotation implementada.

**Endpoints implementados:**

- ✅ `POST /auth/register` (201) — Registro con validación de fortaleza de password
- ✅ `POST /auth/login` (200) — Login, devuelve `access_token` + `refresh_token`
- ✅ `POST /auth/refresh` (200) — Rotación de refresh token (token family)
- ✅ `POST /auth/logout` (204) — Revoca todos los refresh tokens del usuario
- ✅ `GET /auth/me` (200) — Perfil del usuario autenticado

**Implementación:**

**Archivos creados:**
- `auth/password_utils.py` — bcrypt hash/verify + SHA-256 para tokens + `validate_password_strength()`
- `auth/token_service.py` — Generación y decodificación de access (15min) / refresh (7 días) JWT
- `schemas/auth.py` — `RegisterRequest`, `LoginRequest`, `RefreshRequest`, `TokenResponse`, `UserProfile`
- `services/auth_service.py` — Lógica de registro, login, refresh con rotación segura de tokens
- `routes/auth.py` — Los 5 endpoints de autenticación

**Archivos modificados:**
- `models/user/user.py` — `StoredToken` (embedded), `refresh_tokens[]`, `is_active`, `email_verified`
- `auth/jwt_bearer.py` — Reescrito con `get_current_user` dependency (valida JWT y retorna `user_id`)
- `config/config.py` — `ACCESS_TOKEN_EXPIRE_MINUTES=15`, `REFRESH_TOKEN_EXPIRE_DAYS=7`
- `routes/user_team.py`, `routes/league.py` — Reemplazado mock `get_current_user_id()` por `get_current_user`
- `app.py` — incluye `AuthRouter`, protege `/user-teams` y `/leagues` con `Depends(get_current_user)`

**Características de seguridad:**
- ✅ Passwords: bcrypt (12 rounds) con validación de fortaleza (min 8 chars, mayús, número, símbolo)
- ✅ JWT: HS256, access 15min + refresh 7 días con family_id para detección de robo
- ✅ Refresh tokens: almacenados hasheados en BD (nunca en claro), máx 5 sesiones concurrentes
- ✅ Token rotation: nuevo family_id en cada refresh (si se detecta reuso → revoca toda familia)
- ✅ Email + IP logging para auditoría
- ✅ Protección contra timing attacks (constant-time password comparison)

**Testing realizado:**
- ✅ `POST /auth/register` → 201 + tokens
- ✅ `POST /auth/login` → 200 + tokens con `expires_in: 900`
- ✅ `GET /auth/me` → perfil del usuario autenticado
- ✅ `POST /auth/refresh` → rotación segura de tokens
- ✅ Ruta protegida sin token → 401 Unauthorized
- ✅ Password incorrecto → 401 Unauthorized
- ✅ Registración duplicada (email/username) → 400 Bad Request

---

## 🎲 2. SPP — Award Star Player Points

**Estado:** ❌ Pendiente
**Prioridad:** Alta — núcleo del juego de liga

El modelo `UserPlayer` ya tiene `spp: int` y `career: PlayerCareer` pero no hay ningún endpoint para actualizarlos. Tras cada partido los jugadores ganan SPPs según sus acciones.

**Tabla oficial de SPPs:**

- 1 SPP por completar un pase
- 1 SPP por interceptar
- 2 SPPs por touchdown
- 2 SPPs por causar una baja (casualty)
- 4 SPPs por ser elegido MVP

**Endpoints a implementar:**

- `POST /user-teams/{team_id}/players/{player_id}/award-spp` — Body: `{ touchdowns, completions, interceptions, casualties, is_mvp }`
  Calcula los SPPs totales, actualiza `career` y suma al campo `spp` acumulado del jugador.

**Archivos afectados:**

- `routes/user_team.py`
- `services/user_team_service.py`
- `schemas/user_team.py` (nuevo schema `AwardSppRequest`)

---

## 📈 3. Level Up — Mejora de jugadores

**Estado:** ❌ Pendiente
**Prioridad:** Alta — consecuencia directa de los SPPs

Cuando un jugador acumula suficientes SPPs cruza un umbral y puede elegir una mejora. Los umbrales reglamentarios son: 3, 6, 10, 15, 21, 28, 36, 45, 55, 70 SPPs.

**Tipos de mejora posibles:**

- **Random Primary** — Tirar en tabla aleatoria de categoría primaria del jugador (2d6)
- **Random Secondary** — Tirar en tabla aleatoria de categoría secundaria (2d6)
- **Chosen Primary** — Elegir cualquier skill de categoría primaria
- **Chosen Secondary** — Elegir cualquier skill de categoría secundaria
- **Stat Increase** — Tirar en tabla de mejora de estadística (opcional por nivel)

**Endpoints a implementar:**

- `GET /user-teams/{team_id}/players/{player_id}/level-up-options` — Devuelve qué mejoras están disponibles para el jugador según sus SPPs y categorías de acceso (primary_access / secondary_access de su BasePlayer)
- `POST /user-teams/{team_id}/players/{player_id}/level-up` — Body: `{ improvement_type, skill_id? }` — Aplica la mejora elegida

**Archivos afectados:**

- `routes/user_team.py`
- `services/user_team_service.py`
- `services/progression_service.py` (nuevo — lógica de tablas de SPP)
- `schemas/user_team.py` (nuevos schemas `LevelUpOption`, `LevelUpRequest`)

---

## 🏥 4. Lesiones permanentes

**Estado:** ❌ Pendiente
**Prioridad:** Alta — sin esto los partidos no tienen consecuencias

El modelo tiene `injuries: list[str]` pero no hay lógica para aplicarlas. Cuando un jugador es "Casualty" en un partido, se tira en la tabla de lesiones permanentes.

**Tabla de lesiones (Casualty Roll d16/d6+d6):**

- Badly Hurt → sin efecto permanente
- Broken Ribs / Groin Strain / Gouged Eye /... → MNG (falta siguiente partido)
- Smashed Knee → -1 MA permanente
- Smashed Arm → -1 PA permanente
- Smashed Hip → -1 AV permanente
- Smashed Collar Bone → -1 ST permanente
- Niggling Injury → Niggling (tira cada partido para ver si agrava)
- Dead → el jugador muere

**Endpoints a implementar:**

- `POST /user-teams/{team_id}/players/{player_id}/apply-injury` — Body: `{ injury_type }` — Aplica la lesión: modifica stats si corresponde, actualiza `status`, añade a `injuries[]]`
- `POST /user-teams/{team_id}/players/{player_id}/apothecary` — Si el equipo tiene apothecary, permite re-tirar una lesión permanente (una vez por partido)

**Archivos afectados:**

- `routes/user_team.py`
- `services/user_team_service.py`
- `services/injury_service.py` (nuevo — tabla completa de lesiones)
- `schemas/user_team.py` (nuevo schema `ApplyInjuryRequest`)

---

## ☠️ 5. Retiro y muerte de jugadores

**Estado:** ❌ Pendiente
**Prioridad:** Media

Los jugadores pueden morir en partido o ser retirados voluntariamente. Deben quedar en un histórico pero no formar parte del equipo activo.

**Endpoints a implementar:**

- `POST /user-teams/{team_id}/players/{player_id}/retire` — Mueve el jugador a `retired_players[]` y libera su número
- `DELETE /user-teams/{team_id}/players/{player_id}` (fire) — Ya existe, confirmar que el valor de tesorería no cambia (lo perdiste al contratarlo)

**Cambios en modelo:**

- Añadir `retired_players: list[UserPlayer]` al `UserTeam` para conservar el historial

**Archivos afectados:**

- `models/user_team/team.py`
- `services/user_team_service.py`

---

## 🛒 6. Compra de skills en liga

**Estado:** ❌ Pendiente
**Prioridad:** Media

En Blood Bowl 2025, además del level-up por SPP al cruzar umbral, los jugadores pueden **comprar** skills adicionales usando SPPs y pagando oro en la fase pre-temporada o tras el level up.

**Reglas:**

- Primary skill: 6 SPPs + coste en gold según el nivel actual del jugador
- Secondary skill: 8 SPPs + coste en gold
- Solo skills de las categorías habilitadas para ese tipo de jugador

**Endpoints a implementar:**

- `POST /user-teams/{team_id}/players/{player_id}/buy-skill` — Body: `{ skill_id }` — Valida SPPs, verifica categoría accesible, descuenta del treasury y aplica la skill

**Archivos afectados:**

- `routes/user_team.py`
- `services/user_team_service.py`
- `schemas/user_team.py` (nuevo schema `BuySkillRequest`)

---

## 📋 7. Secuencia post-partido (Aftermatch)

**Estado:** ❌ Pendiente
**Prioridad:** Alta — flujo principal tras registrar resultado

Después de cada partido, Blood Bowl tiene una secuencia obligatoria de acciones. Actualmente solo existe `POST /leagues/{league_id}/matches/{match_id}/result`.

**Secuencia completa:**

1. Calcular ganancias de tesorería (Winnings roll D6 × resultado + fanfactor)
2. Tirar para jugadores lesionados (Casualty Roll)
3. Apothecary (si disponible)
4. Asignar SPPs a jugadores participantes
5. Asignar MVP aleatorio (1 por equipo)
6. Nivel de fans (dedicated_fans puede subir o bajar)
7. Actualizar team value

**Endpoints a implementar:**

- `POST /leagues/{league_id}/matches/{match_id}/aftermatch` — Body: `{ home_spp_awards, away_spp_awards, home_injuries, away_injuries }` — Ejecuta toda la secuencia y devuelve un resumen de lo que ocurrió
- `GET /leagues/{league_id}/matches/{match_id}/aftermatch-summary` — Devuelve el resumen del aftermatch si ya fue procesado

**Archivos afectados:**

- `routes/league.py`
- `services/league_service.py`
- `services/aftermatch_service.py` (nuevo)
- `schemas/league.py` (nuevos schemas `AftermatchRequest`, `AftermatchSummary`)

---

## 📅 8. Generación de calendario (Schedule)

**Estado:** ❌ Pendiente
**Prioridad:** Media

Al iniciar una liga con N equipos, hay que generar el calendario completo de partidos (round-robin: cada equipo se enfrenta a todos los demás una vez, o dos veces).

**Endpoints a implementar:**

- `POST /leagues/{league_id}/generate-schedule` — Genera los partidos usando algoritmo round-robin. Solo el propietario de la liga puede hacerlo, y solo en estado `DRAFT`
- `GET /leagues/{league_id}/schedule` — Devuelve todos los partidos organizados por jornada (round 1, round 2...)

**Archivos afectados:**

- `routes/league.py`
- `services/league_service.py` (añadir lógica round-robin)
- `schemas/league.py` (nuevo schema `ScheduleResponse`)

---

## 🏅 9. Clasificación extendida

**Estado:** ❌ Pendiente
**Prioridad:** Media

La `LeagueStanding` actual solo tiene wins/draws/losses. Falta añadir campos y lógica de desempate reglamentaria.

**Campos a añadir:**

- `casualties_caused` / `casualties_received`
- `fan_factor_average`
- `points` calculados (3 por victoria, 1 por empate)
- `touchdown_diff` calculado
- Cálculo automático de puntos de desempate (head-to-head, TD diff, CAS diff)

**Endpoints a implementar:**

- `GET /leagues/{league_id}/standings` — Devuelve clasificación ordenada aplicando todos los criterios de desempate reglamentarios

**Archivos afectados:**

- `models/league/league.py` (ampliar `LeagueStanding`)
- `services/league_service.py`
- `schemas/league.py`

---

## 🪄 10. Inducciones pre-partido

**Estado:** ❌ Pendiente
**Prioridad:** Media

Antes de un partido, el equipo con menor Team Value recibe "petty cash" para contratar inducciones temporales: Re-rolls extra, Bribes, Wizards, Star Players, etc.

**Reglas:**

- Petty cash = diferencia de TV entre ambos equipos (en gold)
- Con ese dinero se puede comprar de la lista de inducciones disponibles para ese tipo de equipo

**Endpoints a implementar:**

- `GET /leagues/{league_id}/matches/{match_id}/inducements` — Calcula el petty cash disponible para cada equipo y devuelve qué inducciones puede comprar cada uno
- `POST /leagues/{league_id}/matches/{match_id}/inducements` — Registra las inducciones elegidas para el partido

**Archivos afectados:**

- `routes/league.py`
- `services/inducement_service.py` (nuevo — catálogo completo de inducciones BB2025)
- `schemas/league.py`

---

## 📊 11. Rankings globales

**Estado:** ❌ Pendiente
**Prioridad:** Baja

Rankings entre todos los usuarios de la plataforma.

**Endpoints a implementar:**

- `GET /rankings/teams?sort_by=team_value|wins|touchdowns&limit=50` — Top equipos
- `GET /rankings/players?sort_by=spp|touchdowns|casualties&limit=50` — Top jugadores de todos los equipos
- `GET /rankings/leagues` — Ligas más activas/recientes

**Archivos afectados:**

- `routes/rankings.py` (nuevo)
- `services/rankings_service.py` (nuevo)
- `schemas/rankings.py` (nuevo)

---

## 🕰️ 12. Historial de partidos por equipo

**Estado:** ❌ Pendiente
**Prioridad:** Media

Un equipo puede jugar en múltiples ligas a lo largo del tiempo. Actualmente no hay forma de consultar todos los partidos jugados por un equipo concreto.

**Endpoints a implementar:**

- `GET /user-teams/{team_id}/matches?status=completed&limit=20` — Historial completo de partidos de un equipo con resultado, rival, TDs, bajas

**Archivos afectados:**

- `routes/user_team.py`
- `services/user_team_service.py`

---

## ✅ 13. Validador de equipo

**Estado:** ❌ Pendiente
**Prioridad:** Media

Antes de poder jugar un partido, el equipo debe superar una validación reglamentaria.

**Reglas a validar:**

- Mínimo 11 jugadores con `status = HEALTHY` o `MISSING_NEXT_GAME` que no falten este partido
- No exceder el máximo de jugadores por tipo (según BaseRoster)
- El número de rerolls no excede el máximo (8)
- Si el equipo tiene apothecary, verificar que el roster lo permite (`apothecary_allowed`)

**Endpoints a implementar:**

- `GET /user-teams/{team_id}/validate` — Devuelve `{ valid: bool, errors: list[str], warnings: list[str] }`

**Archivos afectados:**

- `routes/user_team.py`
- `services/validation_service.py` (nuevo)
- `schemas/user_team.py` (nuevo schema `TeamValidationResult`)

---

## 💰 14. Recálculo de Team Value

**Estado:** ❌ Pendiente
**Prioridad:** Media

El Team Value (TV) es crítico para calcular inducciones y determinar quién tiene ventaja. Actualmente `team_value` es un campo estático. Debe recalcularse automáticamente tras contratar/despedir jugadores, subir de nivel o modificar el staff.

**Fórmula:**

- TV = Σ(valor_actualizado_de_cada_jugador) + (rerolls × coste_reroll) + (apothecary ? 50000 : 0) + (assistant_coaches × 10000) + (cheerleaders × 10000) + (fan_factor × 10000)
- El valor actualizado de un jugador = coste_base + (15000 × número_de_skills_adquiridas) + bonificaciones_por_stats

**Implementar como:**

- Función interna `recalculate_team_value(team: UserTeam) -> int` llamada automáticamente en los servicios tras cualquier modificación al equipo
- `POST /user-teams/{team_id}/recalculate-value` — endpoint manual por si acaso

**Archivos afectados:**

- `services/user_team_service.py`
- `services/team_value_service.py` (nuevo)

---

## 🏁 15. Fin de temporada

**Estado:** ❌ Pendiente
**Prioridad:** Baja

Al completarse todos los partidos de una liga, hay que cerrar la temporada formalmente.

**Proceso:**

1. Verificar que todos los partidos están `completed`
2. Determinar el campeón (primero en clasificación)
3. Fase de pre-temporada: cada equipo puede vender jugadores, contratar nuevos, comprar staff
4. Opcionalmente generar una nueva temporada en la misma liga

**Endpoints a implementar:**

- `POST /leagues/{league_id}/end-season` — Cierra la liga, calcula campeón, habilita pre-temporada para los equipos participantes
- `GET /leagues/{league_id}/winner` — Devuelve el ganador de la liga

**Archivos afectados:**

- `routes/league.py`
- `services/league_service.py`

---

## Resumen de prioridades

| #   | Tarea                    | Prioridad | Estado       |
| --- | ------------------------ | --------- | ------------ |
| 1   | Auth real                | 🔴 Alta    | ✅ Completada |
| 2   | Award SPPs               | 🔴 Alta    | ❌ Pendiente  |
| 3   | Level Up                 | 🔴 Alta    | ❌ Pendiente  |
| 4   | Lesiones permanentes     | 🔴 Alta    | ❌ Pendiente  |
| 7   | Secuencia post-partido   | 🔴 Alta    | ❌ Pendiente  |
| 5   | Retiro/muerte            | 🟡 Media   | ❌ Pendiente  |
| 6   | Compra de skills         | 🟡 Media   | ❌ Pendiente  |
| 8   | Generación de calendario | 🟡 Media   | ❌ Pendiente  |
| 9   | Clasificación extendida  | 🟡 Media   | ❌ Pendiente  |
| 10  | Inducciones              | 🟡 Media   | ❌ Pendiente  |
| 12  | Historial de partidos    | 🟡 Media   | ❌ Pendiente  |
| 13  | Validador de equipo      | 🟡 Media   | ❌ Pendiente  |
| 14  | Recálculo de TV          | 🟡 Media   | ❌ Pendiente  |
| 11  | Rankings globales        | 🟢 Baja    | ❌ Pendiente  |
| 15  | Fin de temporada         | 🟢 Baja    | ❌ Pendiente  |
