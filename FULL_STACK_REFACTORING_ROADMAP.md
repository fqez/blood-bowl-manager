# Roadmap full-stack de refactorizacion: backend primero, React despues

Este documento convierte los planes grandes de backend y frontend en una ruta de ejecucion ordenada. La idea es evitar dos errores caros:

- empezar React demasiado pronto y copiar contratos legacy del backend actual;
- refactorizar backend sin pensar en los contratos limpios que necesitara React.

Documentos fuente:

- `BACKEND_REFACTORING_PLAN.md`
- `../blood-bowl-manager-front/FRONTEND_REFACTORING_PLAN.md`
- `README_RULESETS_MIGRATION_PLAN.md`

## 1. Decision principal

Recomendacion: empezar por backend.

Motivo:

- React depende de contratos API limpios.
- El backend actual mezcla reglas, datos legacy, endpoints antiguos y payloads accidentales.
- Si React se implementa completo ahora, copiara `/perks`, assets locales de reglas, `detail` stringly typed, rutas sin versionado y shapes pensados para Flutter.
- Despues habria que rehacer parte del React cuando lleguen `/rulesets`, `ruleset_id` y `/api/v1`.

Pero no hay que esperar al 100% del backend para tocar frontend. Lo correcto es:

1. Backend primero para estabilizar reglas y contratos.
2. Skeleton React temprano, sin migrar features grandes.
3. Backend hasta `/rulesets` y `/api/v1`.
4. React feature por feature usando esos contratos.
5. Limpieza final de legacy, datos muertos y Flutter.

## 2. Principio de trabajo con IA

Cada chat independiente debe ser pequeno. No pasar los documentos completos salvo tareas de planificacion.

Plantilla base para cualquier ticket:

```text
Trabaja solo en: <documento>, Fase X, Paso Y.
Objetivo: <resultado concreto>.
Codigo actual a leer: <2-5 archivos maximo>.
Usa ese codigo como contrato de comportamiento, no como plantilla de diseno.
No copies god services, god screens, duplicaciones, hardcodes, legacy o contratos accidentales.
Malas practicas a evitar: <copiar del paso>.
Criterio de salida: <copiar del paso>.
Validacion: <tests/comandos concretos>.
No avances a otros pasos.
```

Reglas:

- Backend: extraer comportamiento cubierto por tests antes de cambiar arquitectura.
- Frontend: no traducir Flutter a React linea por linea.
- No abrir tickets que toquen backend y frontend a la vez salvo que el contrato ya este definido.
- Todo paso debe terminar con validacion o con bloqueo documentado.
- Francho arranca servidores persistentes manualmente; no pedir a IA que levante dev servers salvo indicacion expresa.

## 3. Vista global de fases

| Orden | Bloque                      | Repo     | Resultado                                                        |
| ----- | --------------------------- | -------- | ---------------------------------------------------------------- |
| 0     | Preparacion comun           | ambos    | Documentos e inventarios listos                                  |
| 1     | Backend baseline            | backend  | Tests de caracterizacion e inventario API                        |
| 2     | Backend extraccion temprana | backend  | Normalizacion, team value, inducements, temporales               |
| 3     | React skeleton ligero       | frontend | Vite/React/TS, shell, design tokens, auth base con mocks         |
| 4     | Backend rulesets y API v1   | backend  | Catalog loader, `ruleset_id`, `/rulesets`, `/api/v1`             |
| 5     | React migracion real        | frontend | Teams, leagues, matches, aftermatch, wiki, tactics               |
| 6     | Limpieza legacy             | ambos    | Endpoints, assets, scripts, debug y Flutter retirados o aislados |
| 7     | Endurecimiento final        | ambos    | Tests, docs, deploy, smoke y checklist de aceptacion             |

## 4. Bloque 0 - Preparacion comun

Objetivo: dejar claro que se va a construir, que se preserva y como se valida.

### Paso 0.1 - Congelar documentos maestros

Repo: backend y frontend.

Trabajo:

- Revisar que existan:
  - `BACKEND_REFACTORING_PLAN.md`
  - `../blood-bowl-manager-front/FRONTEND_REFACTORING_PLAN.md`
  - este roadmap.
- Confirmar que cada documento tiene:
  - regla de usar codigo actual como contrato de comportamiento;
  - contexto actual a leer por area;
  - fases pequenas;
  - limpieza legacy/muerto;
  - criterios globales.

Criterio de salida:

- Los tres documentos son la fuente de verdad del trabajo.

Validacion:

- Markdown sin caracteres raros ni trailing whitespace.

### Paso 0.2 - Decidir estrategia de ramas y commits

Repo: ambos.

Trabajo:

- Decidir si se trabaja en `main` o ramas por batch.
- Recomendacion: ramas pequenas por bloque o por grupo de tickets.
- No mezclar backend y frontend en el mismo commit salvo contrato compartido.

Criterio de salida:

- Hay politica clara de commits y PRs.

### Paso 0.3 - Crear carpeta de tickets pequenos

Repo: backend primero.

Trabajo:

- Crear, cuando se empiece implementacion, una estructura tipo:

```text
docs/refactor/tickets/
  001-backend-api-inventory.md
  002-backend-characterization-inducements.md
  003-backend-normalization.md
  ...
```

- Cada ticket debe tener maximo 80-150 lineas.
- Cada ticket debe copiar solo el contexto necesario desde los planes grandes.

Criterio de salida:

- La IA puede trabajar sin leer el plan entero.

## 5. Bloque 1 - Backend baseline

Objetivo: congelar comportamiento antes de extraer logica.

Documento base: `BACKEND_REFACTORING_PLAN.md`, Fase 0.

### Paso 1.1 - Inventario API actual

Trabajo:

- Crear `docs/backend/current-api-inventory.md`.
- Listar routers actuales:
  - auth;
  - admin;
  - base-rosters;
  - star-players;
  - rules;
  - perks;
  - characters;
  - teams;
  - user-teams;
  - leagues;
  - quick-matches;
  - tactics.
- Marcar cada endpoint como:
  - publico;
  - protegido;
  - legacy;
  - candidato `/api/v1`;
  - candidato a borrar.

Codigo actual a leer:

- `app.py`
- `routes/*.py`
- `schemas/*.py`

Criterio de salida:

- React sabe que endpoints existen hoy y cuales no debe copiar como contrato futuro.

### Paso 1.2 - Comandos de validacion backend

Trabajo:

- Crear `docs/backend/development.md`.
- Documentar:
  - Python de backend: `C:\Users\Franchoped\Software\bbman\Scripts\python.exe`.
  - `python -m compileall .`
  - `python -m pytest`
  - tests enfocados.
  - no arrancar servidores persistentes salvo peticion expresa.

Criterio de salida:

- Cualquier chat futuro sabe validar backend.

### Paso 1.3 - Tests de caracterizacion criticos

Trabajo:

- Anadir tests antes de cambiar implementacion para:
  - inducement budget favorito/underdog/empate;
  - reserved treasury;
  - share code sin notas privadas;
  - star player availability;
  - SPP no aplicado a star players;
  - MVP requerido y prohibido a star players;
  - expensive mistakes;
  - Masters of Undeath;
  - quick match no acepta equipos en liga si aplica.

Codigo actual a leer:

- `services/user_team_service.py`
- `services/league_service.py`
- `models/user_team/team.py`
- tests existentes relacionados.

Criterio de salida:

- Se puede refactorizar sin romper comportamiento oculto.

Gate para avanzar:

- Tests existentes siguen pasando.
- Tests nuevos capturan flujos de riesgo.

## 6. Bloque 2 - Backend extraccion temprana

Objetivo: reducir los acoplamientos que mas contaminan contratos futuros.

Documento base: `BACKEND_REFACTORING_PLAN.md`, Fases 1 a 8.

### Paso 2.1 - Normalizacion e IDs compartidos

Trabajo:

- Crear modulo de normalizacion compartido.
- Extraer slugify, aliases, canonical skill IDs y keywords.
- Sustituir duplicacion de forma incremental.

Codigo actual a leer:

- `database/seeding.py`
- `services/user_team_service.py`
- `services/base_roster_service.py`
- `services/star_player_service.py`
- `utils/team_special_rules.py`

Criterio de salida:

- Hay una unica forma de normalizar skill IDs, team IDs y rule keywords.

### Paso 2.2 - Team value limpio

Trabajo:

- Extraer `TeamValueCalculator`.
- Mantener compatibilidad con `UserTeam.calculate_team_value_breakdown()` temporalmente.
- Cubrir CTV, TV, staff, muertos, lesionados y temporales.

Codigo actual a leer:

- `models/user_team/team.py`
- `services/user_team_service.py`
- `tests/test_team_value.py`

Criterio de salida:

- Reglas versionables salen del modelo Beanie.

### Paso 2.3 - Inducements y temporales

Trabajo:

- Extraer:
  - `InducementCostResolver`;
  - `InducementBudgetCalculator`;
  - `TemporaryPlayerManager`.
- Usar reglas existentes como comportamiento, no como diseno.
- Eliminar hardcodes como limite fijo si existe regla configurada.

Codigo actual a leer:

- `models/base/inducement.py`
- `services/user_team_service.py`
- `services/league_service.py`
- `tests/test_temporary_player_finalization.py`

Criterio de salida:

- Pre-match React podra depender de match state backend-owned, no de calculos locales.

### Paso 2.4 - Avances, lesiones, SPP y aftermatch base

Trabajo:

- Extraer motores/servicios pequenos para:
  - advancement;
  - injuries;
  - SPP awards;
  - winnings;
  - postmatch purchases.
- Mantener metodos publicos actuales delegando.

Codigo actual a leer:

- `services/user_team_service.py`
- `services/league_service.py`
- `models/base/advancement.py`
- `models/base/injury.py`
- `models/base/spp.py`

Criterio de salida:

- Aftermatch deja de depender de un metodo gigante como unica fuente de verdad.

### Paso 2.5 - Reducir god services sin cambiar API

Trabajo:

- Reducir `LeagueService` y `UserTeamService` por delegacion.
- No cambiar endpoints todavia salvo que el paso lo exija.
- Crear servicios de dominio/aplicacion pequenos.

Criterio de salida:

- Las rutas actuales siguen funcionando, pero la logica ya esta separada.

Gate para avanzar:

- Tests de caracterizacion siguen pasando.
- No se han creado nuevos god files.
- React todavia no debe migrar features grandes.

## 7. Bloque 3 - Skeleton React temprano

Objetivo: avanzar estructura frontend sin contaminarla con API legacy.

Documento base: `../blood-bowl-manager-front/FRONTEND_REFACTORING_PLAN.md`, Fases 0 a 3.

Importante: este bloque puede hacerse en paralelo despues de que backend tenga baseline y tests, pero no debe implementar features grandes todavia.

### Paso 3.1 - Inventario frontend

Trabajo:

- Crear en front:
  - `docs/frontend/current-route-inventory.md`;
  - `docs/frontend/current-api-usage.md`.
- Extraer rutas desde `app_router.dart`.
- Extraer endpoints desde repositorios Flutter.
- Marcar debug, legacy y futuros `/api/v1`.

Codigo actual a leer:

- `lib/core/router/app_router.dart`
- `lib/features/shared/data/team_repository.dart`
- `lib/features/shared/data/league_repository.dart`
- `lib/features/shared/data/quick_match_repository.dart`
- `lib/features/auth/data/repositories/auth_repository.dart`

Criterio de salida:

- React sabe que debe preservar, pero no copia shapes legacy sin decision.

### Paso 3.2 - Decision de stack React

Trabajo:

- Confirmar:
  - Vite + React + TypeScript;
  - React Router o TanStack Router;
  - TanStack Query;
  - React Hook Form + Zod;
  - Vitest + Testing Library;
  - MSW;
  - Playwright;
  - CSS strategy.

Criterio de salida:

- `docs/frontend/react-stack-decision.md` existe.

### Paso 3.3 - Crear skeleton React

Trabajo:

- Crear proyecto en carpeta acordada, por ejemplo `react/` dentro del repo front.
- Configurar:
  - TypeScript estricto;
  - lint;
  - format;
  - test;
  - build;
  - env validation;
  - QueryClient;
  - router;
  - theme provider.

Malas practicas a evitar:

- Mezclar React dentro de `lib/` Flutter.
- Implementar teams/leagues/matches antes de API estable.

Criterio de salida:

- App React vacia construye y testea.

### Paso 3.4 - Design tokens, shell y auth base con mocks

Trabajo:

- Migrar tokens visuales, no pantallas.
- Crear shell responsive con rutas placeholder.
- Crear auth flow contra MSW mocks y wrapper HTTP.

Codigo actual a leer:

- `lib/core/theme/*`
- `lib/core/shell/*`
- `lib/core/network/api_client.dart`
- `lib/features/auth/*`

Criterio de salida:

- React tiene estructura profesional lista, pero sin depender de endpoints legacy de dominio.

Gate para avanzar:

- React build/typecheck/lint/test OK.
- No hay features grandes migradas aun.

## 8. Bloque 4 - Backend rulesets y API v1

Objetivo: crear el contrato limpio que React consumira.

Documento base: `BACKEND_REFACTORING_PLAN.md`, Fases 9 a 15.

### Paso 4.1 - Catalog loader versionado

Trabajo:

- Crear `catalog/rulesets/bb2020` minimo.
- Crear modelos Pydantic del loader.
- Crear loader read-only.
- Crear validacion cruzada.
- Crear converters hacia modelos DB actuales.

Codigo actual a leer:

- `README_RULESETS_MIGRATION_PLAN.md`
- `database/seeding.py`
- `config/skills.json`
- `config/base_teams.json`
- `config/star_players.json`
- `models/base/*.py`

Criterio de salida:

- Catalogo validable sin Mongo.

### Paso 4.2 - Seeder desde catalogo

Trabajo:

- Convertir `database/seeding.py` en orquestador pequeno.
- Crear `scripts/validate_catalog.py`.
- Crear `scripts/seed_catalog.py --ruleset bb2020`.
- Mantener fallback legacy solo con flag y warning claro si se decide.

Criterio de salida:

- Backend ya no depende de reglas largas hardcodeadas en seeder.

### Paso 4.3 - Introducir `ruleset_id`

Trabajo:

- Agregar `ruleset_id` a catalogos DB.
- Resolver `ruleset_id` en teams, leagues y matches.
- Mantener default para datos existentes.

Criterio de salida:

- Cada flujo sabe con que ruleset opera.

### Paso 4.4 - Endpoints `/rulesets`

Trabajo:

- Crear endpoints:
  - `GET /rulesets`;
  - `GET /rulesets/{ruleset_id}`;
  - `GET /rulesets/{ruleset_id}/catalogue`;
  - `GET /rulesets/{ruleset_id}/teams`;
  - `GET /rulesets/{ruleset_id}/skills`;
  - `GET /rulesets/{ruleset_id}/inducements`;
  - `GET /rulesets/{ruleset_id}/advancement`;
  - `GET /rulesets/{ruleset_id}/tables`.

Criterio de salida:

- React puede descubrir catalogos sin assets locales de reglas.

### Paso 4.5 - `/api/v1` limpio para React

Trabajo:

- Definir contratos para:
  - auth/session;
  - rulesets/catalog;
  - teams;
  - leagues;
  - matches;
  - aftermatch;
  - tactics.
- Mantener endpoints actuales como compatibility layer.
- Generar o revisar OpenAPI.

Criterio de salida:

- React ya puede empezar migracion real sin copiar rutas legacy.

Gate para avanzar:

- `/rulesets` funciona.
- Contratos `/api/v1` existen o estan suficientemente definidos.
- Endpoints legacy siguen si Flutter los necesita.

## 9. Bloque 5 - React migracion real

Objetivo: migrar features sobre contratos limpios.

Documento base: `../blood-bowl-manager-front/FRONTEND_REFACTORING_PLAN.md`, Fases 4 a 11.

### Paso 5.1 - Tipos, schemas y API modules

Trabajo:

- Crear tipos/schemas para:
  - User;
  - Ruleset;
  - Team;
  - Player;
  - League;
  - Match;
  - MatchEvent;
  - AftermatchReport.
- Usar OpenAPI si backend lo permite; si no, Zod temporal.
- Crear query keys y API modules.

Criterio de salida:

- Ningun componente React llama fetch/axios directamente.

### Paso 5.2 - Teams y team creator

Trabajo:

- Migrar:
  - teams list;
  - team detail;
  - shared team;
  - team creator wizard;
  - player card basico.

Codigo Flutter a leer:

- `my_teams_screen.dart`
- `my_team_detail_screen.dart`
- `team_creator_screen.dart`
- `player_card_screen.dart`
- `user_team.dart`

Criterio de salida:

- Primer flujo real React funciona end-to-end con backend.

### Paso 5.3 - Leagues

Trabajo:

- Migrar:
  - leagues list;
  - create league;
  - join league;
  - league overview tabs;
  - league backoffice.

Criterio de salida:

- Usuario puede crear/unirse/ver liga en React.

### Paso 5.4 - Matches y quick matches

Trabajo:

- Crear controlador comun de match.
- Migrar:
  - quick match setup;
  - pre-match;
  - team prep;
  - live view;
  - event add/delete;
  - complete match.

Malas practicas a evitar:

- Duplicar league match y quick match.
- Reintroducir `detail` como semantica unica si backend ya da payload estructurado.

Criterio de salida:

- Un partido basico se puede jugar en React.

### Paso 5.5 - Aftermatch

Trabajo:

- Migrar payload/hydration primero.
- Crear wizard por pasos.
- Cubrir MVP, SPP, injuries, winnings, purchases y temporales.

Criterio de salida:

- React puede enviar aftermatch completo y rehidratar report guardado.

### Paso 5.6 - Wiki/rulesets

Trabajo:

- Consumir `/rulesets`.
- Migrar wiki de skills, weather, star players, injuries, blocking, passing y tables.
- Usar assets locales solo para imagenes/fallback.

Criterio de salida:

- React no depende de `assets/rules` como fuente canonica.

### Paso 5.7 - Tacticas

Trabajo:

- Migrar modelo de tacticas.
- Migrar tablero visual.
- Crear tests de posicionamiento.

Criterio de salida:

- Tacticas funciona o queda explicitamente planificado para una version posterior.

Gate para avanzar:

- React cubre flujos principales.
- Tests unit/component importantes OK.
- Smoke desktop/mobile OK.

## 10. Bloque 6 - Limpieza legacy

Objetivo: dejar repos limpios, mantenibles y entendibles.

### Paso 6.1 - Backend legacy

Documento base: `BACKEND_REFACTORING_PLAN.md`, Fase 16.

Trabajo:

- Medir uso de:
  - `/teams`;
  - `/characters`;
  - `/perks`;
  - `/admin`.
- Mover compatibilidad a `legacy/` si hace falta.
- Retirar o migrar:
  - `routes/team.py`;
  - `routes/character.py`;
  - `services/team_operations.py`;
  - `services/character_operations.py`;
  - `models/match.py`;
  - `models/tournament.py`;
  - seeders/scripts duplicados;
  - colecciones residuales.

Criterio de salida:

- Codigo legacy restante vive bajo `legacy/`, con test y fecha de retirada.

### Paso 6.2 - Frontend legacy

Documento base: `../blood-bowl-manager-front/FRONTEND_REFACTORING_PLAN.md`, Fase 12.

Trabajo:

- Retirar o mover a dev-only:
  - `features/debug/*`;
  - rutas `/debug/*`;
  - credenciales hardcodeadas;
  - translations debug si sobran.
- Auditar y reducir:
  - `assets/rules/*`;
  - `assets/data.json`;
  - imagenes duplicadas;
  - scripts Python auxiliares;
  - `build/`;
  - `analyze_output.txt`.
- Definir retirada de Flutter:
  - archivar;
  - borrar;
  - mantener temporalmente con fecha.

Criterio de salida:

- Build React productivo no contiene debug ni reglas locales canonicas.

Gate para avanzar:

- No hay codigo muerto conocido sin decision.
- No hay dos fuentes de verdad para reglas.

## 11. Bloque 7 - Endurecimiento final

Objetivo: preparar el proyecto para evolucionar sin volver al caos.

### Paso 7.1 - Calidad backend

Trabajo:

- Ejecutar tests completos backend.
- Ejecutar compile/lint si existe.
- Revisar OpenAPI.
- Revisar docs de development/deploy.
- Revisar indices/migraciones Mongo.

Criterio de salida:

- Backend soporta React sin depender de endpoints legacy.

### Paso 7.2 - Calidad frontend

Trabajo:

- `npm run typecheck`.
- `npm run lint`.
- `npm run test`.
- `npm run build`.
- Playwright smoke desktop/mobile.
- Revisar bundle para debug/credenciales.

Criterio de salida:

- React esta listo para deploy.

### Paso 7.3 - Deploy y rollback

Trabajo:

- Confirmar Cloudflare Pages para React.
- Confirmar variables env.
- Smoke test post-deploy.
- Documentar rollback.

Criterio de salida:

- Francho puede publicar y revertir con seguridad.

## 12. Orden recomendado de ejecucion real

Esta es la secuencia concreta que recomiendo seguir:

1. Backend: inventario API actual.
2. Backend: documentar comandos de validacion.
3. Backend: tests de caracterizacion criticos.
4. Backend: normalizacion compartida.
5. Backend: team value calculator.
6. Backend: inducements y temporales.
7. Backend: avances/lesiones/SPP/aftermatch base.
8. Backend: reducir `LeagueService` y `UserTeamService` sin cambiar API.
9. Frontend: inventario rutas Flutter.
10. Frontend: inventario endpoints Flutter.
11. Frontend: decision stack React.
12. Frontend: skeleton React limpio.
13. Frontend: design tokens, shell, auth con mocks.
14. Backend: catalog loader versionado.
15. Backend: seeding desde catalogo.
16. Backend: `ruleset_id`.
17. Backend: endpoints `/rulesets`.
18. Backend: `/api/v1` limpio para React.
19. Frontend: tipos/schemas/API modules.
20. Frontend: teams list/detail.
21. Frontend: team creator.
22. Frontend: player card.
23. Frontend: leagues.
24. Frontend: match/live/quick match.
25. Frontend: aftermatch.
26. Frontend: wiki/rulesets.
27. Frontend: tactics.
28. Backend: limpieza legacy.
29. Frontend: limpieza debug/assets/Flutter.
30. Full-stack: tests, smoke, deploy y rollback.

## 13. Gates de decision

No avanzar si el gate falla.

### Gate A - Antes de extraer backend

- Inventario API existe.
- Tests de caracterizacion de riesgo existen.
- Comandos de validacion documentados.

### Gate B - Antes de skeleton React

- Backend tiene baseline de tests.
- React no empezara features grandes.
- Stack React decidido.

### Gate C - Antes de migrar features React reales

- `/rulesets` existe o contrato esta congelado.
- `/api/v1` existe o contrato esta documentado.
- Auth/session React funciona con mocks.
- API modules React centralizados.

### Gate D - Antes de retirar Flutter

- React cubre flujos principales.
- Smoke E2E pasa.
- Deploy React probado.
- Assets/reglas locales auditados.

### Gate E - Antes de borrar legacy backend

- Uso medido.
- Datos migrados/exportados.
- Backup si hay colecciones Mongo.
- Compatibilidad documentada si queda alias.

## 14. Que NO hacer

- No empezar React implementando `aftermatch` completo antes de `/api/v1`.
- No copiar pantallas Flutter gigantes a componentes React gigantes.
- No hacer una reescritura backend total sin tests de caracterizacion.
- No borrar legacy sin medir uso.
- No mantener assets/rules locales como fuente canonica despues de `/rulesets`.
- No mezclar debug credentials con produccion.
- No abrir tickets con mas de una responsabilidad grande.

## 15. Primeros 12 tickets concretos

1. `backend-001-api-inventory`: inventariar endpoints actuales.
2. `backend-002-development-commands`: documentar comandos de validacion.
3. `backend-003-characterization-inducements`: tests de inducement budget.
4. `backend-004-characterization-aftermatch`: tests de MVP/SPP/temporales.
5. `backend-005-normalization-utils`: modulo de normalizacion compartido.
6. `backend-006-team-value-calculator`: extraer team value.
7. `backend-007-inducement-cost-resolver`: extraer costes.
8. `backend-008-inducement-budget-calculator`: extraer presupuesto.
9. `backend-009-temporary-player-manager`: extraer temporales.
10. `frontend-001-route-inventory`: inventariar rutas Flutter.
11. `frontend-002-api-usage-inventory`: inventariar endpoints Flutter.
12. `frontend-003-react-stack-decision`: decidir stack React.

Despues de estos 12 tickets, el proyecto ya tendra base suficiente para avanzar con menos riesgo y menos tokens por chat.