# Prompt pack full-stack para ejecutar la refactorizacion

Este documento es para facilitar chats independientes con IA. Cada bloque es un prompt listo para copiar y pegar.

Documentos de referencia:

- `FULL_STACK_REFACTORING_ROADMAP.md`
- `BACKEND_REFACTORING_PLAN.md`
- `README_RULESETS_MIGRATION_PLAN.md`
- `../blood-bowl-manager-front/FRONTEND_REFACTORING_PLAN.md`

Mapa de repositorios:

- Backend legacy, solo como fuente de comportamiento: `c:\Users\Franchoped\Software\blood-bowl-manager`.
- Frontend Flutter legacy, solo como fuente de comportamiento: `c:\Users\Franchoped\Software\blood-bowl-manager-front`.
- Backend v2, destino de codigo/documentacion nueva backend: `c:\Users\Franchoped\Software\bb-manager-v2`.
- Frontend v2 React, destino de codigo/documentacion nueva frontend: `c:\Users\Franchoped\Software\bb-manager-v2-front`.

Decisiones cerradas por Francho:

- Backend v2 mantiene stack actual: FastAPI + Beanie + MongoDB.
- Backend v2 usa base de datos nueva; no hay obligacion de migrar historico actual.
- El codigo/endpoints legacy no se conservan como producto final; se auditan y desaparecen.
- Ruleset inicial y default: `bb2025`.
- Los textos actuales de reglas/catalogos no se modifican ni se resumen; si falta texto, no inventar ni copiar texto oficial protegido.
- Historico exacto de matches/ligas actuales no es requisito.
- API nueva limpia: usar `/api/v1` salvo motivo tecnico documentado.
- Auth web con bearer tokens/JWT como base.
- Frontend v2 en `bb-manager-v2-front`, separado de Flutter.
- Stack frontend estandar: Vite + React + TypeScript, React Router, TanStack Query, React Hook Form + Zod, Vitest/Testing Library, MSW, Playwright.
- UI frontend estandar: Tailwind CSS + shadcn/ui sobre CSS variables, salvo que el repo v2 ya decida otra cosa explicitamente.
- La capa visual del frontend actual se conserva como contrato visual: layout, fuentes, escala tipografica, colores, espaciados, ritmo visual, densidad de informacion, jerarquia, navegacion, aspecto de tarjetas/tablas/formularios/dialogos/botones, iconografia, assets e identidad visual.
- La logica del frontend NO se conserva como arquitectura: estado, data fetching, formularios, validaciones, componentes gigantes y acoplamientos se rehacen a fondo en React.
- Deploy frontend: mantener Cloudflare Pages con GitHub Actions por ahora.
- Imagenes actuales se mantienen, pero reglas/catalogos/wiki vienen siempre del backend.
- Debug tools actuales no se conservan de momento.
- Idiomas desde el inicio: ES y EN.

Regla base para todos los prompts:

- Usa el codigo actual como contrato de comportamiento, no como plantilla de diseno.
- Lee solo los documentos/secciones y archivos indicados.
- No copies god services, god screens, duplicaciones, hardcodes, legacy ni contratos accidentales.
- No avances a otros pasos.
- No arranques servidores persistentes; Francho los arranca manualmente.
- Los repos legacy (`blood-bowl-manager` y `blood-bowl-manager-front`) son SOLO LECTURA en todos los prompts, salvo los prompts 003 y 004, que permiten escribir tests de caracterizacion en `blood-bowl-manager`.
- Si escribes codigo/documentacion backend nueva, el unico destino permitido es `c:\Users\Franchoped\Software\bb-manager-v2`.
- Si escribes codigo/documentacion frontend nueva, el unico destino permitido es `c:\Users\Franchoped\Software\bb-manager-v2-front`.
- Si un prompt pide leer legacy y escribir v2, esta prohibido modificar, formatear, mover, borrar o crear archivos dentro del repo legacy.
- Si necesitas modificar un repo distinto del destino indicado, detente y pregunta antes de tocar archivos.
- Si trabajas con reglas/catalogos/wiki, la fuente canonica debe ser el backend v2; no crees fallback local frontend.
- Si trabajas con UI frontend, prepara ES/EN desde el inicio.
- Si trabajas con frontend visual, conserva el look and feel actual como contrato visual. Rehaz la implementacion, no el aspecto salvo mejora puntual justificada.
- No copies widgets Flutter ni pantallas gigantes, pero si reproduce su layout, fuentes, tamanos, colores, espaciados, componentes visuales, assets y patrones de navegacion cuando funcionen bien.
- Si cambias backend Python legacy para pruebas de caracterizacion, valida con `C:\Users\Franchoped\Software\bbman\Scripts\python.exe` desde `c:\Users\Franchoped\Software\blood-bowl-manager`.
- Si el paso solo crea documentacion, no ejecutes tests salvo que el prompt lo pida.

## Como usar estos prompts

1. Abre un chat nuevo.
2. Copia un solo prompt.
3. Deja que la IA termine ese paso.
4. Revisa diff y validacion.
5. Sigue con el siguiente prompt.

No copies todo este documento en cada chat. Copia solo el prompt del paso.

## Prompt 001 - Backend API inventory

```text
Trabaja solo en el backend.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager.

Objetivo: crear el inventario actual de API antes de refactorizar.

Referencias a leer:
- FULL_STACK_REFACTORING_ROADMAP.md, Bloque 1, Paso 1.1.
- BACKEND_REFACTORING_PLAN.md, Fase 0, Paso 0.1.

Codigo actual a leer:
- app.py
- routes/*.py
- schemas/*.py

Trabajo:
- Crear docs/backend/current-api-inventory.md.
- Listar todos los endpoints actuales con metodo, path, router, auth, request schema, response schema si existe y dominio propietario.
- Marcar cada endpoint como publico, protegido, legacy a eliminar o candidato /api/v1.
- Marcar especialmente /teams, /characters, /perks y /admin como legacy a eliminar salvo que se justifique una reimplementacion limpia en /api/v1.
- Recordar que backend v2 usara DB nueva, asi que no hay que preservar historico exacto.

Reglas:
- No cambies codigo funcional ni documentacion en el repo legacy.
- No mantengas endpoints legacy por inercia; si un comportamiento sigue siendo necesario, propon su contrato limpio en /api/v1.
- No arranques servidores.

Criterio de salida:
- Existe docs/backend/current-api-inventory.md.
- Cada endpoint tiene decision preliminar.

Validacion:
- Revisa que el Markdown no tenga trailing whitespace.
- No requiere tests.
```

## Prompt 002 - Backend development commands

```text
Trabaja solo en el backend.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager.

Objetivo: documentar comandos de validacion backend para futuros chats.

Referencias a leer:
- FULL_STACK_REFACTORING_ROADMAP.md, Bloque 1, Paso 1.2.
- BACKEND_REFACTORING_PLAN.md, Fase 0, Paso 0.2.
- .github/instructions/copilot-instructions.md si aplica.

Codigo/documentos a leer:
- requirements.txt
- README.md
- docker/docker-compose.yml
- tests/conftest.py

Trabajo:
- Crear docs/backend/development.md.
- Documentar stack objetivo backend v2: FastAPI + Beanie + MongoDB.
- Documentar que backend v2 usa una base de datos nueva.
- Documentar entorno Python: C:\Users\Franchoped\Software\bbman\Scripts\python.exe.
- Documentar comandos de compile/test enfocados.
- Documentar que Francho prefiere arrancar servidores persistentes manualmente.
- Documentar cuando reconstruir Docker tras cambios backend de codigo/config/deps.

Reglas:
- No crear virtualenv nuevo.
- No modificar codigo funcional ni documentacion en el repo legacy.
- No ejecutar builds largos salvo necesario.

Criterio de salida:
- Cualquier IA futura sabe validar backend sin preguntar.

Validacion:
- Markdown limpio en c:\Users\Franchoped\Software\bb-manager-v2-front.
- No requiere tests.
```

## Prompt 003 - Backend characterization: inducements

```text
Trabaja solo en el backend.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager.
- ESCRITURA PERMITIDA: c:\Users\Franchoped\Software\blood-bowl-manager, solo archivos de tests de caracterizacion.
- PROHIBIDO: modificar servicios, modelos, rutas, seeders o cualquier codigo productivo legacy.
- PROHIBIDO: escribir codigo backend limpio en c:\Users\Franchoped\Software\bb-manager-v2 en este prompt.

Objetivo: anadir tests de caracterizacion para inducement budget antes de refactorizar.

Referencias a leer:
- FULL_STACK_REFACTORING_ROADMAP.md, Bloque 1, Paso 1.3.
- BACKEND_REFACTORING_PLAN.md, Fase 0, Paso 0.3, y Fase 3.

Codigo actual a leer:
- services/user_team_service.py, solo funciones de inducements/petty cash/treasury.
- services/league_service.py, solo usos de inducements en match/pre-match.
- models/base/inducement.py
- models/user_team/team.py
- tests/test_team_value.py
- tests/test_temporary_player_finalization.py si aporta contexto.

Trabajo:
- Crear o ampliar tests para casos de inducement budget: empate CTV, favorito gasta treasury, underdog recibe diferencia, underdog recibe gasto del favorito, limite de top-up si aplica, temporales excluidos/incluidos segun comportamiento actual.
- Los tests deben documentar el comportamiento actual aunque sea imperfecto.

Reglas:
- No cambies implementacion salvo ajustes minimos de test setup.
- No arregles bugs todavia salvo que impidan escribir tests; si pasa, documenta bloqueo.
- Usa el codigo actual como contrato de comportamiento, no como diseno.
- Este prompt es una excepcion: aqui los tests van en el repo legacy. No escribas codigo nuevo v2.

Criterio de salida:
- Tests de inducements existen y pasan.

Validacion:
- Ejecuta tests enfocados con C:\Users\Franchoped\Software\bbman\Scripts\python.exe.
```

## Prompt 004 - Backend characterization: aftermatch

```text
Trabaja solo en el backend.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager.
- ESCRITURA PERMITIDA: c:\Users\Franchoped\Software\blood-bowl-manager, solo archivos de tests de caracterizacion.
- PROHIBIDO: modificar servicios, modelos, rutas, seeders o cualquier codigo productivo legacy.
- PROHIBIDO: escribir codigo backend limpio en c:\Users\Franchoped\Software\bb-manager-v2 en este prompt.

Objetivo: anadir tests de caracterizacion para aftermatch, MVP, SPP y temporales.

Referencias a leer:
- FULL_STACK_REFACTORING_ROADMAP.md, Bloque 1, Paso 1.3.
- BACKEND_REFACTORING_PLAN.md, Fases 4, 6 y tests minimos de aftermatch.

Codigo actual a leer:
- services/league_service.py, solo aftermatch/apply reports/SPP/winnings/temporales.
- services/user_team_service.py, solo temporales, player updates, SPP/advancement interactions.
- models/league/league.py
- models/user_team/team.py
- tests/test_temporary_player_finalization.py
- tests/test_league_commissioners.py si aplica.

Trabajo:
- Crear tests de caracterizacion para MVP obligatorio, MVP prohibido a star players, SPP por eventos principales, casualty accidental/self-inflicted si existe, temporales postmatch, compras postmatch y/o expensive mistakes si el setup lo permite.
- Mantener tests pequenos y aislados.

Reglas:
- No refactorices todavia.
- No cambies contratos de API.
- Si una regla no se puede testear sin demasiado setup, documenta el caso pendiente en el test/doc.
- Este prompt es una excepcion: aqui los tests van en el repo legacy. No escribas codigo nuevo v2.

Criterio de salida:
- Existe cobertura inicial de aftermatch antes de extraer servicios.

Validacion:
- Ejecuta tests enfocados con C:\Users\Franchoped\Software\bbman\Scripts\python.exe.
```

## Prompt 005 - Backend normalization utils

```text
Trabaja solo en el backend.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager.

Objetivo: extraer normalizacion compartida sin cambiar comportamiento.

Referencias a leer:
- FULL_STACK_REFACTORING_ROADMAP.md, Bloque 2, Paso 2.1.
- BACKEND_REFACTORING_PLAN.md, Fase 1 y tabla 7.0 Normalizacion e IDs.

Codigo actual a leer:
- database/seeding.py, solo slugify/normal keys/aliases.
- services/user_team_service.py, solo normalizacion de skills/rules.
- services/base_roster_service.py, solo normalizacion/hatred keywords.
- services/star_player_service.py, solo normalizacion/aliases.
- utils/team_special_rules.py

Trabajo:
- Crear utils/normalization.py o catalog_loader/normalization.py segun encaje.
- Mover funciones puras reutilizables.
- Anadir tests unitarios con casos reales existentes.
- Si necesitas demostrar un primer uso, hazlo solo dentro de c:\Users\Franchoped\Software\bb-manager-v2.

Reglas:
- No reescribir seeding legacy ni ningun archivo del repo legacy.
- No cambiar IDs publicos observados en legacy.
- No introducir dependencias de DB en normalizacion.
- No reemplaces usos en c:\Users\Franchoped\Software\blood-bowl-manager.

Criterio de salida:
- Hay modulo compartido testeado y listo para migraciones incrementales.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2, ejecuta tests nuevos/enfocados del modulo creado.
- No ejecutes ni modifiques tests en c:\Users\Franchoped\Software\blood-bowl-manager.
```

## Prompt 006 - Backend TeamValueCalculator

```text
Trabaja solo en el backend.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager.

Objetivo: extraer TeamValueCalculator limpio preservando comportamiento.

Referencias a leer:
- FULL_STACK_REFACTORING_ROADMAP.md, Bloque 2, Paso 2.2.
- BACKEND_REFACTORING_PLAN.md, Fase 2.

Codigo actual a leer:
- models/user_team/team.py
- services/user_team_service.py, solo team value/CTV/inducement value.
- tests/test_team_value.py

Trabajo:
- Crear servicio/calculadora de dominio para team value.
- Crear API publica equivalente en backend v2 si hace falta.
- Cubrir TV/CTV, muertos, lesionados, temporales, staff y rerolls segun tests.

Reglas:
- No meter reglas versionables nuevas en modelos Beanie.
- No tocar endpoints ni codigo en el repo legacy.
- No arreglar otros bugs.

Criterio de salida:
- Team value esta aislado en backend v2 y los tests de backend v2 pasan.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2, ejecuta los tests de team value creados o portados en backend v2.
- No ejecutes ni modifiques tests en c:\Users\Franchoped\Software\blood-bowl-manager.
```

## Prompt 007 - Backend InducementCostResolver

```text
Trabaja solo en el backend.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager.

Objetivo: extraer la resolucion de costes de inducements.

Referencias a leer:
- FULL_STACK_REFACTORING_ROADMAP.md, Bloque 2, Paso 2.3.
- BACKEND_REFACTORING_PLAN.md, Fase 3, pasos de InducementCostResolver.

Codigo actual a leer:
- models/base/inducement.py
- services/user_team_service.py, solo coste/compra de inducements.
- services/league_service.py, solo coste/compra de inducements en match.
- tests de inducements creados previamente.

Trabajo:
- Crear InducementCostResolver como logica pura.
- Cubrir cost option por roster/special rule si existe.
- Crear integracion solo dentro de backend v2 si hace falta.

Reglas:
- No mezclar presupuesto con coste.
- No hardcodear reglas nuevas.
- No cambiar payloads publicos observados en legacy.

Criterio de salida:
- Costes de inducements estan testeados y aislados en backend v2.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2, ejecuta tests enfocados de inducements en backend v2.
- No ejecutes ni modifiques tests en c:\Users\Franchoped\Software\blood-bowl-manager.
```

## Prompt 008 - Backend InducementBudgetCalculator

```text
Trabaja solo en el backend.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager.

Objetivo: extraer calculo de presupuesto de inducements.

Referencias a leer:
- FULL_STACK_REFACTORING_ROADMAP.md, Bloque 2, Paso 2.3.
- BACKEND_REFACTORING_PLAN.md, Fase 3, pasos de InducementBudgetCalculator.

Codigo actual a leer:
- models/base/inducement.py
- services/user_team_service.py, solo budget/petty cash/treasury.
- services/league_service.py, solo budget en pre-match/live.
- tests de inducement budget.

Trabajo:
- Crear InducementBudgetCalculator como logica pura.
- Usar reglas configuradas si existen, no constantes escondidas.
- Mantener compatibilidad con comportamiento actual cubierto por tests.

Reglas:
- No mutar treasury dentro del calculador.
- No mezclar compras con calculo de disponibilidad.

Criterio de salida:
- Presupuesto de inducements queda aislado y testeado en backend v2.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2, ejecuta tests enfocados en backend v2.
- No ejecutes ni modifiques tests en c:\Users\Franchoped\Software\blood-bowl-manager.
```

## Prompt 009 - Backend TemporaryPlayerManager

```text
Trabaja solo en el backend.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager.

Objetivo: extraer gestion de jugadores temporales, journeymen, mercenaries y star players temporales.

Referencias a leer:
- FULL_STACK_REFACTORING_ROADMAP.md, Bloque 2, Paso 2.3.
- BACKEND_REFACTORING_PLAN.md, Fase 3, temporales.

Codigo actual a leer:
- services/user_team_service.py, solo temporales/journeymen/star hires.
- services/league_service.py, solo finalizacion de temporales/aftermatch.
- models/user_team/team.py
- models/base/star_player.py
- tests/test_temporary_player_finalization.py

Trabajo:
- Crear TemporaryPlayerManager.
- Preservar legacy live charge y compensaciones existentes.
- Separar crear temporal, mantener journeyman, retirar temporales y finalizar postmatch.

Reglas:
- No esconder compensaciones legacy sin documentarlas.
- No cambiar persistencia de golpe.

Criterio de salida:
- Temporales tienen servicio dedicado en backend v2 y tests de backend v2 pasan.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2, ejecuta tests de TemporaryPlayerManager en backend v2.
- No ejecutes ni modifiques tests en c:\Users\Franchoped\Software\blood-bowl-manager.
```

## Prompt 010 - Frontend route inventory

```text
Trabaja solo en el frontend Flutter actual. No crees React todavia.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager-front.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2-front.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager-front.

Objetivo: inventariar rutas actuales para preparar React.

Referencias a leer:
- ../blood-bowl-manager/FULL_STACK_REFACTORING_ROADMAP.md, Bloque 3, Paso 3.1.
- FRONTEND_REFACTORING_PLAN.md, Fase 0, Paso 0.1.

Codigo actual a leer:
- lib/core/router/app_router.dart
- lib/core/shell/app_shell.dart
- lib/core/shell/widgets/app_shell_navigation_widgets.dart

Trabajo:
- Crear docs/frontend/current-route-inventory.md.
- Listar cada ruta con auth, pantalla Flutter, datos que carga, acciones principales y decision React: migrar, reemplazar, deprecar o no portar.
- Marcar rutas /debug/* como no portar/eliminar de v2.

Reglas:
- No cambies codigo Flutter ni documentacion en el repo legacy.
- No empieces React.

Criterio de salida:
- Todas las rutas actuales tienen decision preliminar.

Validacion:
- Markdown limpio en c:\Users\Franchoped\Software\bb-manager-v2-front.
```

## Prompt 011 - Frontend API usage inventory

```text
Trabaja solo en el frontend Flutter actual. No crees React todavia.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager-front.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2-front.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager-front.

Objetivo: inventariar endpoints usados por Flutter.

Referencias a leer:
- ../blood-bowl-manager/FULL_STACK_REFACTORING_ROADMAP.md, Bloque 3, Paso 3.1.
- FRONTEND_REFACTORING_PLAN.md, Fase 0, Paso 0.2.
- ../blood-bowl-manager/BACKEND_REFACTORING_PLAN.md, seccion de endpoints versionados.

Codigo actual a leer:
- lib/features/shared/data/team_repository.dart
- lib/features/shared/data/league_repository.dart
- lib/features/shared/data/quick_match_repository.dart
- lib/features/auth/data/repositories/auth_repository.dart
- lib/core/network/api_client.dart

Trabajo:
- Crear docs/frontend/current-api-usage.md.
- Listar endpoint, metodo, feature, payload, response model y pantalla consumidora.
- Marcar endpoints legacy como /perks y rutas sin /api/v1.
- Marcar dependencias de assets/rules locales como deuda a sustituir por backend v2.

Reglas:
- No cambies codigo funcional ni documentacion en el repo legacy.
- No normalices contratos todavia.

Criterio de salida:
- React sabra que endpoints preservar temporalmente y cuales no copiar.

Validacion:
- Markdown limpio en c:\Users\Franchoped\Software\bb-manager-v2-front.
```

## Prompt 012 - Frontend React stack decision

Estado: HECHO. No repetir salvo que Francho pida revisar el stack.

```text
Trabaja solo en documentacion del frontend.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager-front.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2-front.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager-front.

Objetivo: documentar el stack React elegido antes de crear codigo.

Referencias a leer:
- ../blood-bowl-manager/FULL_STACK_REFACTORING_ROADMAP.md, Bloque 3, Paso 3.2.
- FRONTEND_REFACTORING_PLAN.md, Fase 1 y Arquitectura objetivo React.

Codigo/documentos a leer:
- README.md
- package/tooling existente si lo hubiera.
- pubspec.yaml solo para entender assets y dependencias Flutter a no copiar.

Trabajo:
- Crear docs/frontend/react-stack-decision.md.
- Documentar stack elegido: Vite + React + TypeScript, React Router, TanStack Query, React Hook Form + Zod, Vitest/Testing Library, MSW, Playwright.
- Documentar UI elegida: Tailwind CSS + shadcn/ui sobre CSS variables.
- Documentar auth con bearer tokens/JWT.
- Documentar i18n ES/EN desde el inicio.
- Documentar Cloudflare Pages + GitHub Actions como deploy inicial.
- Documentar comandos npm esperados.

Reglas:
- No inicialices proyecto aun.
- No instales dependencias.
- No modifiques el repo Flutter legacy.

Criterio de salida:
- Stack decidido sin nuevas preguntas abiertas salvo bloqueo tecnico real.

Validacion:
- Markdown limpio.
```

## Prompt 013 - Frontend React skeleton

Estado: HECHO. No repetir salvo que Francho pida rehacer el skeleton.

```text
Trabaja solo en el frontend.

Repositorios:
- LECTURA OPCIONAL: c:\Users\Franchoped\Software\blood-bowl-manager-front.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2-front.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager-front.

Objetivo: crear skeleton React limpio sin migrar features grandes.

Referencias a leer:
- ../blood-bowl-manager/FULL_STACK_REFACTORING_ROADMAP.md, Bloque 3, Paso 3.3.
- FRONTEND_REFACTORING_PLAN.md, Fase 1.
- docs/frontend/react-stack-decision.md.

Codigo actual a leer:
- No leas pantallas Flutter salvo que necesites confirmar rutas placeholder.

Trabajo:
- Crear proyecto React directamente en c:\Users\Franchoped\Software\bb-manager-v2-front, salvo que ya exista estructura previa.
- Configurar TypeScript estricto, lint, format, test y build.
- Crear AppProviders, router basico, QueryClient y pagina placeholder.
- Preparar i18n ES/EN desde el skeleton.
- No migrar teams/leagues/matches todavia.

Reglas:
- No mezcles React dentro de lib/ Flutter.
- No copies implementacion Flutter, pero conserva el contrato visual actual: layout, fuentes, escala, colores, espaciados, componentes visuales, assets y navegacion.
- No arranques dev server persistente.
- Todo archivo nuevo o modificado debe quedar en c:\Users\Franchoped\Software\bb-manager-v2-front.

Criterio de salida:
- npm scripts existen para typecheck/lint/test/build.
- App vacia compila.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2-front, ejecuta comandos no persistentes: typecheck/lint/test/build si estan disponibles.
- No ejecutes ni modifiques nada en c:\Users\Franchoped\Software\blood-bowl-manager-front.
```

## -- Prompt 014 - Frontend design tokens, shell, auth mocks

```text
Trabaja solo en el frontend React skeleton.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager-front.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2-front.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager-front.

Objetivo: crear base visual, shell responsive y auth base con mocks, sin migrar features de dominio.

Referencias a leer:
- ../blood-bowl-manager/FULL_STACK_REFACTORING_ROADMAP.md, Bloque 3, Paso 3.4.
- FRONTEND_REFACTORING_PLAN.md, Fases 2 y 3.

Codigo Flutter actual a leer:
- lib/core/theme/app_colors.dart
- lib/core/theme/app_theme.dart
- lib/core/theme/app_dimensions.dart
- lib/core/shell/app_shell.dart
- lib/core/network/api_client.dart
- lib/features/auth/data/repositories/auth_repository.dart
- lib/features/auth/data/providers/auth_provider.dart

Trabajo:
- Crear tokens visuales React a partir de app_colors.dart, app_theme.dart, app_dimensions.dart y fuentes/assets actuales.
- Crear primitives UI minimas usando Tailwind CSS + shadcn/ui, adaptadas para verse como el frontend actual.
- Crear AppShell responsive con rutas placeholder manteniendo layout, navegacion, densidad, espaciados y jerarquia visual actuales.
- Crear http client con bearer token/JWT, auth API mock con MSW, login/logout/me basicos y route guard.
- Preparar textos visibles en namespaces ES/EN.

Reglas:
- Usa Flutter como contrato visual de layout, fonts, colores, espaciados y apariencia; no copies widgets ni logica Flutter.
- Si Tailwind/shadcn no encaja visualmente de serie, ajusta tokens/clases para aproximar el aspecto actual antes que imponer un look nuevo.
- No metas rutas debug en produccion.
- No implementes teams/leagues todavia.
- Todo archivo nuevo o modificado debe quedar en c:\Users\Franchoped\Software\bb-manager-v2-front.

Criterio de salida:
- Shell y auth mock funcionan en tests.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2-front, ejecuta npm run typecheck/lint/test/build.
- No ejecutes ni modifiques nada en c:\Users\Franchoped\Software\blood-bowl-manager-front.
```

## -- Prompt 015 - Backend catalog loader versionado

```text
Trabaja solo en el backend.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager.

Objetivo: crear catalog loader versionado read-only para bb2025.

Referencias a leer:
- FULL_STACK_REFACTORING_ROADMAP.md, Bloque 4, Paso 4.1.
- BACKEND_REFACTORING_PLAN.md, Fase 9.
- README_RULESETS_MIGRATION_PLAN.md.

Codigo actual a leer:
- database/seeding.py, solo conversiones utiles.
- config/skills.json
- config/base_teams.json
- config/star_players.json
- models/base/*.py

Trabajo:
- Crear estructura catalog/rulesets/bb2025 minima.
- Crear modelos Pydantic del loader.
- Crear loader read-only sin Mongo.
- Crear validacion cruzada inicial.
- Crear tests unitarios del loader.

Reglas:
- No generar/copiar texto oficial protegido.
- No modificar ni resumir los textos de reglas/catalogos ya existentes; conservarlos exactos.
- No escribir en Mongo desde el loader.
- No borrar ni modificar seed legacy.

Criterio de salida:
- Catalogo carga y valida sin DB.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2, ejecuta tests del loader en backend v2.
- No ejecutes ni modifiques tests en c:\Users\Franchoped\Software\blood-bowl-manager.
```

## Prompt 016 - Backend seed catalog

```text
Trabaja solo en el backend.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager.

Objetivo: hacer que el seeding use el catalogo versionado como fuente principal.

Referencias a leer:
- FULL_STACK_REFACTORING_ROADMAP.md, Bloque 4, Paso 4.2.
- BACKEND_REFACTORING_PLAN.md, Fase 10.
- README_RULESETS_MIGRATION_PLAN.md.

Codigo actual a leer:
- database/seeding.py
- scripts/seed_database.py
- scripts/seed_base_rosters.py
- catalog_loader/* si ya existe.

Trabajo:
- Crear scripts/validate_catalog.py.
- Crear scripts/seed_catalog.py --ruleset bb2025 o equivalente.
- Crear orquestador pequeno de seeding en backend v2.
- Sembrar en base de datos nueva; no disenar migracion obligatoria desde la DB actual.

Reglas:
- No borrar ni modificar scripts legacy; solo leerlos/auditarlos.
- No duplicar conversiones nuevas y viejas.
- Mantener idempotencia.
- No crear fallback legacy como comportamiento normal.
- No modificar database/seeding.py ni scripts legacy.

Criterio de salida:
- Se puede validar y sembrar desde catalogo versionado.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2, ejecuta tests relacionados y validate_catalog en backend v2.
- No ejecutes ni modifiques scripts/tests en c:\Users\Franchoped\Software\blood-bowl-manager.
```

## Prompt 017 - Backend ruleset_id

```text
Trabaja solo en el backend.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager.

Objetivo: introducir ruleset_id en catalogos y dominio sin romper datos existentes.

Referencias a leer:
- FULL_STACK_REFACTORING_ROADMAP.md, Bloque 4, Paso 4.3.
- BACKEND_REFACTORING_PLAN.md, Fase 11.
- README_RULESETS_MIGRATION_PLAN.md.

Codigo actual a leer:
- models/base/*.py
- models/user_team/team.py
- models/league/league.py
- services/base_roster_service.py
- services/user_team_service.py
- services/league_service.py

Trabajo:
- Agregar ruleset_id donde corresponda.
- Mantener default bb2025 para datos nuevos.
- Documentar que la DB v2 es nueva y que no hay migracion obligatoria de historico.
- Tests para resolver ruleset_id en equipos/ligas/partidos.

Reglas:
- No romper documentos existentes en backend v2.
- No cambiar IDs canonicos sin migracion.
- No modificar modelos legacy.

Criterio de salida:
- Flujos principales saben con que ruleset operan.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2, ejecuta tests enfocados de ruleset_id en backend v2.
- No ejecutes ni modifiques tests en c:\Users\Franchoped\Software\blood-bowl-manager.
```

## Prompt 018 - Backend /rulesets endpoints

```text
Trabaja solo en el backend.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager.

Objetivo: crear endpoints /api/v1/rulesets para que React descubra catalogos.

Referencias a leer:
- FULL_STACK_REFACTORING_ROADMAP.md, Bloque 4, Paso 4.4.
- BACKEND_REFACTORING_PLAN.md, Fase 12.
- README_RULESETS_MIGRATION_PLAN.md.

Codigo actual a leer:
- routes/rules.py
- routes/base_roster.py
- routes/star_player.py
- services/rules_service.py
- services/base_roster_service.py
- services/star_player_service.py
- catalog_loader/*

Trabajo:
- Crear routes/rulesets.py, service y schemas.
- Implementar endpoints minimos: /api/v1/rulesets, /api/v1/rulesets/{ruleset_id}, /teams, /skills, /inducements, /advancement, /tables bajo el ruleset.
- Exponer catalogos desde backend v2 como fuente canonica para React.

Reglas:
- No reutilizar /rules con query params ambiguos.
- No mezclar response models legacy con v1.

Criterio de salida:
- React puede consumir catalogos desde /api/v1/rulesets sin assets/rules locales.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2, ejecuta tests de endpoints si existe setup; si no, tests de service en backend v2.
- No ejecutes ni modifiques tests en c:\Users\Franchoped\Software\blood-bowl-manager.
```

## Prompt 019 - Backend /api/v1 contracts

```text
Trabaja solo en el backend.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager.

Objetivo: definir contratos /api/v1 limpios para React.

Referencias a leer:
- FULL_STACK_REFACTORING_ROADMAP.md, Bloque 4, Paso 4.5.
- BACKEND_REFACTORING_PLAN.md, Fase 15.
- ../blood-bowl-manager-front/FRONTEND_REFACTORING_PLAN.md, secciones API/router.

Codigo actual a leer:
- app.py
- routes/*.py
- schemas/*.py
- docs/backend/current-api-inventory.md si existe.
- ../blood-bowl-manager-front/docs/frontend/current-api-usage.md si existe.

Trabajo:
- Definir estructura /api/v1 para auth/session, rulesets, teams, leagues, matches, aftermatch y tactics.
- Crear docs/backend/api-v1-contract-plan.md o implementar rutas si ya esta claro.
- Definir auth con bearer tokens/JWT.
- Identificar endpoints legacy que no se portan y su reemplazo limpio.

Reglas:
- No mezclar rutas nuevas y legacy sin prefijo.
- No disenar contratos para mantener Flutter; Flutter es solo fuente de comportamiento.

Criterio de salida:
- React tiene contrato claro para migracion real.

Validacion:
- Si solo documenta, Markdown limpio.
- Si implementa, desde c:\Users\Franchoped\Software\bb-manager-v2 ejecuta tests/API checks enfocados en backend v2.
- No ejecutes ni modifiques tests en c:\Users\Franchoped\Software\blood-bowl-manager.
```

## Prompt 020 - Frontend React types, schemas and API modules

```text
Trabaja solo en el frontend React.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager-front.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2-front.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager-front.

Objetivo: crear tipos, schemas y modulos API sobre contratos limpios.

Referencias a leer:
- ../blood-bowl-manager/FULL_STACK_REFACTORING_ROADMAP.md, Bloque 5, Paso 5.1.
- FRONTEND_REFACTORING_PLAN.md, Fase 4.
- ../blood-bowl-manager/docs/backend/api-v1-contract-plan.md si existe.
- ../blood-bowl-manager/BACKEND_REFACTORING_PLAN.md, Fases /rulesets y /api/v1.

Codigo actual a leer:
- lib/features/*/domain/models/*.dart solo para shape actual.
- lib/features/shared/data/*.dart solo para payloads actuales.

Trabajo:
- Crear tipos/schemas para User, Ruleset, Team, Player, League, Match, MatchEvent y AftermatchReport.
- Crear query keys y API modules por feature.
- Usar OpenAPI si existe; si no, Zod temporal.
- Crear base i18n ES/EN para mensajes de error/labels compartidos.

Reglas:
- No llames fetch/axios desde componentes.
- No copies getters UI de modelos Flutter.
- No uses defaults silenciosos que oculten payload roto.
- No cargar catalogos/reglas/wiki desde assets locales.

Criterio de salida:
- API modules centralizados y testeados con MSW o unit tests.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2-front, ejecuta npm run typecheck/lint/test/build.
- No ejecutes ni modifiques nada en c:\Users\Franchoped\Software\blood-bowl-manager-front.
```

## Prompt 021 - Frontend teams list/detail

```text
Trabaja solo en el frontend React.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager-front.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2-front.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager-front.

Objetivo: migrar listado y detalle de equipos como primera feature real.

Referencias a leer:
- ../blood-bowl-manager/FULL_STACK_REFACTORING_ROADMAP.md, Bloque 5, Paso 5.2.
- FRONTEND_REFACTORING_PLAN.md, Fase 5.1.
- BACKEND_REFACTORING_PLAN.md, contratos teams /api/v1 si existen.

Codigo Flutter actual a leer:
- lib/features/my_teams/presentation/screens/my_teams_screen.dart
- lib/features/my_teams/presentation/screens/my_team_detail_screen.dart
- lib/features/my_teams/domain/models/user_team.dart
- lib/features/shared/data/team_repository.dart

Trabajo:
- Crear rutas React para teams list, team detail y shared team si aplica.
- Crear componentes pequenos: TeamSummaryCard, RosterTable, StaffPanel, TreasuryPanel, WarningsPanel.
- Usar API modules y query keys ya creados.

Reglas:
- No crear una route gigante.
- No meter reglas canonicas de team value en UI.
- No depender de assets/rules locales como fuente de verdad.
- Mantener imagenes existentes cuando sean assets visuales, no datos canonicos.

Criterio de salida:
- List/detail funcionan con MSW y backend cuando este disponible.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2-front, ejecuta npm run typecheck/lint/test/build.
- No ejecutes ni modifiques nada en c:\Users\Franchoped\Software\blood-bowl-manager-front.
```

## Prompt 022 - Frontend team creator

```text
Trabaja solo en el frontend React.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager-front.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2-front.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager-front.

Objetivo: migrar Team Creator como wizard limpio.

Referencias a leer:
- ../blood-bowl-manager/FULL_STACK_REFACTORING_ROADMAP.md, Bloque 5, Paso 5.2.
- FRONTEND_REFACTORING_PLAN.md, Fase 5.2.

Codigo Flutter actual a leer:
- lib/features/team_creator/presentation/screens/team_creator_screen.dart
- lib/features/team_creator/presentation/widgets/team_creator_race_step.dart
- lib/features/team_creator/presentation/widgets/team_creator_roster_step.dart
- lib/features/team_creator/presentation/widgets/team_creator_confirm_step.dart
- lib/features/team_creator/presentation/widgets/race_card.dart
- lib/features/team_creator/presentation/widgets/position_card.dart
- lib/features/team_creator/presentation/widgets/budget_bar.dart

Trabajo:
- Crear wizard dividido en race, roster, staff si aplica, confirm.
- Crear reducer/hook testeado para estado de wizard.
- Crear payload de creacion usando API module.

Reglas:
- No copiar pantalla monolitica.
- Budget de UI es preview; backend valida definitivo.

Criterio de salida:
- Crear equipo funciona con mocks y payload correcto.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2-front, ejecuta npm run typecheck/lint/test/build.
- No ejecutes ni modifiques nada en c:\Users\Franchoped\Software\blood-bowl-manager-front.
```

## Prompt 023 - Frontend player card

```text
Trabaja solo en el frontend React.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager-front.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2-front.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager-front.

Objetivo: migrar ficha de jugador sin crear otro archivo gigante.

Referencias a leer:
- ../blood-bowl-manager/FULL_STACK_REFACTORING_ROADMAP.md, Bloque 5, Paso 5.2.
- FRONTEND_REFACTORING_PLAN.md, Fase 5.3.

Codigo Flutter actual a leer:
- lib/features/roster/presentation/screens/player_card_screen.dart, solo secciones necesarias.
- lib/features/roster/presentation/widgets/player_row.dart
- lib/features/shared/utils/player_advancement.dart
- lib/features/my_teams/domain/models/user_team.dart

Trabajo:
- Crear PlayerCard route con secciones/tabs pequenas.
- Crear componentes para stats, skills, injuries, career, advancement actions e image handling si aplica.
- Crear tests de payloads de acciones principales.

Reglas:
- No copiar 4000+ lineas a React.
- No poner colores/labels UI dentro del modelo API.

Criterio de salida:
- Player detail y acciones clave funcionan con mocks.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2-front, ejecuta npm run typecheck/lint/test/build.
- No ejecutes ni modifiques nada en c:\Users\Franchoped\Software\blood-bowl-manager-front.
```

## Prompt 024 - Frontend leagues

```text
Trabaja solo en el frontend React.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager-front.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2-front.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager-front.

Objetivo: migrar ligas list/create/join/overview/backoffice por piezas.

Referencias a leer:
- ../blood-bowl-manager/FULL_STACK_REFACTORING_ROADMAP.md, Bloque 5, Paso 5.3.
- FRONTEND_REFACTORING_PLAN.md, Fase 6.

Codigo Flutter actual a leer:
- lib/features/leagues/presentation/screens/leagues_screen.dart
- lib/features/leagues/presentation/screens/create_league_screen.dart
- lib/features/leagues/presentation/screens/join_league_screen.dart
- lib/features/league/presentation/screens/league_overview_screen.dart
- lib/features/league/presentation/screens/league_backoffice_screen.dart
- lib/features/league/presentation/widgets/standings_table.dart
- lib/features/league/presentation/widgets/match_card.dart
- lib/features/league/presentation/widgets/league_stats_dashboard.dart
- lib/features/shared/data/league_repository.dart

Trabajo:
- Migrar primero list/create/join.
- Despues overview por tabs: standings, schedule, current round, stats, bracket.
- Mantener backoffice separado.

Reglas:
- No crear un LeagueOverview gigante.
- No duplicar modelos summary/detail sin razon.

Criterio de salida:
- Usuario puede crear/unirse/ver liga en React.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2-front, ejecuta npm run typecheck/lint/test/build.
- No ejecutes ni modifiques nada en c:\Users\Franchoped\Software\blood-bowl-manager-front.
```

## Prompt 025 - Frontend match/live/quick match

```text
Trabaja solo en el frontend React.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager-front.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2-front.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager-front.

Objetivo: migrar match live y quick match usando controlador comun.

Referencias a leer:
- ../blood-bowl-manager/FULL_STACK_REFACTORING_ROADMAP.md, Bloque 5, Paso 5.4.
- FRONTEND_REFACTORING_PLAN.md, Fase 7.
- BACKEND_REFACTORING_PLAN.md, secciones match/live state y aftermatch si necesitas contrato.

Codigo Flutter actual a leer:
- lib/features/live_match/presentation/screens/live_match_screen.dart
- lib/features/live_match/presentation/widgets/live_match_pre_match.dart
- lib/features/live_match/presentation/widgets/live_match_team_prep.dart
- lib/features/live_match/presentation/widgets/live_match_live_view.dart, solo acciones/eventos necesarias.
- lib/features/live_match/presentation/widgets/live_match_dialogs.dart
- lib/features/shared/presentation/widgets/match_event_dialog.dart
- lib/features/shared/data/quick_match_repository.dart
- lib/features/shared/data/league_repository.dart, solo metodos match.

Trabajo:
- Crear adapter comun para league match y quick match.
- Crear reducer/state machine.
- Migrar pre-match, team prep, scoreboard, actions y event timeline por componentes pequenos.

Reglas:
- No duplicar league/quick match.
- No reintroducir detail string como semantica unica si backend ya da estructura.
- Budget de inducements debe venir del backend match state.

Criterio de salida:
- Un partido basico se puede jugar en React con mocks/backend.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2-front, ejecuta npm run typecheck/lint/test/build.
- No ejecutes ni modifiques nada en c:\Users\Franchoped\Software\blood-bowl-manager-front.
```

## Prompt 026 - Frontend aftermatch

```text
Trabaja solo en el frontend React.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager-front.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2-front.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager-front.

Objetivo: migrar aftermatch empezando por payload/hydration, luego wizard.

Referencias a leer:
- ../blood-bowl-manager/FULL_STACK_REFACTORING_ROADMAP.md, Bloque 5, Paso 5.5.
- FRONTEND_REFACTORING_PLAN.md, Fase 8.
- BACKEND_REFACTORING_PLAN.md, Fase 6 y contratos aftermatch.

Codigo Flutter actual a leer:
- lib/features/aftermatch/domain/models/aftermatch.dart
- lib/features/aftermatch/presentation/screens/aftermatch_screen.dart, solo payload/hydration/secciones necesarias.
- lib/features/aftermatch/presentation/widgets/touchdown_recorder.dart
- lib/features/aftermatch/presentation/widgets/injury_recorder.dart
- lib/features/aftermatch/presentation/widgets/score_input.dart
- lib/features/aftermatch/presentation/widgets/spp_summary.dart
- lib/features/shared/data/league_repository.dart, metodos applyAftermatch/finalizeAftermatchRosters.

Trabajo:
- Crear schema AftermatchReport.
- Crear buildAftermatchPayload e hydrateAftermatchReport con tests.
- Crear wizard por pasos: MVP, SPP/stats, injuries, winnings, purchases, review.

Reglas:
- No crear otra pantalla de 5000 lineas.
- Cualquier campo nuevo debe tener payload + hydration + test.

Criterio de salida:
- React puede enviar aftermatch completo y rehidratar reporte guardado.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2-front, ejecuta npm run typecheck/lint/test/build.
- No ejecutes ni modifiques nada en c:\Users\Franchoped\Software\blood-bowl-manager-front.
```

## Prompt 027 - Frontend wiki/rulesets

```text
Trabaja solo en el frontend React.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager-front.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2-front.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager-front.

Objetivo: migrar wiki y reglas consumiendo /rulesets del backend.

Referencias a leer:
- ../blood-bowl-manager/FULL_STACK_REFACTORING_ROADMAP.md, Bloque 5, Paso 5.6.
- FRONTEND_REFACTORING_PLAN.md, Fase 9.
- BACKEND_REFACTORING_PLAN.md, Fases 9, 12 y 15.

Codigo Flutter actual a leer:
- lib/features/wiki/presentation/screens/wiki_skills_screen.dart
- lib/features/wiki/presentation/screens/wiki_weather_screen.dart
- lib/features/wiki/presentation/screens/wiki_star_players_screen.dart
- lib/features/wiki/presentation/screens/wiki_injuries_screen.dart
- lib/features/wiki/presentation/widgets/wiki_page_layout.dart
- lib/features/wiki/presentation/widgets/wiki_page_chrome.dart
- lib/features/shared/data/team_repository.dart, solo catalog/rules methods.
- assets/rules/* solo para inventariar datos legacy que deben venir del backend.

Trabajo:
- Crear ruleset discovery.
- Migrar wiki modular con layouts comunes.
- Consumir toda documentacion/catalogos desde backend v2.
- Usar assets locales solo como imagen visual cuando aplique, nunca como fuente de reglas.
- Mantener textos de reglas/catalogos exactos; no resumir ni reescribir.

Reglas:
- No copiar texto oficial protegido.
- No crear fallback local de reglas/catalogos en React.
- No resumir ni reescribir textos de reglas/catalogos recibidos del backend.

Criterio de salida:
- Wiki React carga desde backend rulesets.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2-front, ejecuta npm run typecheck/lint/test/build.
- No ejecutes ni modifiques nada en c:\Users\Franchoped\Software\blood-bowl-manager-front.
```

## Prompt 028 - Frontend tactics

```text
Trabaja solo en el frontend React.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager-front.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2-front.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager-front.

Objetivo: migrar tacticas separando dominio, tablero y persistencia.

Referencias a leer:
- ../blood-bowl-manager/FULL_STACK_REFACTORING_ROADMAP.md, Bloque 5, Paso 5.7.
- FRONTEND_REFACTORING_PLAN.md, Fase 10.

Codigo Flutter actual a leer:
- lib/features/tactics/presentation/screens/tactics_screen.dart
- lib/features/tactics/presentation/screens/my_tactics_screen.dart
- assets/images/plantilla_pitch.png

Trabajo:
- Crear modelo de tacticas y tests de posicionamiento.
- Crear UI de campo responsive.
- Crear persistencia usando API module.

Reglas:
- No mezclar geometria, UI y API en un solo componente.
- No usar coordenadas magicas sin constantes.

Criterio de salida:
- Crear/editar/ver tacticas funciona o queda scope reducido documentado.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2-front, ejecuta npm run typecheck/lint/test/build.
- No ejecutes ni modifiques nada en c:\Users\Franchoped\Software\blood-bowl-manager-front.
```

## Prompt 029 - Backend legacy cleanup

```text
Trabaja solo en el backend.

Repositorios:
- LECTURA/AUDITORIA: c:\Users\Franchoped\Software\blood-bowl-manager.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager.

Objetivo: limpiar codigo legacy/muerto del backend con auditoria previa.

Referencias a leer:
- FULL_STACK_REFACTORING_ROADMAP.md, Bloque 6, Paso 6.1.
- BACKEND_REFACTORING_PLAN.md, Fase 16 e Inventario de codigo legacy.

Codigo actual a leer:
- app.py
- routes/team.py
- routes/character.py
- routes/perk.py
- routes/admin.py
- services/team_operations.py
- services/character_operations.py
- services/perk_operations.py
- models/match.py
- models/tournament.py
- database/database_dependencies.py
- README.md seccion de colecciones.

Trabajo:
- Medir usos/imports de legacy.
- Crear docs/backend/legacy-usage-inventory.md si no existe.
- Eliminar legacy del producto final o reimplementar comportamiento necesario con contrato limpio.
- Auditar colecciones residuales, pero recordar que backend v2 usa DB nueva.

Reglas:
- No borrar ni modificar archivos/datos del repo legacy; solo auditarlo.
- No mantener Flutter como restriccion de diseno del backend v2.

Criterio de salida:
- No queda legacy en backend v2 salvo excepcion documentada con fecha de retirada.

Validacion:
- Tests backend relevantes.
```

## Prompt 030 - Frontend debug/assets/Flutter cleanup

```text
Trabaja solo en el frontend.

Repositorios:
- LECTURA/AUDITORIA: c:\Users\Franchoped\Software\blood-bowl-manager-front.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2-front.
- PROHIBIDO: modificar cualquier archivo en c:\Users\Franchoped\Software\blood-bowl-manager-front.

Objetivo: limpiar debug, assets, datos locales y preparar retirada de Flutter cuando React cubra flujos.

Referencias a leer:
- ../blood-bowl-manager/FULL_STACK_REFACTORING_ROADMAP.md, Bloque 6, Paso 6.2.
- FRONTEND_REFACTORING_PLAN.md, Fase 12 e Inventario de codigo legacy.

Codigo actual a leer:
- lib/features/debug/*
- lib/core/router/app_router.dart, rutas /debug.
- lib/core/l10n/translations.dart, traducciones debug.
- assets/rules/*
- assets/data.json
- assets/images/* y assets/teams/* solo para auditoria.
- api/, config/, main.py, create_placeholders.py, download_*.py.

Trabajo:
- Crear inventario de assets/datos/scripts.
- Eliminar debug tools actuales; no conservar modo dev de aftermatch por ahora.
- Asegurar que build productivo no contiene credenciales/rutas debug.
- Definir plan de retirada de Flutter: archivar, borrar o mantener temporal con fecha.

Reglas:
- Conservar imagenes actuales cuando sean assets visuales.
- No mantener reglas locales como fuente canonica en ningun caso.

Criterio de salida:
- Frontend final no contiene debug/credenciales ni datos muertos conocidos sin decision.

Validacion:
- Desde c:\Users\Franchoped\Software\bb-manager-v2-front, ejecuta npm run typecheck/lint/test/build si React existe.
- Grep de credenciales/rutas debug en build/codigo.
- No ejecutes ni modifiques nada en c:\Users\Franchoped\Software\blood-bowl-manager-front.
```

## Prompt 031 - Full-stack quality, smoke, deploy and rollback

```text
Trabaja como coordinador full-stack. No implementes nuevas features.

Repositorios:
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager.
- LECTURA: c:\Users\Franchoped\Software\blood-bowl-manager-front.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2, solo documentacion/evidencias finales backend si hace falta.
- ESCRITURA: c:\Users\Franchoped\Software\bb-manager-v2-front, solo documentacion/evidencias finales frontend si hace falta.
- PROHIBIDO: modificar cualquier archivo en los repos legacy.

Objetivo: hacer endurecimiento final antes de considerar la migracion lista.

Referencias a leer:
- FULL_STACK_REFACTORING_ROADMAP.md, Bloque 7.
- BACKEND_REFACTORING_PLAN.md, Criterios globales.
- ../blood-bowl-manager-front/FRONTEND_REFACTORING_PLAN.md, Criterios globales.

Codigo/documentos a leer:
- docs/backend/*
- ../blood-bowl-manager-front/docs/frontend/*
- workflows de CI/deploy.
- README de ambos repos.

Trabajo:
- Ejecutar o documentar validacion backend completa.
- Ejecutar o documentar validacion React completa: typecheck, lint, test, build, Playwright smoke.
- Revisar OpenAPI/contratos.
- Revisar cobertura i18n ES/EN de textos visibles.
- Revisar deploy Cloudflare Pages con GitHub Actions y rollback.
- Crear checklist final de aceptacion y riesgos residuales.

Reglas:
- No arranques servidores persistentes salvo que Francho lo pida.
- No arregles bugs nuevos no relacionados; documentalos como follow-up si no bloquean.

Criterio de salida:
- Hay evidencia clara de que backend y React estan listos o lista de bloqueos concreta.

Validacion:
- Comandos disponibles de ambos repos, con resultados resumidos.
```

## Prompts auxiliares

### Prompt A - Crear ticket pequeno desde un plan grande

```text
Quiero convertir una fase del plan en un ticket pequeno para IA.

Antes de escribir el ticket, identifica el repo destino:
- backend nuevo: escritura solo en c:\Users\Franchoped\Software\bb-manager-v2;
- frontend React nuevo: escritura solo en c:\Users\Franchoped\Software\bb-manager-v2-front;
- backend legacy: lectura/auditoria solo, salvo tickets de caracterizacion explicitamente marcados;
- frontend Flutter legacy: lectura/auditoria solo, nunca escritura.

Lee solo:
- FULL_STACK_REFACTORING_ROADMAP.md
- BACKEND_REFACTORING_PLAN.md o FRONTEND_REFACTORING_PLAN.md segun el repo
- la fase/paso indicado: <pegar fase/paso>

Crea un archivo docs/refactor/tickets/<id>.md con:
- objetivo;
- repo/s de lectura;
- repo unico de escritura;
- lista explicita de repos prohibidos para escritura;
- documentos de referencia;
- codigo actual a leer, maximo 5 archivos;
- tareas;
- malas practicas a evitar;
- criterio de salida;
- validacion;
- lo que NO debe tocar.

No implementes codigo.
```

### Prompt B - Revisar si un ticket esta demasiado grande

```text
Revisa este ticket antes de ejecutarlo.

Objetivo: detectar si el scope es demasiado grande para un chat de IA.

Lee el ticket pegado abajo y responde con:
- si es ejecutable en un chat;
- que partes sobran;
- como partirlo en tickets mas pequenos;
- que archivos maximos deberia leer cada sub-ticket;
- validacion recomendada.

No modifiques archivos.

Ticket:
<pegar ticket>
```

### Prompt C - Auditoria antes de borrar legacy

```text
Antes de borrar codigo legacy, haz auditoria.

Repositorios:
- Backend legacy fuente si aplica: c:\Users\Franchoped\Software\blood-bowl-manager.
- Frontend Flutter legacy fuente si aplica: c:\Users\Franchoped\Software\blood-bowl-manager-front.
- Backend v2 destino a no romper: c:\Users\Franchoped\Software\bb-manager-v2.
- Frontend v2 React destino a no romper: c:\Users\Franchoped\Software\bb-manager-v2-front.

Lee:
- FULL_STACK_REFACTORING_ROADMAP.md, gates de legacy.
- El inventario legacy del plan correspondiente.
- Los archivos candidatos indicados.

Trabajo:
- Buscar imports/usos.
- Buscar rutas o endpoints expuestos.
- Buscar tests que lo cubren.
- Buscar datos/colecciones/assets relacionados.
- Recomendar: mantener, mover a legacy, migrar o borrar.

No borres nada en este chat. Solo entrega informe con evidencia y siguiente ticket recomendado.
```
