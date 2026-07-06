# Plan pristino de refactorizacion del backend

Este documento analiza el backend actual de `blood-bowl-manager` y propone una refactorizacion por fases pequenas, verificables y compatibles con el plan de migracion a rulesets versionados descrito en `README_RULESETS_MIGRATION_PLAN.md`.

Objetivo principal: rehacer/refactorizar el backend sin perder funcionalidad, separando datos de reglas, logica de dominio, persistencia, API y compatibilidad legacy. La prioridad no es cambiar la experiencia de usuario todavia, sino preparar una base profesional para que luego el frontend React consuma un backend canonico y versionado.

## 1. Resumen ejecutivo

El backend actual ya cubre mucha funcionalidad real: autenticacion, catalogos, equipos de usuario, progresion, ligas, partidos en vivo, postpartido, equipos temporales, inducements, reglas, estrellas, tacticas y quick matches.

El problema no es falta de funcionalidad, sino concentracion de responsabilidades y reglas mezcladas con codigo:

- `services/league_service.py` tiene unas 4400 lineas y mezcla ligas, permisos, fixtures, live match, eventos, standings, estadisticas dashboard, aftermatch, winnings, compras, heridas, SPP y temporales.
- `services/user_team_service.py` tiene unas 2400 lineas y mezcla acceso a equipos, serializacion, contratacion, valor de equipo, treasury, inducements, avances, lesiones, estrellas, jornaleros y normalizacion de skills.
- `database/seeding.py` tiene unas 2000 lineas y mezcla carga de JSON, parsers, conversores, datos largos de reglas, seeders, upserts y reconciliacion de datos embebidos.
- Hay datos de reglas en codigo Python que deberian vivir en `catalog/rulesets/<ruleset_id>/` segun el migration plan.
- Hay normalizacion de texto/IDs duplicada en `database/seeding.py`, `services/user_team_service.py`, `services/base_roster_service.py`, `services/star_player_service.py` y `utils/team_special_rules.py`.
- Hay endpoints legacy (`/teams`, `/characters`, `/perks`, `/admin`) mezclados con endpoints modernos sin una capa clara de compatibilidad.
- Hay codigo legacy y probablemente muerto que debe tener plan de retirada explicito: CRUD antiguo de `teams/characters`, auth admin paralela, modelos `match/tournament`, scripts one-shot de migracion/seed y colecciones residuales.
- El modelo `League` embebe `matches` y `events`; esto permite atomicidad sencilla, pero ya genera riesgo de documentos grandes y lecturas pesadas.

Estrategia recomendada: no reescribir todo de golpe. Primero congelar comportamiento con tests caracterizacion, luego extraer logica pura, despues mover catalogos a ficheros versionados, y solo entonces introducir endpoints versionados y `ruleset_id` en dominio.

## 2. Alcance de este documento

Incluye:

- Inventario funcional del backend actual.
- Code smells, malas practicas y riesgos por area.
- Relacion con `README_RULESETS_MIGRATION_PLAN.md`.
- Plan paso a paso para refactorizar sin pasos gigantes.
- Inventario de codigo legacy, codigo muerto y artefactos residuales que deben eliminarse o aislarse.
- Contexto de que hace cada pieza actualmente para no perder comportamiento.
- Criterios de salida y pruebas por fase.
- Dudas abiertas que conviene resolver antes de implementar algunas fases.

No incluye:

- Nuevo frontend React.
- Implementacion de codigo.
- Eliminacion inmediata de endpoints legacy sin medir uso, migrar datos y dejar compatibilidad temporal.
- Cambios de datos productivos sin migracion.

## 3. Funcionalidad actual que hay que preservar

### 3.1 Arranque y configuracion

Archivos actuales:

- `app.py`
- `config/config.py`
- `database/seeding.py`
- `models/__init__.py`

Contexto actual:

- `app.py` crea `FastAPI`, configura CORS y registra routers.
- `lifespan()` llama a `initiate_database()`.
- `initiate_database()` crea cliente Mongo o `mongomock`, inicializa Beanie y llama a `auto_seed_database()`.
- El seeding se ejecuta en arranque y reconcilia catalogos base.

Funcionalidad a preservar:

- La API debe arrancar aunque los catalogos esten vacios, siempre que existan los ficheros requeridos.
- Los catalogos base deben poder recrearse o reconciliarse de forma idempotente.
- Tests pueden usar mock DB con `USE_MOCK_DB`.

Malas practicas actuales:

- El arranque tiene side effects fuertes: conecta DB y ademas siembra contenido.
- Si `auto_seed_database()` falla, captura `Exception`, loguea, pero no necesariamente hace fallar el arranque. Esto puede dejar la app viva con catalogos incompletos.
- No hay separacion entre bootstrap de infraestructura y migracion/seed de datos.
- `secret_key` por defecto es `secret`, util para desarrollo pero peligroso si una configuracion productiva queda incompleta.

### 3.2 Autenticacion y usuarios

Archivos actuales:

- `routes/auth.py`
- `services/auth_service.py`
- `auth/token_service.py`
- `auth/password_utils.py`
- `auth/jwt_bearer.py`
- `models/user/user.py`

Contexto actual:

- Registro con validacion de password.
- Login por email/password.
- Access token JWT y refresh token.
- Refresh token rotation.
- Hash de refresh token en DB.
- Maximo de 5 sesiones concurrentes por usuario.
- Logout elimina refresh tokens.

Funcionalidad a preservar:

- Rotacion de refresh tokens.
- Revocacion completa si se reutiliza un refresh token no almacenado.
- `GET /auth/me` para perfil del usuario.
- Password hashing y validacion de fortaleza.

Malas practicas actuales:

- `AuthService` instancia `Settings()` directamente, lo que complica inyeccion de configuracion en tests.
- Los errores son `ValueError` y luego se traducen en rutas, en vez de excepciones de dominio tipadas.
- Falta una politica explicita de seguridad para cookies vs bearer tokens si el frontend React se va a usar como web real.

### 3.3 Admin legacy

Archivos actuales:

- `routes/admin.py`
- `models/user/admin.py`
- `auth/admin.py`

Contexto actual:

- Hay endpoints de login/signup admin.
- Parece heredado y separado del flujo moderno de usuarios.

Funcionalidad a preservar o decidir:

- Confirmar si admin se usa en UI o Postman.
- Si se mantiene, integrarlo en RBAC moderno.
- Si no se mantiene, marcarlo como legacy y protegerlo durante la transicion.

Malas practicas actuales:

- Sistema paralelo de usuarios/admins.
- No queda clara la frontera entre propietario de liga, comisario y admin global.

### 3.4 Catalogos base y reglas

Archivos actuales:

- `routes/base_roster.py`
- `services/base_roster_service.py`
- `routes/star_player.py`
- `services/star_player_service.py`
- `routes/rules.py`
- `services/rules_service.py`
- `models/base/*`
- `config/skills.json`
- `config/base_teams.json`
- `config/star_players.json`
- `database/seeding.py`
- `utils/team_special_rules.py`

Contexto actual:

- `base_rosters` contiene rosters base inmutables para crear equipos.
- `star_players` contiene estrellas y disponibilidad.
- `rules_catalog` contiene documentos como advancement, inducements, weather, kickoff, winnings, injuries, SPP, league points, dedicated fans y expensive mistakes.
- `/rules/catalogue` expone un indice hardcodeado en `RulesService.RULE_CATALOGUE`.
- `BaseRosterService` lee hatred keywords desde `config/base_teams.json` con cache, no desde DB.
- `utils/team_special_rules.py` contiene datos hardcodeados de chaos/favoured/star player requirements.

Funcionalidad a preservar:

- `GET /base-rosters`
- `GET /base-rosters/{roster_id}`
- `GET /base-rosters/hatred-keywords`
- `GET /base-rosters/{roster_id}/hatred-keywords`
- `GET /star-players`
- `GET /star-players/details`
- `GET /star-players/team/{team_id}` con `favoured_of` opcional.
- `GET /star-players/{star_player_id}`
- Todos los endpoints `/rules/*` actuales.

Malas practicas actuales:

- Datos de rulesets hardcodeados en Python.
- `rules_catalog` usa IDs globales no versionados, por ejemplo `advancement_rules` o `inducements`.
- Los mismos conceptos aparecen como IDs con estilos distintos: `perk-foo`, `foo_bar`, `foo-bar`, nombres visibles y nombres localizados.
- `BaseRoster.id` sigue siendo legacy slug, no ID canonico tipo `team.lizardmen`.
- `RulesService.RULE_CATALOGUE` duplica metadatos que deberian salir del catalogo versionado.
- Hatred keywords se calculan desde fichero JSON antiguo, no desde catalogo cargado/validado.

### 3.5 Equipos de usuario

Archivos actuales:

- `routes/user_team.py`
- `services/user_team_service.py`
- `models/user_team/team.py`
- `schemas/user_team.py`

Contexto actual:

- Un `UserTeam` pertenece a un usuario y referencia un `base_roster_id`.
- Los jugadores (`UserPlayer`) estan embebidos en el equipo.
- El equipo guarda treasury, rerolls, staff, apothecary, dedicated fans, notas, share code, icono y wallpaper.
- Los jugadores guardan stats actuales, skills/perks, SPP, avances, lesiones, estado y flags de temporal/journeyman.
- `UserTeam.calculate_team_value_breakdown()` calcula TV/CTV con costes hardcodeados para staff.
- `UserTeamService` gestiona creacion, detalle, resumen, actualizacion, borrado, contratacion, estrellas, despido, perks, avances, lesiones, valores y acceso.

Funcionalidad a preservar:

- Crear equipo con roster base y jugadores iniciales.
- Validar limite 16 jugadores permanentes vivos.
- Validar maximo por posicion.
- Cobrar treasury por jugadores, rerolls, staff, apothecary y dedicated fans iniciales.
- Bloquear boticario si roster no lo permite.
- Generar y resolver share code publico sin exponer notas.
- Permitir lectura a comisarios en contexto de liga.
- Permitir acceso en contexto de partido de liga o quick match.
- Bloquear gestion de roster cuando el equipo esta en liga activa, salvo acciones permitidas.
- Contratar jugadores permanentes.
- Contratar jornaleros temporales y mercenarios para partido.
- Contratar estrellas permanentes/temporales segun reglas actuales.
- Aplicar traits manuales y avances oficiales por SPP.
- Aplicar lesiones y reducciones de stat.

Malas practicas actuales:

- `UserTeamService` es un god service.
- Muchas funciones son `@staticmethod`, lo que impide inyeccion limpia de repositorios/calculadoras.
- Mezcla queries Mongo, autorizacion, reglas, calculos y serializacion de respuestas.
- Costes 10k/50k/30k/5k y limites viven en codigo.
- Reglas especiales se detectan por strings normalizados y busquedas parciales.
- Hay aliases hardcodeados como `plague_ridden -> infected` en varios sitios.
- `_next_available_number()` devuelve random si 1-99 esta ocupado, lo que puede crear numero duplicado.
- `get_team_detail_by_share_code()` hace fallback escaneando todos los equipos si no encuentra codigo; esto no escala.
- `UserTeam.calculate_team_value_breakdown()` vive en el modelo Beanie y conoce reglas de staff, mezclando entidad persistente con calculadora de dominio versionable.

### 3.6 Ligas

Archivos actuales:

- `routes/league.py`
- `services/league_service.py`
- `models/league/league.py`
- `schemas/league.py`

Contexto actual:

- Una liga tiene owner, commissioner_ids, invite_code, estado, formato, max_teams, rules, teams, standings y matches embebidos.
- Estados: draft, active, completed, cancelled.
- Matches embebidos guardan equipos snapshot, resultado, pre-match, live state, eventos, MVPs, gate y guards de aftermatch.
- `LeagueRules` hoy solo modela starting budget, resurrection, inducements, spiraling expenses y max team value.

Funcionalidad a preservar:

- Crear liga.
- Listar ligas publicas y ligas del usuario.
- Leer detalle con standings ordenados.
- Dashboard stats backend.
- Buscar por invite code.
- Editar settings por comisario.
- Borrar/archivar.
- Unirse/salir con equipo mientras esta en draft.
- Iniciar liga y generar calendario round robin o modo manual.
- Crear/editar/borrar partidos programados.
- Registrar resultado.

Malas practicas actuales:

- `LeagueService` es un god service aun mas grande que `UserTeamService`.
- `League` embebe `matches.events`; util al inicio, pero peligroso para ligas largas.
- Algunas lecturas usan `League.find(...).to_list()` y pueden arrastrar matches/events enormes si no usan proyeccion.
- `LeagueStanding.points` sigue calculando 3/1 estatico, mientras `LeagueService` usa `LeaguePointsRules`; hay dos fuentes conceptuales.
- `get_all_leagues()` no parece aplicar autorizacion, devuelve ligas en general.
- `_get_league()` intenta `ObjectId` y si falla devuelve `None`; hay otros sitios que duplican conversion.
- Round robin es simple y asigna rondas por pares con logica basica; hay que preservar si ya se espera, pero redisenarlo como generador testeable.

### 3.7 Partidos en vivo

Archivos actuales:

- `routes/league.py`
- `services/league_service.py`
- `models/league/league.py`
- `schemas/league.py`
- `services/quick_match_service.py`

Contexto actual:

- Match state: scheduled, in_progress, completed, cancelled.
- Pre-match permite weather, kickoff_event, current_team, ready flags, squads e inducement purchases/uses/details.
- Start match sanitiza squads, valida jugadores y setea turnos.
- Add/delete event actualiza eventos y marcador si touchdown.
- Update state modifica score, half, turn, current team, timers, rerolls, ready flags, squads, inducements, MVP, gate.

Funcionalidad a preservar:

- Solo participantes o comisarios gestionan match.
- Eventos solo en in_progress, salvo decision de temporales tras completed.
- Touchdown auto-incrementa score y al borrar evento revierte score.
- Turn timers guardan segundos por equipo.
- Squads excluyen jugadores no disponibles, salvo temporales del partido.

Malas practicas actuales:

- Logica de validacion live duplicada entre liga y quick match.
- Eventos son strings libres (`type`, `detail`) sin schema fuerte ni event taxonomy central.
- Flags internos como `BBM_SELF_INFLICTED:1` viven dentro de texto libre.
- `detail` se parsea con busquedas de texto en varios sitios.
- `UpdateMatchStateRequest` hace demasiadas cosas en un unico endpoint.

### 3.8 Aftermatch/postpartido

Archivos actuales:

- `services/league_service.py`
- `schemas/league.py`
- `models/base/spp.py`
- `models/base/injury.py`
- `models/base/winnings.py`
- `models/base/expensive_mistake.py`
- `models/base/dedicated_fans.py`

Contexto actual:

- `apply_aftermatch_spp()` realmente aplica el reporte completo postpartido.
- Hay flujo de submissions por lado: cada participante puede enviar su parte; cuando ambos han enviado se marca aplicado.
- Hay flujo de comisario/compatibilidad que puede aplicar ambos lados.
- Aplica SPP por eventos, MVP, throw teammate, reglas especiales como Brawlin Brutes.
- Aplica injuries, lasting injuries y reducciones de stat.
- Calcula winnings con dedicated fans, touchdowns y stalling.
- Aplica expensive mistakes.
- Aplica compras postmatch: jugadores, rerolls, staff, apothecary.
- Aplica Masters of Undeath/free raise dead.
- Finaliza temporales: keep/release, cobra si se mantienen, quita loner de journeyman si toca.
- Limpia `sent_off` al terminar.

Funcionalidad a preservar:

- Idempotencia con `aftermatch_spp_applied_at`.
- No permitir MVP para Star Players.
- No dar SPP a Star Players.
- Validar que jugadores participaron o estaban disponibles.
- Preservar submissions parciales por lado.
- Preservar alias `/aftermatch/spp` como compatibilidad.
- Preservar shortfall de treasury en settlement cuando procede.
- Preservar legacy live-charged temporary hires.

Malas practicas actuales:

- `apply_aftermatch_spp()` tiene duplicacion entre flujo por lado y flujo completo.
- Muchos helpers internos cierran sobre variables externas, dificil de testear.
- Reglas de negocio importantes estan en funciones anidadas y no en servicios/calculadoras nombradas.
- Winnings, expensive mistakes, purchases, injuries y SPP se aplican en una misma transaccion conceptual sin unidad explicita.
- Los eventos postmatch se appendan con strings de detalle que luego se parsean.

### 3.9 Inducements y temporales

Archivos actuales:

- `services/user_team_service.py`
- `models/base/inducement.py`
- `models/user_team/team.py`
- `models/league/league.py`

Contexto actual:

- `InducementRules` define budget rules e inducements.
- El calculo real del budget esta en `UserTeamService._match_inducement_budget_for_state()`.
- Para underdog: petty cash = diferencia CTV + gasto de treasury del favorito.
- Underdog puede aportar hasta 50k de treasury.
- Favorito puede gastar treasury.
- Si CTV es igual, nadie puede gastar treasury.
- Temporales de partido se excluyen del CTV del match.
- Mercenarios cuestan base + 30k.
- Jornaleros ganan Loner (4+) si no lo tienen.
- Riotous Rookies requiere Low Cost Linemen.
- Existe workaround para partidas antiguas con cargos live de temporales.

Funcionalidad a preservar:

- Snapshot de budget: petty_cash, treasury_allowance, total_available, spent, treasury_contribution, remaining, is_favorite, is_tied.
- Cost options por special_rule o roster.
- `required_special_rules` y disponibilidad.
- Liquidacion de treasury en aftermatch.
- Reserva de treasury para partidos en progreso/completed no finalizados.

Malas practicas actuales:

- `petty_cash_top_up_limit` existe en `InducementBudgetRules`, pero el calculo usa `50_000` hardcodeado.
- Staff costs tambien estan hardcodeados.
- `rules` puede ser `None` y se continua con defaults silenciosos.
- Cost options con `applies_to` son strings semanticos sin tipos fuertes.
- Workaround legacy no tiene fecha de retirada ni migracion explicita.

### 3.10 Quick matches

Archivos actuales:

- `routes/quick_match.py`
- `services/quick_match_service.py`
- `models/quick_match/quick_match.py`

Contexto actual:

- Quick match usa el mismo modelo `Match` embebido dentro de `QuickMatch`.
- Permite crear amistosos entre equipos no registrados en liga.
- Lista quick matches del owner.
- Get teams para rosters.
- Start, add event, delete event, update state, complete, delete.

Funcionalidad a preservar:

- Bloquear equipos registrados en liga.
- Reusar estructura de Match para UI live.
- Acceso solo a owner/participantes para team rosters.

Malas practicas actuales:

- Mucha logica duplicada con `LeagueService`.
- `list_quick_matches()` solo lista por `owner_id`, aunque `_user_can_access_qm()` reconoce participantes. Puede ocultar quick matches donde participas pero no eres owner.
- No valida jugadores de eventos como lo hace liga.
- No tiene aftermatch equivalente o decision explicita de no modificar equipos.

### 3.11 Tacticas

Archivos actuales:

- `routes/tactic.py`
- `services/tactic_service.py`
- `models/tactic/tactic.py`

Contexto actual:

- CRUD de formaciones/tacticas.
- Grid 12x14 para posicionamiento.
- Tactica pertenece a usuario.

Funcionalidad a preservar:

- Crear, listar, ver, editar y borrar tacticas.
- Validar ownership.

Malas practicas actuales:

- Dominio bastante aislado, bajo riesgo.
- Revisar si el grid deberia validarse con objeto de valor.

### 3.12 Endpoints legacy

Archivos actuales:

- `routes/team.py`
- `routes/character.py`
- `routes/perk.py`
- `services/team_operations.py`
- `services/character_operations.py`
- `services/perk_operations.py`
- `models/team/*`

Contexto actual:

- Mantienen modelo antiguo de team/character/perk.
- Conviven con `UserTeam` moderno.

Funcionalidad a preservar o retirar con cuidado:

- Confirmar si frontend actual aun llama estos endpoints.
- Mantenerlos durante transicion si hay clientes antiguos.
- Documentar fecha/criterio de deprecacion.

Malas practicas actuales:

- No hay capa `legacy` separada.
- No hay versionado de API.
- `Perk` legacy se usa tambien como catalogo canonico de skills, asi que no se puede borrar sin migracion.

## 4. Code smells globales

### 4.1 God services

Sintoma:

- `LeagueService` y `UserTeamService` contienen la mayoria de reglas de negocio.

Riesgo:

- Cada cambio toca archivos gigantes.
- La IA necesita mucho contexto para modificar una parte pequena.
- Tests se vuelven pesados o fragiles.
- Es facil romper reglas no relacionadas.

Direccion:

- Extraer calculadoras y servicios de dominio puros antes de cambiar comportamiento.

### 4.2 Modelos persistentes con logica versionable

Sintoma:

- `UserTeam.calculate_team_value_breakdown()` calcula costes de staff.
- `LeagueStanding.points` calcula puntos 3/1.

Riesgo:

- Contradice rulesets versionados.
- Dificulta cambiar reglas por liga/ruleset.

Direccion:

- Mover calculos a servicios/calculadoras que reciban `ruleset_id` o reglas cargadas.

### 4.3 Datos de reglas en codigo

Sintoma:

- `database/seeding.py` contiene tablas y textos largos.
- `utils/team_special_rules.py` contiene datos de favoured chaos y requisitos de estrellas.
- `RulesService.RULE_CATALOGUE` hardcodea indice de reglas.

Riesgo:

- No hay multi-ruleset.
- Cambiar contenido requiere deploy.
- Mezcla contenido posiblemente protegido con codigo.

Direccion:

- Mover a `catalog/rulesets/bb2020/*` con modelos Pydantic, validacion y conversores.

### 4.4 Normalizacion duplicada

Sintoma:

- Varias funciones hacen slugify, strip parameter, canonical id, localized fallback.

Riesgo:

- Un mismo skill puede resolverse distinto segun endpoint.
- Aliases se duplican y se olvidan.

Direccion:

- `shared/normalization.py` o `catalog_loader/normalization.py` con tests.

### 4.5 Strings libres para eventos y flags

Sintoma:

- `MatchEvent.type` es string libre.
- `detail` guarda flags parseables como `BBM_SELF_INFLICTED:1`.

Riesgo:

- Errores tipograficos rompen reglas.
- No hay contrato claro para frontend React.
- Parsing de texto en lugar de datos estructurados.

Direccion:

- Introducir `event_code`, `payload` estructurado y mantener `detail` solo display/compatibilidad.

### 4.6 Persistencia acoplada a dominio

Sintoma:

- Servicios llaman directamente a Beanie `get`, `find`, `save` en medio de calculos.

Riesgo:

- No se pueden testear reglas sin DB o mocks grandes.
- Dificulta transacciones y consistencia.

Direccion:

- Repositorios finos para IO y calculadoras puras para dominio.

### 4.7 Compatibilidad legacy no aislada

Sintoma:

- Endpoints antiguos y modernos conviven en `app.py` sin prefijo legacy.

Riesgo:

- La nueva arquitectura puede arrastrar decisiones antiguas.
- No hay claridad sobre que API debe consumir React.

Direccion:

- Versionar API nueva y documentar legacy.

## 5. Relacion con el migration plan

El documento `README_RULESETS_MIGRATION_PLAN.md` propone:

- `catalog/rulesets/<ruleset_id>` como fuente de conocimiento.
- IDs canonicos estables.
- Separar `rules_text` de `rules_logic`.
- Loader read-only antes de escribir DB.
- Validacion cruzada antes de seed.
- Conversores hacia modelos actuales.
- `ruleset_id` en catalogos y dominio.
- Endpoints versionados `/rulesets/...`.
- Compatibilidad temporal de endpoints legacy.

El backend actual esta a medio camino:

- Ya existen modelos de reglas en DB.
- Ya hay `config/skills.json`, `config/base_teams.json` y `config/star_players.json`.
- Ya hay endpoints de reglas.
- Pero falta `ruleset_id`, loader versionado, validacion cruzada, aliases externos, endpoints `/rulesets`, y separar reglas de codigo.

La refactorizacion debe seguir este orden:

1. Caracterizar comportamiento actual con tests.
2. Extraer logica pura sin cambiar API.
3. Crear catalogo versionado y loader read-only.
4. Convertir catalogo a modelos actuales.
5. Cambiar seeding para usar catalogo.
6. Anadir `ruleset_id`.
7. Crear endpoints versionados.
8. Migrar dominio de ligas/equipos/partidos a `ruleset_id`.

## 6. Arquitectura objetivo del backend

### 6.1 Capas recomendadas

Estructura objetivo orientativa:

```text
app/
  api/
    v1/
      routers/
      dependencies/
      schemas/
  auth/
  core/
    config.py
    logging.py
    errors.py
  domain/
    catalog/
    teams/
    leagues/
    matches/
    aftermatch/
    inducements/
    advancements/
  infrastructure/
    mongo/
    repositories/
    seeding/
  catalog_loader/
    models.py
    loader.py
    validation.py
    converters.py
  tests/
```

No hace falta renombrar todo de golpe. Se puede introducir por modulos nuevos mientras los routers actuales siguen funcionando.

### 6.2 Principios

- Routers solo traducen HTTP a comandos/queries.
- Servicios de aplicacion coordinan repositorios y dominio.
- Dominio calcula sin tocar DB.
- Repositorios encapsulan Beanie/Mongo.
- Catalogo versionado es fuente canonica de reglas.
- Modelos Beanie no contienen reglas versionables.
- Endpoints legacy siguen, pero no guian el nuevo diseno.

### 6.3 Regla critica para trabajar con IA

El codigo actual debe usarse como contrato de comportamiento, no como plantilla de diseno.

En cada chat/ticket independiente, la IA debe recibir referencias concretas al codigo actual que contiene la logica que se va a extraer. Eso evita que invente comportamiento, reglas de Blood Bowl o compatibilidad de datos. Pero la instruccion debe ser explicita: leer para entender, cubrir con tests y reimplementar limpio por piezas pequenas.

Instruccion recomendada para cada ticket:

```text
Usa el codigo actual como fuente de comportamiento, no como referencia de arquitectura.
Lee solo los archivos indicados en este ticket.
Preserva el comportamiento cubierto por tests de caracterizacion.
No copies la estructura de god services, duplicaciones, hardcodes o acceso directo a DB.
Extrae logica pura cuando sea posible.
Mantiene contratos publicos existentes salvo que el ticket indique migracion/deprecacion.
No modifiques archivos fuera del alcance sin justificarlo.
```

Reglas practicas:

- Si el paso refactoriza logica existente, primero leer el codigo actual y anadir tests de caracterizacion.
- Si el paso crea arquitectura nueva, leer codigo actual solo para entradas/salidas y casos limite; no replicar su estructura.
- Si el paso elimina legacy, leer imports, rutas, scripts y datos antes de borrar.
- Si un archivo actual supera cientos o miles de lineas, leer solo funciones/clases relacionadas con el paso.
- El resultado nuevo debe tener nombres de dominio claros, funciones pequenas, dependencias explicitas y tests enfocados.

## 7. Plan de refactorizacion paso a paso

Cada paso debe ser pequeno, verificable y apto para IA. No mezclar pasos de extraccion con cambios de comportamiento salvo que el paso lo diga expresamente.

### 7.0 Contexto actual a pasar a la IA por area

Para no gastar tokens leyendo todo el plan en cada chat, cada ticket debe copiar solo su fila de esta tabla, mas el paso concreto de la fase correspondiente.

| Area / fases                         | Codigo actual a leer                                                                                                                                                                                            | Como usarlo                                                                     | No copiar al diseno nuevo                                                                   |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Arranque, config y seeding inicial   | `app.py`, `config/config.py`, `database/seeding.py`, `models/__init__.py`                                                                                                                                       | Entender bootstrap, Beanie init, mock DB y seed idempotente                     | Side effects fuertes en startup,`Exception` generico, reglas largas dentro del seeder       |
| API actual e inventario              | `app.py`, `routes/*.py`, `schemas/*.py`                                                                                                                                                                         | Mapear endpoints, auth, request/response y compatibilidad                       | Shapes accidentales, respuestas inconsistentes, rutas legacy como base de`/api/v1`          |
| Auth y usuarios                      | `routes/auth.py`, `services/auth_service.py`, `auth/token_service.py`, `auth/password_utils.py`, `auth/jwt_bearer.py`, `models/user/user.py`                                                                    | Preservar registro, login, refresh rotation, logout y`/auth/me`                 | `Settings()` directo en servicio, `ValueError` como dominio, admin separado                 |
| Admin legacy                         | `routes/admin.py`, `models/user/admin.py`, `auth/admin.py`, `services/user_operations.py`                                                                                                                       | Confirmar comportamiento antes de unificar o eliminar                           | Sistema paralelo de identidad/autenticacion                                                 |
| Normalizacion e IDs                  | `database/seeding.py`, `services/user_team_service.py`, `services/base_roster_service.py`, `services/star_player_service.py`, `utils/team_special_rules.py`                                                     | Extraer aliases, slugify y canonical IDs comunes                                | Duplicar mapas de aliases o resolver IDs con strings ad hoc                                 |
| Team value                           | `models/user_team/team.py`, `services/user_team_service.py`, `tests/test_team_value.py`                                                                                                                         | Preservar breakdown, CTV, staff, temporales y casos cubiertos                   | Reglas versionables dentro del modelo Beanie                                                |
| Inducements                          | `models/base/inducement.py`, `services/user_team_service.py`, `services/league_service.py`, tests de temporales/valor si aplican                                                                                | Extraer coste, presupuesto, petty cash y purchases con tests                    | Hardcodear 50000, mezclar treasury con calculo puro, repetir low cost linemen               |
| Temporales, journeymen y stars       | `services/user_team_service.py`, `services/league_service.py`, `models/user_team/team.py`, `models/base/star_player.py`, `tests/test_temporary_player_finalization.py`                                          | Preservar finalizacion postmatch, legacy live charge y restricciones de roster  | Flags temporales dispersos, compensaciones sin documentar                                   |
| Avances, SPP y lesiones              | `services/user_team_service.py`, `models/user_team/team.py`, `models/base/advancement.py`, `models/base/injury.py`, `models/base/spp.py`, `tests/test_player_advancement_value.py`                              | Congelar coste SPP, skills, injuries, stat caps y cambios de valor              | Mutaciones grandes sin motor de reglas ni validadores claros                                |
| Match/live state                     | `models/league/league.py`, `routes/league.py`, `services/league_service.py`                                                                                                                                     | Preservar eventos, score, estados, permissions y transiciones                   | `detail` stringly typed como unica fuente de verdad                                         |
| Aftermatch                           | `services/league_service.py`, `services/user_team_service.py`, `models/league/league.py`, tests de commissioners/temporales                                                                                     | Extraer SPP, winnings, expensive mistakes, purchases, casualties e idempotencia | Un metodo coordinador gigante que modifica liga y equipos sin frontera                      |
| Reducir`LeagueService`               | `services/league_service.py`, `routes/league.py`, `models/league/league.py`, `tests/test_league_commissioners.py`                                                                                               | Identificar bloques por responsabilidad antes de extraer                        | Repartir codigo gigante en archivos gigantes nuevos                                         |
| Reducir`UserTeamService`             | `services/user_team_service.py`, `routes/user_team.py`, `models/user_team/team.py`, tests `test_user_team_*`                                                                                                    | Separar query, roster, economy, advancement, conditions, sharing                | Mantener acceso DB, serializacion y reglas en el mismo servicio                             |
| Catalog loader versionado            | `README_RULESETS_MIGRATION_PLAN.md`, `database/seeding.py`, `config/skills.json`, `config/base_teams.json`, `config/star_players.json`, `models/base/*.py`                                                      | Convertir datos actuales a schema versionado y validar referencias              | Generar/copiar texto oficial, hardcodear reglas Python, cargar Mongo desde loader read-only |
| Seeding desde catalogo               | `database/seeding.py`, `scripts/seed_database.py`, `scripts/seed_base_rosters.py`, `config/*.json`                                                                                                              | Preservar idempotencia y conversiones utiles                                    | Dos seeders divergentes, fallback silencioso a JSON legacy                                  |
| `ruleset_id` y endpoints versionados | `models/base/*.py`, `models/user_team/team.py`, `models/league/league.py`, `routes/base_roster.py`, `routes/rules.py`, `routes/star_player.py`                                                                  | Mantener compatibilidad mientras se introduce versionado                        | Query params ambiguos o mezclar rutas nuevas y legacy                                       |
| Repositorios/transacciones           | Servicios que hoy llaman Beanie directo:`services/user_team_service.py`, `services/league_service.py`, `services/auth_service.py`                                                                               | Encapsular persistencia y revisar atomicidad de aftermatch                      | Repositorios con reglas de negocio                                                          |
| Optimizar ligas/eventos              | `models/league/league.py`, `services/league_service.py`, `routes/league.py`                                                                                                                                     | Detectar lecturas pesadas y definir proyecciones/ADR                            | Migrar persistencia antes de aislar dominio                                                 |
| API v1 React                         | `app.py`, routers actuales, schemas actuales, necesidades del futuro frontend React                                                                                                                             | Definir contratos limpios y tipables                                            | Hacer que React dependa de shapes legacy accidentales                                       |
| Limpieza legacy/muerto               | `app.py`, `routes/team.py`, `routes/character.py`, `routes/perk.py`, `routes/admin.py`, `services/*_operations.py`, `models/match.py`, `models/tournament.py`, `database/database_dependencies.py`, `README.md` | Medir uso, migrar datos utiles y borrar con gate final                          | Borrar sin auditoria o dejar legacy mezclado con dominio nuevo                              |

Plantilla minima para cada chat/ticket:

```text
Trabaja solo en: Fase X, Paso Y.
Objetivo: <resultado concreto>.
Codigo actual a leer: <2-5 archivos maximo>.
Usa ese codigo como contrato de comportamiento, no como plantilla de diseno.
Malas practicas a evitar: <copiar del paso>.
Criterio de salida: <copiar del paso>.
Validacion: <tests/comandos concretos>.
No avances a otros pasos.
```

### Fase 0 - Preparacion y baseline

#### Paso 0.1 - Congelar inventario de endpoints

Contexto actual:

- Routers actuales: auth, admin, base-rosters, star-players, rules, perks, characters, teams, user-teams, leagues, quick-matches, tactics.

Trabajo:

- Crear `docs/backend/current-api-inventory.md` o extender este documento con tabla endpoint/metodo/request/response/auth.
- Marcar endpoints publicos, protegidos, legacy y compatibilidad.

Malas practicas a evitar:

- No usar nombres de endpoints en varios sitios sin fuente unica.
- No asumir que endpoint legacy no se usa.

Criterio de salida:

- Existe inventario de API actual.
- Cada endpoint tiene dominio propietario.

Validacion:

- Revisar routers.
- No requiere tests.

#### Paso 0.2 - Congelar comandos de validacion

Contexto actual:

- Instruccion de repo: usar `C:\Users\Franchoped\Software\bbman\Scripts\python.exe`.

Trabajo:

- Documentar en `docs/backend/development.md` los comandos:
  - `python -m compileall .`
  - `python -m pytest`
  - tests enfocados.
- Documentar que Francho prefiere arrancar servers manualmente.

Malas practicas a evitar:

- No crear otro virtualenv.
- No arrancar servicios persistentes salvo peticion explicita.

Criterio de salida:

- Cualquier IA sabe como validar backend.

#### Paso 0.3 - Crear tests de caracterizacion para rutas criticas

Contexto actual:

- Hay tests para auth, team value, temporary players, quick match, commissioners y algunos avances.

Trabajo:

- Anadir tests que capturen comportamiento actual antes de extraer codigo:
  - presupuesto de inducements favorito/underdog/empate.
  - reserved treasury para match pendiente.
  - share code sin notas.
  - star player availability con favoured_of.
  - SPP no se aplica a star players.
  - MVP requerido y prohibido a star players.
  - expensive mistakes dice obligatorios.
  - Masters of Undeath free purchase.
  - quick match no acepta equipos en liga.

Malas practicas a evitar:

- No cambiar implementacion mientras se escriben tests de caracterizacion.
- No testear detalles accidentales salvo los necesarios para compatibilidad.

Criterio de salida:

- Tests actuales siguen pasando.
- Los edge cases principales quedan cubiertos.

### Fase 1 - Aislar normalizacion e IDs

#### Paso 1.1 - Crear modulo de normalizacion compartido

Contexto actual:

- `slugify`, `_normal_key`, `_canonical_skill_id`, `_normalize_rule_keyword` y aliases se repiten.

Trabajo:

- Crear `utils/normalization.py` o `catalog_loader/normalization.py`.
- Mover funciones puras:
  - `english_text(value)`
  - `localized_text(value, locale, fallback)`
  - `strip_parenthetical(value)`
  - `extract_parenthetical(value)`
  - `slugify_snake(value)`
  - `slugify_kebab(value)`
  - `canonical_skill_id(value, aliases)`
  - `normalize_rule_keyword(value)`
- Crear tests unitarios con casos reales.

Malas practicas existentes a evitar:

- Aliases hardcodeados duplicados.
- Reglas de normalizacion distintas por servicio.
- Parsear texto localizado cuando hay ID canonico.

Criterio de salida:

- Ningun comportamiento cambia.
- Al menos `database/seeding.py`, `UserTeamService` y `StarPlayerService` usan el modulo comun para skill IDs.

#### Paso 1.2 - Externalizar aliases iniciales

Contexto actual:

- Alias `plague_ridden -> infected` aparece en seeding, user teams y star players.

Trabajo:

- Crear `config/catalog_aliases.json` temporal o esperar a `catalog/rulesets/bb2020/aliases.json` si se hace en la fase 4.
- Cargar aliases en normalizacion.
- Mantener fallback interno solo con warning durante transicion.

Malas practicas existentes a evitar:

- Meter nuevos aliases en funciones.
- Usar nombres visibles como identificador permanente.

Criterio de salida:

- Alias conocidos se resuelven desde datos.

### Fase 2 - Extraer calculos de equipo

#### Paso 2.1 - Crear `TeamValueCalculator`

Contexto actual:

- El calculo vive en `UserTeam.calculate_team_value_breakdown()` y wrappers de `UserTeamService`.

Trabajo:

- Crear `services/team_value_calculator.py` o `domain/teams/team_value.py`.
- Implementar funcion pura:
  - input: `UserTeam`, `BaseRoster`, `TeamValuationRules`.
  - output: `TeamValueBreakdown`.
- Dejar `UserTeam.calculate_team_value_breakdown()` como wrapper temporal o deprecarlo.

Malas practicas existentes a evitar:

- Costes de staff hardcodeados en el modelo.
- Repetir logica de low cost linemen en varios metodos.
- Acceder a DB desde calculadora.

Criterio de salida:

- Tests de `test_team_value.py` pasan.
- `UserTeamService._calculate_team_value_breakdown()` delega en calculadora.

#### Paso 2.2 - Crear reglas de valor de equipo versionables

Contexto actual:

- Assistant coach 10k, cheerleader 10k, apothecary 50k, dedicated fans 5k y mercenary surcharge 30k estan repartidos.

Trabajo:

- Crear modelo Pydantic de entrada `TeamEconomyRules` o ampliar catalogo `advancement/inducements` segun migration plan.
- Valores iniciales bb2020:
  - assistant coach cost.
  - cheerleader cost.
  - apothecary cost.
  - dedicated fan initial and purchase delta.
  - mercenary surcharge.
  - journeyman loner parameter.
- Usar defaults solo en capa de compatibilidad.

Malas practicas existentes a evitar:

- Anadir otro set de constantes globales sin ruleset.
- Mezclar costes de roster con costes de liga.

Criterio de salida:

- Un solo sitio define costes economicos globales.

#### Paso 2.3 - Extraer `TreasuryReservationService`

Contexto actual:

- `_pending_match_treasury_reservation()` y `_available_treasury_for_team_management()` viven en `UserTeamService` y dependen de matches activos/completed no finalizados.

Trabajo:

- Extraer servicio pequeno para calcular treasury disponible.
- Mantener consultas a liga en capa de aplicacion.
- Calculadora pura recibe snapshots de matches relevantes.

Malas practicas existentes a evitar:

- Consultar todas las ligas sin proyeccion.
- Mezclar reservas con contratacion de jugadores.

Criterio de salida:

- Tests cubren equipo con match in_progress, completed sin aftermatch y completed con aftermatch.

### Fase 3 - Extraer inducements y temporales

#### Paso 3.1 - Crear `InducementCostResolver`

Contexto actual:

- `_resolve_inducement_cost`, `_inducement_cost_option_applies` y `_team_has_inducement_rule` viven en `UserTeamService`.

Trabajo:

- Extraer resolucion de costes a modulo puro.
- Tipar `applies_to` internamente como objeto: `any`, `roster`, `special_rule`, `base_player_cost_plus`, `optional_primary_skill`.
- Mantener parser string para compatibilidad con datos actuales.

Malas practicas existentes a evitar:

- Comparar special rules por substring sin normalizacion controlada.
- Silenciar inducements desconocidos.

Criterio de salida:

- Tests cubren bribe, halfling chef, biased referee y unknown rule.

#### Paso 3.2 - Crear `InducementBudgetCalculator`

Contexto actual:

- `_match_inducement_budget_for_state()` calcula CTV, spend, petty cash, allowance y contribution.

Trabajo:

- Extraer calculadora pura.
- Inputs: match id, selected team id, teams, rosters, purchases, rules, league rules.
- Output: snapshot actual.
- Usar `rules.budget.petty_cash_top_up_limit` en vez de `50_000`.

Malas practicas existentes a evitar:

- Hardcodear 50k.
- Continuar si `InducementRules` falta.
- Calcular CTV y budget en la misma funcion si se puede separar.

Criterio de salida:

- `UserTeamService` solo carga datos y delega.
- Tests cubren favorito, underdog, empate, inducements disabled, gasto favorito, gasto underdog, treasury menor al allowance, temporales excluidos del CTV.

#### Paso 3.3 - Crear `TemporaryPlayerManager`

Contexto actual:

- Hiring temporal vive en `UserTeamService`; finalizacion vive en `LeagueService`; settlement esta en `UserTeamService`.

Trabajo:

- Extraer:
  - calcular coste mercenario.
  - aplicar loner a journeyman.
  - detectar temporal del match.
  - calcular settlement.
  - finalizar keep/release.
- Mantener las operaciones de guardado en servicios actuales.

Malas practicas existentes a evitar:

- Workaround legacy sin documento.
- Repetir `temporary_for_match` checks.
- Quitar Loner (4+) sin comprobar si el base player ya tenia loner.

Criterio de salida:

- Tests actuales de temporary finalization y team value pasan.
- Nuevo test documenta legacy live charge.

#### Paso 3.4 - Documentar retirada del workaround legacy

Contexto actual:

- Partidos antiguos antes del deferred inducement rollout pueden tener cargos live.

Trabajo:

- Crear comentario/documentacion en `docs/backend/legacy-data.md`.
- Definir criterio: migracion que marque matches afectados o fecha de corte.

Malas practicas existentes a evitar:

- Workarounds permanentes invisibles.

Criterio de salida:

- El workaround esta documentado y testeado.

### Fase 4 - Extraer progresion y lesiones

#### Paso 4.1 - Crear `PlayerAdvancementService`

Contexto actual:

- `apply_player_advancement`, `_apply_skill_advancement`, `_apply_characteristic_advancement`, random skill table y value increases viven en `UserTeamService`.

Trabajo:

- Extraer la logica de avance a modulo dedicado.
- Inputs: player, base player, request, advancement rules, skill catalog.
- Output: cambios a aplicar o `AdvancementResult`.

Malas practicas existentes a evitar:

- Consultar `Perk` desde dentro de calculadora.
- Recalcular advancement count con skills por nombres visibles.
- Usar string libre de `advancement_type` sin enum.

Criterio de salida:

- Tests de player advancement pasan.
- Hay tests para random primary completa.

#### Paso 4.2 - Crear `PlayerConditionService`

Contexto actual:

- `_apply_player_condition` y reducciones de stat aparecen en `UserTeamService` y duplicadas en `LeagueService` aftermatch.

Trabajo:

- Extraer aplicar lesion, muerte, sent_off, miss_next_game y lasting injury.
- Usar rules de injury como input.

Malas practicas existentes a evitar:

- Duplicar `_apply_stat_reduction`.
- Guardar estado `sent_off` sin ciclo claro de limpieza.

Criterio de salida:

- Una sola implementacion de reduccion de stat.

### Fase 5 - Extraer match/live state

#### Paso 5.1 - Crear `MatchAccessPolicy`

Contexto actual:

- Permisos de liga/equipo/match estan repartidos entre `LeagueService` y `UserTeamService`.

Trabajo:

- Crear policy functions:
  - can_view_league.
  - can_manage_match.
  - can_view_team_in_context.
  - can_edit_roster_as_commissioner.

Malas practicas existentes a evitar:

- Repetir checks y mensajes distintos.
- Confundir owner de liga, comisario, owner de equipo y participante.

Criterio de salida:

- Servicios actuales delegan permisos.
- Tests de commissioners pasan.

#### Paso 5.2 - Crear `MatchEventProcessor`

Contexto actual:

- Add/delete event, score sync, accidental/self-inflicted checks y player reference validation viven en `LeagueService`; quick match tiene version simplificada.

Trabajo:

- Introducir procesador comun para eventos live.
- Definir enum inicial de event types conocidos.
- Mantener `detail` como compatibilidad.
- Anadir `payload` opcional estructurado en modelo si se decide modificar schema.

Malas practicas existentes a evitar:

- Seguir parseando flags desde texto libre para casos nuevos.
- Divergencia entre liga y quick match.

Criterio de salida:

- Liga y quick match usan la misma logica para score por touchdown y delete event.

#### Paso 5.3 - Separar `MatchStateUpdater`

Contexto actual:

- `update_match_state` modifica muchos campos y crea eventos derivados.

Trabajo:

- Extraer updater puro que compare estado anterior y request.
- Crear eventos derivados de score/half/turn/weather/kickoff/reroll.

Malas practicas existentes a evitar:

- Un endpoint que cambie cualquier cosa sin reglas por estado.

Criterio de salida:

- Tests cubren pre-match only updates y updates in_progress.

### Fase 6 - Extraer aftermatch

#### Paso 6.1 - Crear `SppAwardEngine`

Contexto actual:

- Scoring de SPP se repite en flujo parcial y flujo completo.

Trabajo:

- Input: match events, post match events, teams, rosters, squads, rules.
- Output: deltas por jugador y eventos invalidos.
- Tratar Star Players, MVP, throw teammate, accidental casualty y self-inflicted.

Malas practicas existentes a evitar:

- Helpers anidados con closures.
- Parseo duplicado de `BBM_SELF_INFLICTED`.

Criterio de salida:

- Tests cubren cada tipo de SPP.

#### Paso 6.2 - Crear `AftermatchInjuryEngine`

Contexto actual:

- Injury application vive en funciones anidadas.

Trabajo:

- Input: injury requests, injury rules, team/player snapshots.
- Output: injury records, status changes, stat reductions, match events.

Malas practicas existentes a evitar:

- Duplicar casualty lookup.
- Aplicar injury sin validar jugador jugado.

Criterio de salida:

- Tests cubren casualty sin lasting, con lasting, dead, invalid rolls.

#### Paso 6.3 - Crear `WinningsEngine`

Contexto actual:

- Winnings, expensive mistakes y purchases se mezclan.

Trabajo:

- Separar:
  - calcular winnings.
  - aplicar expensive mistakes.
  - generar evento resumen.
- Inputs deben ser rules, team, opponent, touchdowns, stalling, dice.

Malas practicas existentes a evitar:

- Calcular expensive mistakes con indices sin validar rango.
- Texto de resumen como unica fuente de auditoria.

Criterio de salida:

- Tests cubren todos los bands/effects.

#### Paso 6.4 - Crear `PostMatchPurchaseService`

Contexto actual:

- Compras postmatch estan duplicadas en flujo parcial y completo.

Trabajo:

- Extraer compras de jugadores, rerolls, staff, apothecary.
- Recibir `TeamEconomyRules`.
- Reusar `UserPlayerFactory` para crear jugadores.

Malas practicas existentes a evitar:

- Costes 10k/50k hardcodeados.
- Duplicar Masters of Undeath.

Criterio de salida:

- Misma logica para submission parcial y completa.

#### Paso 6.5 - Crear `AftermatchApplicationService`

Contexto actual:

- `apply_aftermatch_spp()` coordina todo.

Trabajo:

- Mantener metodo publico actual, pero delegar en servicios:
  - store submission.
  - apply side report.
  - finalize both sides.
  - persist teams/match/league.

Malas practicas existentes a evitar:

- Rehacer el flujo y romper idempotencia.
- Cambiar la semantica del alias `/aftermatch/spp`.

Criterio de salida:

- `LeagueService.apply_aftermatch_spp()` baja a coordinador pequeno.
- Tests de aftermatch cubren partial submission y commissioner flow.

### Fase 7 - Reducir `LeagueService`

#### Paso 7.1 - Extraer `LeagueQueryService`

Contexto actual:

- Queries de summary, detail y dashboard estan mezcladas con comandos.

Trabajo:

- Mover `get_all_leagues`, `get_leagues_by_user`, `get_league_detail`, `get_league_dashboard_stats`.
- Usar proyecciones para summaries.

Malas practicas existentes a evitar:

- Cargar `matches.events` para listar ligas.

Criterio de salida:

- Respuestas iguales.
- Menos carga de documentos grandes.

#### Paso 7.2 - Extraer `LeagueLifecycleService`

Contexto actual:

- Crear, editar, join, leave, start, archive y delete estan en `LeagueService`.

Trabajo:

- Mover comandos de liga sin match live.
- Crear `FixtureGenerator` para round robin.

Malas practicas existentes a evitar:

- Generador de fixture sin tests.
- Mezclar owner/comisario con participante.

Criterio de salida:

- Tests de commissioners pasan.

#### Paso 7.3 - Extraer `LeagueMatchService`

Contexto actual:

- CRUD de calendario y record result en `LeagueService`.

Trabajo:

- Mover create/update/delete fixture y record result.
- Reusar `MatchEventProcessor` para casualties/score.

Malas practicas existentes a evitar:

- Actualizar standings en multiples sitios sin unidad.

Criterio de salida:

- Standings siguen iguales.

### Fase 8 - Reducir `UserTeamService`

#### Paso 8.1 - Extraer `UserTeamQueryService`

Contexto actual:

- Summaries y detail mezclan acceso, DB, serialization y calculos.

Trabajo:

- Mover summaries/detail/share code.
- Usar proyecciones en summaries.

Malas practicas existentes a evitar:

- Generar share code en lectura sin control transaccional.
- Buscar todos los equipos para fallback de share code indefinidamente.

Criterio de salida:

- Endpoint `/user-teams` mantiene respuesta.

#### Paso 8.2 - Extraer `UserTeamRosterService`

Contexto actual:

- Crear equipo, update staff, hire/fire player, hire star player estan juntos.

Trabajo:

- Mover comandos de gestion de roster.
- Usar `UserPlayerFactory`, `TeamValueCalculator`, `TreasuryReservationService`.

Malas practicas existentes a evitar:

- Restar treasury antes de validar todo.
- Crear jugador con numero duplicado.

Criterio de salida:

- Tests de user team numbers y team value pasan.

#### Paso 8.3 - Extraer `UserPlayerFactory`

Contexto actual:

- `_build_user_player`, `_perk_from_star_skill`, `_journeyman_loner_perk`, `_next_available_number` viven en `UserTeamService`.

Trabajo:

- Crear factory pura/asinc separada.
- Recibir skill lookup ya cargado si necesita nombres.

Malas practicas existentes a evitar:

- Factory que consulta DB para cada skill de estrella sin batch.

Criterio de salida:

- Contratacion y postmatch purchases usan la misma factory.

### Fase 9 - Catalog loader versionado

Esta fase debe seguir directamente el migration plan.

#### Paso 9.1 - Crear estructura `catalog/`

Trabajo:

- Crear:

```text
catalog/
  README.md
  schemas/
  rulesets/
    bb2020/
      ruleset.json
      skills.json
      teams.json
      inducements.json
      advancement.json
      tables.json
      documents.json
      aliases.json
```

Malas practicas existentes a evitar:

- Copiar texto largo protegido generado por IA.
- Meter logica Python en ficheros de datos.
- Duplicar frontend como fuente canonica.

Criterio de salida:

- JSON minimo valido.

#### Paso 9.2 - Crear modelos Pydantic de entrada

Trabajo:

- Crear `catalog_loader/models.py`.
- Modelos minimos:
  - `LocalizedTextData`
  - `RulesetManifestData`
  - `SkillCatalogData`
  - `TeamCatalogData`
  - `InducementCatalogData`
  - `AdvancementCatalogData`
  - `TableCatalogData`
  - `DocumentCatalogData`
  - `AliasCatalogData`

Malas practicas existentes a evitar:

- Reusar modelos Beanie como modelos de entrada.
- Permitir campos libres sin validacion cuando son reglas estructuradas.

Criterio de salida:

- Cargar JSON incompleto falla con error claro.

#### Paso 9.3 - Implementar loader read-only

Trabajo:

- Crear `catalog_loader/loader.py`.
- Funciones:
  - `list_rulesets(base_path)`
  - `load_ruleset(base_path, ruleset_slug_or_id)`
  - `load_json(path)`
- No tocar Mongo.

Malas practicas existentes a evitar:

- Validar despues de escribir DB.
- Resolver paths relativos al working directory sin control.

Criterio de salida:

- Test carga `bb2020` sin DB.

#### Paso 9.4 - Implementar validacion cruzada

Trabajo:

- Crear `catalog_loader/validation.py`.
- Validar:
  - IDs unicos.
  - Legacy IDs no colisionan.
  - Skills de positions existen.
  - Access categories existen.
  - Tables referenciadas existen.
  - Stats/costes/rangos correctos.
  - Locales obligatorios.

Malas practicas existentes a evitar:

- Normalizar silently un ID roto.
- Permitir textos vacios sin warning cuando se van a mostrar.

Criterio de salida:

- Un ID roto falla antes de DB.

#### Paso 9.5 - Crear conversores a modelos actuales

Trabajo:

- Crear `catalog_loader/converters.py`.
- Funciones:
  - `to_base_rosters(loaded)`
  - `to_perks(loaded)`
  - `to_star_players(loaded)` si se decide meter estrellas en catalogo.
  - `to_advancement_rules(loaded)`
  - `to_inducement_rules(loaded)`
  - `to_generic_rule_documents(loaded)`

Malas practicas existentes a evitar:

- Duplicar parsers viejos sin tests.
- Perder legacy IDs.

Criterio de salida:

- Conversores generan objetos compatibles con endpoints actuales.

#### Paso 9.6 - Script `scripts/validate_catalog.py`

Trabajo:

- Script sin DB.
- Output:
  - ruleset cargado.
  - counts de skills, teams, positions, inducements, tables.
  - errores y warnings.

Malas practicas existentes a evitar:

- Requerir API o Mongo para validar datos.

Criterio de salida:

- `python scripts/validate_catalog.py --ruleset bb2020` funciona.

### Fase 10 - Seeding desde catalogo

#### Paso 10.1 - Convertir `database/seeding.py` en orquestador

Contexto actual:

- `database/seeding.py` contiene todo.

Trabajo:

- Mover seeders antiguos a modulos temporales.
- Crear `seed_ruleset_catalog(ruleset_slug)`.
- Flujo:
  1. load.
  2. validate.
  3. convert.
  4. upsert.
  5. reconcile legacy user data si aplica.

Malas practicas existentes a evitar:

- Mantener bloques largos de contenido en Python.
- Fallback silencioso a seeders antiguos.

Criterio de salida:

- `auto_seed_database()` usa loader para `bb2020`.

#### Paso 10.2 - Mantener fallback controlado solo temporal

Trabajo:

- Si se conserva fallback antiguo, debe estar tras flag `ENABLE_LEGACY_SEED_FALLBACK` y log fatal/warning claro.

Malas practicas existentes a evitar:

- Que produccion use fallback sin saberlo.

Criterio de salida:

- Entorno local puede fallback si se decide, pero CI debe fallar si catalogo no carga.

### Fase 11 - `ruleset_id` en catalogos y dominio

#### Paso 11.1 - Anadir `ruleset_id` a catalogos DB

Trabajo:

- Modelos:
  - `BaseRoster`
  - `AdvancementRules`
  - `InducementRules`
  - `InjuryRules`
  - `WinningsRules`
  - `SppRewardsRules`
  - `DedicatedFansRules`
  - `LeaguePointsRules`
  - `WeatherRules`
  - `KickoffEventRules`
  - `StarPlayer`
  - `Perk` si skills se versionan.

Malas practicas existentes a evitar:

- Usar solo `_id` global y pisar ediciones.

Criterio de salida:

- Puede convivir `ruleset.bb2020` y otro ruleset sin overwrite.

#### Paso 11.2 - Resolver compatibilidad de IDs legacy

Trabajo:

- Decidir si `_id` DB sera canonico completo o compuesto.
- Opcion conservadora:
  - Mantener `_id` legacy para endpoints actuales.
  - Anadir `catalog_id` y `ruleset_id`.
  - Endpoints versionados usan `catalog_id`.

Malas practicas existentes a evitar:

- Cambiar `BaseRoster.id` sin migrar `UserTeam.base_roster_id`.

Criterio de salida:

- Equipos existentes siguen abriendo.

#### Paso 11.3 - Anadir `ruleset_id` a ligas/equipos/partidos

Trabajo:

- `League.ruleset_id` default `ruleset.bb2020`.
- `UserTeam.ruleset_id` default heredado de liga o seleccionado al crear.
- `Match.ruleset_id` snapshot opcional para proteger historico.

Malas practicas existentes a evitar:

- Resolver reglas siempre desde default global.
- Cambiar historico si el ruleset cambia.

Criterio de salida:

- Liga nueva persiste `ruleset_id`.
- Equipo dentro de liga hereda/resuelve ruleset.

### Fase 12 - Endpoints versionados

#### Paso 12.1 - Crear `rulesets` read API

Trabajo:

- Crear:
  - `routes/rulesets.py`
  - `services/ruleset_service.py`
  - `schemas/ruleset.py`
- Endpoints minimos:
  - `GET /rulesets`
  - `GET /rulesets/{ruleset_id}`
  - `GET /rulesets/{ruleset_id}/catalogue`
  - `GET /rulesets/{ruleset_id}/teams`
  - `GET /rulesets/{ruleset_id}/teams/{team_id}`
  - `GET /rulesets/{ruleset_id}/skills`
  - `GET /rulesets/{ruleset_id}/inducements`
  - `GET /rulesets/{ruleset_id}/advancement`
  - `GET /rulesets/{ruleset_id}/tables`
  - `GET /rulesets/{ruleset_id}/tables/{table_id}`

Malas practicas existentes a evitar:

- Reusar `/rules` para versionado con query params ambiguos.
- Duplicar response models con pequenas diferencias no documentadas.

Criterio de salida:

- React podra descubrir catalogos por ruleset.

#### Paso 12.2 - Mantener endpoints legacy

Trabajo:

- `/rules/*`, `/base-rosters/*`, `/star-players/*` usan default ruleset.
- Documentar deprecacion futura.

Malas practicas existentes a evitar:

- Romper frontend Flutter antes de React.

Criterio de salida:

- Contratos actuales siguen pasando.

### Fase 13 - Repositorios y transacciones

#### Paso 13.1 - Crear repositorios finos

Trabajo:

- Repositorios por agregado:
  - `UserTeamRepository`
  - `LeagueRepository`
  - `CatalogRepository`
  - `QuickMatchRepository`

Malas practicas existentes a evitar:

- Repositorios con logica de negocio.
- Servicios consultando Beanie directamente despues de la extraccion.

Criterio de salida:

- Nuevos servicios de dominio no importan Beanie.

#### Paso 13.2 - Revisar atomicidad

Contexto actual:

- Aftermatch modifica liga y dos equipos.

Trabajo:

- Evaluar transacciones Mongo si deployment lo soporta.
- Si no, guardar eventos/auditoria de compensacion.

Malas practicas existentes a evitar:

- Guardar equipo A, fallar equipo B y dejar aftermatch parcial sin marca.

Criterio de salida:

- Hay estrategia documentada de consistencia.

### Fase 14 - Optimizar modelo de liga y eventos

#### Paso 14.1 - Proyecciones obligatorias

Trabajo:

- Todas las lecturas summary usan proyeccion para excluir `matches.events`.

Malas practicas existentes a evitar:

- `League.find(...).to_list()` en rutas ligeras.

Criterio de salida:

- Tests o reviews confirman no cargar payload pesado.

#### Paso 14.2 - Evaluar separar matches a coleccion propia

Trabajo:

- No hacerlo al principio.
- Crear ADR comparando:
  - matches embebidos.
  - `league_matches` propia.
  - eventos propios `match_events`.

Malas practicas existentes a evitar:

- Migrar persistencia antes de aislar dominio.

Criterio de salida:

- Decision documentada con umbral: numero de equipos, partidos, eventos o tamano doc.

### Fase 15 - API v1 limpia para React

#### Paso 15.1 - Definir contratos nuevos

Trabajo:

- Crear OpenAPI revisada para React:
  - auth/session.
  - rulesets/catalog.
  - teams.
  - leagues.
  - matches.
  - aftermatch.
- Usar response models estables.

Malas practicas existentes a evitar:

- Dejar que React dependa de shapes legacy accidentales.

Criterio de salida:

- Front puede generar cliente tipado.

#### Paso 15.2 - Versionar rutas nuevas

Trabajo:

- Introducir `/api/v1/...` para React.
- Mantener rutas actuales como compatibility layer.

Malas practicas existentes a evitar:

- Mezclar endpoints nuevos y legacy sin prefijo.

Criterio de salida:

- Rutas nuevas tienen ownership y contrato.

### Fase 16 - Limpieza de codigo legacy y muerto

Esta fase no debe hacerse al principio. Su sitio natural es despues de tener tests de caracterizacion, catalogo versionado, endpoints `/rulesets` y `/api/v1`. La meta es que el backend final no conserve modulos antiguos solo por miedo: cada pieza debe estar en una de tres categorias claras.

Categorias:

- Mantener: codigo usado por flujos actuales y con ownership claro.
- Aislar temporalmente: codigo usado solo por compatibilidad Flutter/Postman/datos historicos.
- Eliminar: codigo sin ruta, sin test, sin import real o reemplazado por API/modelo nuevo.

#### Paso 16.1 - Medir uso real de endpoints legacy

Trabajo:

- Instrumentar logs o metricas por ruta legacy:
  - `/teams/*`
  - `/characters/*`
  - `/perks/*`
  - `/admin/*`
- Revisar Postman, frontend actual, scripts y logs de produccion.
- Crear `docs/backend/legacy-usage-inventory.md` con columna `uso confirmado`, `sustituto`, `fecha objetivo retirada`.

Malas practicas existentes a evitar:

- Borrar endpoints porque parecen viejos sin confirmar consumidores.
- Mantener endpoints legacy sin fecha de retirada ni sustituto.

Criterio de salida:

- Cada endpoint legacy tiene decision: mantener temporal, redirigir, deprecar o borrar.

#### Paso 16.2 - Mover compatibilidad a un paquete `legacy`

Trabajo:

- Mover routers/servicios/schemas legacy bajo un limite explicito:
  - `routes/legacy/team.py`
  - `routes/legacy/character.py`
  - `routes/legacy/perk.py` si sigue exponiendo shape antiguo.
  - `routes/legacy/admin.py` si admin no se unifica todavia.
  - `services/legacy/team_operations.py`
  - `services/legacy/character_operations.py`
  - `services/legacy/perk_operations.py`
- En `app.py`, registrar legacy con prefijo visible cuando sea posible:
  - `/legacy/teams`
  - `/legacy/characters`
  - `/legacy/perks`
  - `/legacy/admin`
- Si no se puede cambiar URL todavia, mantener aliases antiguos que deleguen en los routers legacy y documentar deprecacion.

Malas practicas existentes a evitar:

- Seguir mezclando rutas canonicas nuevas con compatibilidad accidental.
- Importar modelos legacy desde servicios nuevos de dominio.

Criterio de salida:

- Un grep de servicios nuevos no muestra imports de `models.team.*`, `models.user.admin` ni `services.*_operations` legacy salvo adaptadores.

#### Paso 16.3 - Retirar CRUD antiguo de teams/characters

Contexto actual:

- `routes/team.py` expone CRUD `/teams` sobre `models.team.team.Team`.
- `routes/character.py` expone CRUD `/characters` sobre `models.team.character.Character`.
- `services/team_operations.py` inyecta characters en teams manualmente.
- `services/character_operations.py` busca perks por ID y actualiza rosters antiguos.
- El modelo moderno de usuario vive en `models/user_team/team.py` y el catalogo canonico debe vivir en `models/base/roster.py` o en rulesets versionados.

Trabajo:

- Confirmar si `/teams` y `/characters` los consume el Flutter actual o solo datos antiguos.
- Crear sustitutos claros:
  - catalogo publico: `/api/v1/rulesets/{ruleset_id}/teams`.
  - equipos de usuario: `/api/v1/user-teams`.
- Migrar datos utiles de `teams`/`characters` a `base_rosters` o `user_teams` si existen en Mongo.
- Eliminar o archivar:
  - `routes/team.py`
  - `routes/character.py`
  - `services/team_operations.py`
  - `services/character_operations.py`
  - `schemas/team.py` antiguo si solo servia a `/teams`.
  - `schemas/character.py` antiguo si solo servia a `/characters`.
  - `models/team/team.py` y `models/team/character.py` cuando no haya imports vivos.

Malas practicas existentes a evitar:

- Tener dos conceptos llamados `Team`: plantilla legacy, equipo de usuario y equipo de liga sin nombres diferenciados.
- Mantener un CRUD antiguo que permite escribir datos fuera del flujo canonico.

Criterio de salida:

- No existe ruta publica que escriba en colecciones antiguas `teams`/`characters`.
- `UserTeam`, `BaseRoster` y `LeagueTeam` son los nombres dominantes para los tres conceptos reales.

#### Paso 16.4 - Resolver `perks` legacy sin perder catalogo de skills

Contexto actual:

- `routes/perk.py` y `services/perk_operations.py` exponen `/perks`.
- `models/team/perk.py` se usa como coleccion `perks` y tambien como skill catalog actual.
- `database/seeding.py` y scripts antiguos siembran `Perk` desde `config/skills.json`.

Trabajo:

- Decidir si `Perk` se renombra conceptualmente a `Skill` en API nueva.
- Crear respuesta canonica desde ruleset: `/api/v1/rulesets/{ruleset_id}/skills`.
- Mantener `/perks` solo como alias temporal que lee el mismo catalogo, no como fuente separada.
- Cuando React ya use `/skills`, eliminar:
  - `routes/perk.py` o moverlo a `routes/legacy/perk.py`.
  - `services/perk_operations.py`.
  - `schemas/perk.py` si queda sin uso.
- Mantener o migrar la coleccion DB segun decision:
  - opcion conservadora: coleccion `perks` queda como storage legacy con `catalog_id`.
  - opcion limpia: migrar a `skills` versionado por `ruleset_id`.

Malas practicas existentes a evitar:

- Borrar `Perk` antes de que star players, rosters y equipos de usuario resuelvan skills por catalogo nuevo.
- Mantener nombres `perk` en contratos nuevos si el dominio real habla de skills.

Criterio de salida:

- Hay una unica fuente de verdad de skills por ruleset y `/perks` no introduce divergencia.

#### Paso 16.5 - Unificar o eliminar admin paralelo

Contexto actual:

- `routes/admin.py` tiene login/signup propios.
- `models/user/admin.py` y `auth/admin.py` representan un sistema separado del usuario moderno.
- `admin_signup` usa hashing directo y `user_operations.add_admin`, fuera del flujo `AuthService`.

Trabajo:

- Decidir si habra rol `admin` dentro de `User` o si se elimina admin global.
- Si se mantiene:
  - anadir `roles` o `is_admin` al modelo `User`.
  - mover login a `/auth/login` comun.
  - proteger rutas admin con policy/permission service.
- Si no se mantiene:
  - exportar o borrar coleccion `admins`.
  - retirar `routes/admin.py`, `models/user/admin.py`, `auth/admin.py` y `get_admin_database()`.

Malas practicas existentes a evitar:

- Dos sistemas de autenticacion con tokens y hashes distintos.
- Endpoints admin sin relacion clara con owner/comisario de liga.

Criterio de salida:

- Solo hay una identidad autenticada en el backend: `User` con permisos/roles explicitos.

#### Paso 16.6 - Eliminar modelos muertos de matches/tournaments antiguos

Contexto actual:

- `models/match.py` define un `Match` Beanie separado de `models/league/league.py`.
- `models/tournament.py` define `Torunament` con typo en el nombre y no aparece registrado en `models/__init__.py`.
- La logica viva de partidos esta en `models/league/league.py` y `services/league_service.py`.

Trabajo:

- Confirmar por grep/imports y por colecciones Mongo si `matches` o `tournaments` antiguos tienen uso/datos.
- Si no hay uso:
  - borrar `models/match.py`.
  - borrar `models/tournament.py`.
  - borrar dependencias antiguas asociadas si existieran.
- Si hay datos historicos:
  - crear script de migracion a `league_matches` o archivo de export.
  - borrar modelos despues de migrar.

Malas practicas existentes a evitar:

- Tener dos clases `Match` en dominios distintos sin prefijo ni contexto.
- Mantener un modelo con typo (`Torunament`) porque nadie sabe si se usa.

Criterio de salida:

- Solo existe un modelo de partido activo por dominio: league match actual o `league_matches` futuro.

#### Paso 16.7 - Archivar scripts one-shot y seeders duplicados

Contexto actual:

- `database/seeding.py` es el seeder vivo de arranque.
- `scripts/seed_database.py` y `scripts/seed_base_rosters.py` duplican conversiones antiguas.
- `scripts/fix_types.py`, `scripts/migrate_base_types.py`, `_debug_images.py`, `scrap_logos.py` y `scrape_star_player_images.py` parecen herramientas puntuales.
- `scripts/audit_user_team_sizes.py` esta sin trackear en el worktree actual; no tocarlo sin confirmar.

Trabajo:

- Clasificar scripts en:
  - necesarios en CI (`validate_catalog.py`, migraciones activas).
  - herramientas manuales documentadas.
  - one-shot ya ejecutados.
- Mover herramientas manuales a `tools/` o `scripts/manual/` con README corto.
- Borrar one-shot reemplazados por catalog loader.
- Reemplazar `scripts/seed_database.py` y `scripts/seed_base_rosters.py` por comandos nuevos:
  - `scripts/validate_catalog.py`
  - `scripts/seed_catalog.py --ruleset bb2020`

Malas practicas existentes a evitar:

- Scripts que modifican JSON productivo (`fix_types.py`) sin dry-run, tests ni backup.
- Dos seeders distintos con reglas divergentes.

Criterio de salida:

- Cada script restante tiene owner, README/comando de uso y no duplica reglas del catalogo.

#### Paso 16.8 - Retirar colecciones residuales y campos legacy

Contexto actual:

- README marca `base_teams` y `perk_families` como colecciones residuales candidatas a borrar.
- `config/base_teams.json` todavia se usa para seed y para resolver hatred keywords en `BaseRosterService`.
- Datos legacy pueden seguir referenciando IDs antiguos.

Trabajo:

- Crear auditoria Mongo antes de borrar colecciones:
  - conteo documentos.
  - ultimos `updated_at` si existe.
  - referencias desde user teams/leagues.
- Migrar datos necesarios a catalogos versionados.
- Eliminar lecturas runtime desde `config/base_teams.json` antes de borrar el fichero o reducirlo.
- Borrar colecciones solo despues de backup y script reversible.

Malas practicas existentes a evitar:

- Borrar coleccion residual sin backup.
- Dejar ficheros JSON viejos como fuente oculta de verdad tras introducir rulesets.

Criterio de salida:

- No hay colecciones residuales necesarias para arranque normal.
- La app puede reconstruir catalogos desde `catalog/rulesets/<ruleset_id>/`.

#### Paso 16.9 - Gate final de limpieza

Trabajo:

- Ejecutar busquedas antes del merge final:
  - imports de `routes.team`, `routes.character`, `routes.admin`.
  - imports de `models.match`, `models.tournament`, `models.user.admin`.
  - usos de `get_team_database`, `get_character_database`, `get_admin_database`.
  - menciones de `base_teams.json` fuera de migraciones/catalog converter.
  - TODO/FIXME sin ticket.
- Ejecutar tests de compatibilidad legacy antes de borrar aliases.
- Documentar en changelog interno que rutas/colecciones se retiran y como migrar.

Malas practicas existentes a evitar:

- Declarar el backend limpio solo porque compila.
- Dejar imports muertos, modelos Beanie registrados sin uso o scripts peligrosos.

Criterio de salida:

- El repo no tiene codigo muerto conocido ni compatibilidad legacy sin fecha de retirada.
- Cualquier codigo legacy restante vive bajo `legacy/`, tiene test y tiene ticket de eliminacion.

## 8. Orden recomendado de implementacion para IA

Orden practico, con batches pequenos:

1. Documentacion baseline y tests de caracterizacion.
2. Normalizacion compartida.
3. `TeamValueCalculator`.
4. `InducementCostResolver`.
5. `InducementBudgetCalculator`.
6. `TemporaryPlayerManager`.
7. `PlayerAdvancementService`.
8. `PlayerConditionService`.
9. `SppAwardEngine`.
10. `WinningsEngine`.
11. `PostMatchPurchaseService`.
12. `AftermatchApplicationService` coordinador.
13. `MatchEventProcessor` y `MatchStateUpdater`.
14. `LeagueQueryService` con proyecciones.
15. `LeagueLifecycleService` y `FixtureGenerator`.
16. `UserTeamQueryService` y `UserTeamRosterService`.
17. `catalog/` minimo.
18. `catalog_loader/models.py`.
19. `catalog_loader/loader.py`.
20. `catalog_loader/validation.py`.
21. `catalog_loader/converters.py`.
22. `scripts/validate_catalog.py`.
23. Seeder desde catalogo.
24. `ruleset_id` en catalogos DB.
25. `ruleset_id` en liga/equipo/match.
26. Endpoints `/rulesets`.
27. `/api/v1` limpio para React.
28. Limpieza de codigo legacy y muerto con gate final.

## 9. Tests minimos por area

### 9.1 Catalog loader

- Carga manifest valido.
- Falla si falta modulo requerido.
- Falla si `ruleset_id` interno no coincide.
- Falla por JSON invalido con path claro.
- Falla por skill inexistente en roster.
- Falla por table inexistente en inducement.
- Falla por legacy ID duplicado.
- Warning por locale faltante.

### 9.2 Team value

- Ignora muertos.
- CTV excluye no disponibles.
- Low Cost Linemen se excluye cuando toca.
- Staff suma costes desde reglas.
- Temporales del match se excluyen del CTV de inducements.

### 9.3 Inducements

- Empate CTV no permite gasto.
- Favorito gasta treasury.
- Underdog recibe diferencia.
- Underdog recibe gasto del favorito.
- Underdog solo puede anadir limite configurado.
- Cost option por roster.
- Cost option por special rule.
- Compra desconocida falla o warning segun contrato, no se ignora silenciosamente.

### 9.4 Temporales

- Journeyman solo lineman.
- Journeyman no supera 11 elegibles salvo Riotous Rookies.
- Riotous Rookies requiere Low Cost Linemen.
- Mercenary cuesta base + surcharge.
- Star temporal no se mantiene.
- Journeyman keep cobra treasury y quita loner temporal si base no lo tenia.
- Legacy live charge se compensa.

### 9.5 Advancements

- No avanzar muertos.
- Star Player no avanza.
- SPP insuficiente falla.
- Random primary valida dados y categoria.
- Skill duplicada falla.
- Trait no se compra como skill.
- Characteristic valida D8 y max por stat.

### 9.6 Aftermatch

- MVP obligatorio.
- MVP no puede ser star.
- SPP por touchdown/casualty/completion/interception/MVP.
- Casualty accidental no da SPP.
- Self-inflicted no da SPP ni puntos de baja.
- Throw teammate landed/superb.
- Injury con lasting requiere D6.
- Winnings con stalling/no stalling.
- Expensive mistakes cada efecto.
- Dedicated fans win/loss/draw.
- Compras postmatch staff/jugador/apothecary.
- Masters of Undeath free lineman.
- Partial submissions por lado.
- Commissioner completa lado pendiente.
- Idempotencia final.

### 9.7 League/match

- Owner/comisario/participante permissions.
- Round robin determinista.
- Crear/editar/borrar fixture solo scheduled.
- Add/delete touchdown actualiza score.
- Update state pre-match only antes de start.
- Sent off se limpia tras aftermatch/complete.

## 10. Inventario de codigo legacy, muerto y residual

Este inventario debe revisarse durante la Fase 16. No significa borrar todo inmediatamente; significa que nada de esta lista debe quedar en el backend final sin justificacion, test y fecha de retirada.

| Candidato                                            | Estado probable                             | Sustituto objetivo                                                                 | Condicion para eliminar                                                  |
| ---------------------------------------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `routes/team.py`                                     | Legacy CRUD de equipos antiguos             | `/api/v1/rulesets/{ruleset_id}/teams` y `/api/v1/user-teams`                       | Flutter/Postman no lo usan o existe alias documentado                    |
| `routes/character.py`                                | Legacy CRUD de jugadores antiguos           | Jugadores embebidos en`UserTeam` y posiciones en `BaseRoster`                      | Datos antiguos migrados o exportados                                     |
| `services/team_operations.py`                        | Legacy service procedural                   | `UserTeamRosterService`, `CatalogService`                                          | No quedan imports fuera de`legacy/`                                      |
| `services/character_operations.py`                   | Legacy service procedural                   | `UserTeamRosterService`, `PlayerConditionService`, catalog skills                  | No quedan rutas antiguas que lo llamen                                   |
| `schemas/team.py` legacy                             | Contratos viejos para`/teams`               | Schemas versionados`api/v1`                                                        | Rutas`/teams` retiradas o movidas a legacy                               |
| `schemas/character.py` legacy                        | Contratos viejos para`/characters`          | Schemas de user team/player                                                        | Rutas`/characters` retiradas o movidas a legacy                          |
| `models/team/team.py`                                | Modelo Beanie antiguo`teams`                | `BaseRoster`, `UserTeam`, `LeagueTeam`                                             | Coleccion`teams` migrada o confirmada vacia                              |
| `models/team/character.py`                           | Modelo Beanie antiguo`characters`           | `BasePlayer`/`UserPlayer`                                                          | Coleccion`characters` migrada o confirmada vacia                         |
| `routes/perk.py`                                     | Nombre legacy para skills                   | `/api/v1/rulesets/{ruleset_id}/skills`                                             | React y backend nuevo no consumen`/perks`                                |
| `services/perk_operations.py`                        | Wrapper fino legacy                         | `RulesetCatalogService` o `SkillCatalogService`                                    | `/perks` es alias o esta eliminado                                       |
| `models/team/perk.py`                                | Catalogo actual de skills con nombre legacy | `Skill` versionado por `ruleset_id`                                                | Star players, rosters y user teams resuelven skills desde catalogo nuevo |
| `routes/admin.py`                                    | Auth/admin paralelo                         | `User` con roles/permisos                                                          | Admin global unificado o eliminado                                       |
| `models/user/admin.py`                               | Identidad separada                          | `User.roles` o `User.is_admin`                                                     | Coleccion`admins` migrada o descartada                                   |
| `auth/admin.py`                                      | Auth legacy separada                        | `AuthService` comun                                                                | No hay login admin paralelo                                              |
| `database/database_dependencies.py` providers legacy | Acopla DB a colecciones antiguas            | Repositorios finos                                                                 | No quedan rutas legacy dependientes                                      |
| `models/match.py`                                    | Probable modelo muerto de partido antiguo   | `models/league/league.py` o futura `league_matches`                                | No hay datos utiles en`matches` antiguo o estan migrados                 |
| `models/tournament.py`                               | Probable modelo muerto, typo`Torunament`    | `League`                                                                           | No hay datos utiles en`tournaments` o estan migrados                     |
| `scripts/seed_database.py`                           | Seeder duplicado                            | `scripts/seed_catalog.py`                                                          | Catalog loader cubre seed completo                                       |
| `scripts/seed_base_rosters.py`                       | Seeder duplicado parcial                    | `scripts/seed_catalog.py`                                                          | `base_rosters` sale del catalogo versionado                              |
| `scripts/fix_types.py`                               | One-shot que modifica JSON                  | Migracion validada/dry-run                                                         | Ya no se modifica`config/base_teams.json`                                |
| `scripts/migrate_base_types.py`                      | One-shot de migracion                       | Migraciones versionadas                                                            | Migracion ejecutada o sustituida                                         |
| `scripts/_debug_images.py`                           | Herramienta manual/debug                    | `tools/` documentado o borrar                                                      | No forma parte de flujo activo                                           |
| `scripts/scrap_logos.py`                             | Herramienta manual, typo incluido           | `tools/assets/` documentado o borrar                                               | Assets ya gestionados fuera del backend                                  |
| `scripts/scrape_star_player_images.py`               | Herramienta manual de assets                | Pipeline/documentacion de assets                                                   | Assets ya gestionados fuera del backend                                  |
| `config/base_teams.json`                             | Fuente legacy todavia usada                 | `catalog/rulesets/<ruleset_id>/teams.json`                                         | `BaseRosterService` y seed ya no lo leen en runtime                      |
| `config/skills.json`                                 | Fuente actual no versionada                 | `catalog/rulesets/<ruleset_id>/skills.json`                                        | Seeder y endpoints consumen ruleset catalog                              |
| `config/star_players.json`                           | Fuente actual no versionada                 | `catalog/rulesets/<ruleset_id>/star_players.json` o `teams/documents` segun diseno | Star players tienen`ruleset_id`                                          |
| Coleccion`base_teams`                                | Residual segun README                       | Ninguna o`base_rosters`/catalogo                                                   | Backup + conteo + sin referencias                                        |
| Coleccion`perk_families`                             | Residual segun README                       | `skill_families` versionado                                                        | Backup + conteo + sin referencias                                        |
| Colecciones`matches`/`tournaments` antiguas          | Probablemente residuales                    | `leagues`, `league_matches`, `match_events`                                        | Historico migrado/exportado                                              |

Regla de limpieza:

- Borrar codigo solo cuando exista sustituto probado o confirmacion de no uso.
- Si queda compatibilidad, moverla bajo `legacy/` y cubrirla con tests minimos.
- Ningun modulo nuevo debe importar modelos o servicios legacy directamente.
- Los scripts que modifican datos deben tener dry-run, backup y README; si no, se borran o se archivan fuera del flujo normal.

## 11. Dudas abiertas para Francho

Estas dudas no bloquean la redaccion del plan, pero si conviene resolverlas antes de implementar fases grandes:

1. Backend nuevo/refactor: quieres conservar FastAPI + Beanie + MongoDB, o estas abierto a cambiar persistencia/framework? RESPUESTA: el stack de backen está bien como está.
2. Endpoints legacy `/teams`, `/characters`, `/perks` y `/admin`: se usan todavia o podemos marcarlos como compatibilidad temporal? RESPUESTA: todo lo que sea legacy deberá desaparecer
3. Datos existentes en Mongo: hay que migrarlos obligatoriamente o se puede empezar con una DB nueva para el backend rehecho? RESPUESTA: se puede crear y se debe crear una nueva base de datos.
4. Rulesets: `bb2020` sera el default inicial seguro, pero quieres preparar `bb2025` desde el principio o dejar solo estructura? RESPUESTA: el default será el ruleset de 2025
5. Texto de reglas: prefieres que el catalogo inicial conserve los textos actuales curados, o que se reduzcan a summaries propios mas cortos? RESPUESTA: los textos no se deben modificar un ápice, es verdad universal
6. Matches: quieres preservar historico exacto de ligas/partidos actuales, incluidos eventos libres, o podemos normalizarlos en migracion? RESPUESTA: me da igual.
7. React: quieres que la nueva API sea `/api/v1` limpia aunque Flutter quede en rutas legacy? RESPUESTA: como quieras, no tengo preferencia
8. Autenticacion web: bearer tokens como ahora o cookies httpOnly para React? RESPUESTA: creo que mejor utilizar token, quiero que los usuarios puedan gestionar sus cuentas de forma segura

## 12. Criterios globales de aceptacion

La refactorizacion backend se considerara lista para construir el frontend React cuando:

- `database/seeding.py` sea orquestador pequeno y no contenga tablas largas de reglas.
- Exista `catalog/rulesets/bb2020` validable sin Mongo.
- `scripts/validate_catalog.py --ruleset bb2020` funcione.
- Los catalogos tengan `ruleset_id`.
- Ligas/equipos/partidos guarden o resuelvan `ruleset_id`.
- Existan endpoints `/rulesets` para discovery.
- Endpoints legacy sigan funcionando con default ruleset.
- `LeagueService` y `UserTeamService` hayan bajado de tamano y deleguen en servicios/calculadoras.
- No haya costes/reglas principales hardcodeadas fuera del catalogo o ruleset config.
- Tests cubran rulesets, inducements, aftermatch, team value, advancements y permisos.
- React pueda consumir una API versionada sin leer assets locales de reglas.
- Codigo legacy restante, si existe, vive bajo `legacy/`, tiene test y tiene fecha de retirada.
- No hay modelos/scripts/colecciones residuales conocidos sin decision documentada.

## 13. Riesgos principales y mitigacion

### Riesgo 1 - Romper comportamiento existente por refactor grande

Mitigacion:

- Tests de caracterizacion antes de tocar.
- Extraer sin cambiar comportamiento.
- Un batch por responsabilidad.

### Riesgo 2 - Perder compatibilidad con datos existentes

Mitigacion:

- Mantener legacy IDs.
- Introducir `catalog_id` antes de cambiar `_id`.
- Crear scripts de migracion.

### Riesgo 3 - Duplicar fuente de verdad frontend/backend

Mitigacion:

- Backend canonico.
- Front React consume `/rulesets`.
- Assets frontend solo fallback temporal si se decide.

### Riesgo 4 - Texto de reglas protegido

Mitigacion:

- Separar `rules_logic` de `rules_text`.
- Usar summaries propios o texto aportado por usuario.
- No generar texto oficial exacto con IA.

### Riesgo 5 - Documentos Mongo demasiado grandes

Mitigacion:

- Proyecciones inmediatas.
- ADR para separar matches/events cuando el dominio ya este aislado.

### Riesgo 6 - IA sin contexto suficiente en archivos gigantes

Mitigacion:

- Reducir servicios por fases.
- Documentar ownership por modulo.
- Mantener pasos pequenos con tests concretos.

## 14. Primeros 10 tickets recomendados

1. Crear inventario API actual en docs.
2. Anadir tests de caracterizacion de inducement budget.
3. Anadir tests de caracterizacion de aftermatch MVP/SPP/star players.
4. Crear `utils/normalization.py` y tests.
5. Reemplazar normalizacion duplicada en `StarPlayerService`.
6. Reemplazar normalizacion duplicada en `UserTeamService`.
7. Extraer `TeamValueCalculator` sin cambiar comportamiento.
8. Extraer `InducementCostResolver`.
9. Extraer `InducementBudgetCalculator` usando todavia modelos actuales.
10. Crear `catalog/rulesets/bb2020` minimo y loader read-only.

Estos tickets son suficientemente pequenos para trabajarlos con IA sin cargar todo el backend cada vez.
