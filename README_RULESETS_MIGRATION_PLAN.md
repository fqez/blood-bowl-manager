# Plan de migracion a rulesets versionados

Este README describe un plan paso a paso para que una IA migre el backend desde datos de reglas incrustados en codigo hacia una base de conocimiento versionada por edicion de Blood Bowl.

La idea principal es que el backend deje de depender de grandes bloques hardcodeados en `database/seeding.py` y pase a leer ficheros estructurados, validados y con IDs estables. Asi el frontend podra adaptarse dinamicamente a distintas ediciones sin cambiar pantallas cada vez que cambie el texto, coste, tabla o roster.

## Respuesta corta sobre contenido exacto

Que la aplicacion no sea comercial ayuda a explicar el contexto, pero no elimina automaticamente los derechos de autor. No conviene que la IA genere, copie o reconstruya texto exacto de libros/reglas protegidas.

Politica recomendada para este proyecto:

- Se pueden guardar datos mecanicos y estructurados necesarios para que la app funcione: IDs, costes, limites, tiradas, categorias, estadisticas, referencias, etc.
- Para texto descriptivo, usar resumen propio, texto escrito por el usuario, o referencias a pagina/fuente si el usuario tiene el material.
- Si el usuario tiene permiso o licencia para introducir texto exacto, la arquitectura debe permitir almacenarlo, pero la IA no debe inventarlo ni copiarlo desde fuentes protegidas.
- Separar siempre `rules_text` de `rules_logic`: la app debe funcionar con datos estructurados aunque el texto largo sea resumido o este vacio.
- Si el repositorio es publico, ser aun mas conservador con texto exacto. Si es privado/local, el riesgo cambia, pero no desaparece.

Este plan por tanto disena soporte para contenido exacto si el propietario del proyecto lo aporta bajo su responsabilidad, pero la migracion inicial debe usar contenido estructurado y resumenes propios.

## Objetivos

1. Crear una base de conocimiento versionada por ruleset, por ejemplo `bb2020`, `bb2025`, `house_rules_v1`.
2. Mantener IDs estables entre ediciones cuando el concepto sea el mismo.
3. Permitir que el contenido cambie por ruleset sin romper equipos, ligas, partidos ni pantalla de frontend.
4. Sustituir gradualmente los seeders hardcodeados de `database/seeding.py` por un loader de ficheros.
5. Validar los ficheros antes de escribir nada en MongoDB.
6. Exponer endpoints que permitan al frontend descubrir rulesets, equipos, tablas, incentivos y reglas disponibles.
7. Mantener compatibilidad con los endpoints existentes mientras el frontend migra.
8. Evitar duplicar datos entre backend y frontend. El backend debe ser la fuente canonica.

## No objetivos de la primera migracion

- No reescribir toda la UI del frontend de golpe.
- No introducir texto oficial exacto generado por IA.
- No cambiar reglas de negocio de ligas o partidos salvo lo necesario para seleccionar `ruleset_id`.
- No eliminar inmediatamente los endpoints actuales.
- No cambiar IDs de documentos ya usados por equipos existentes sin alias o migracion.

## Estado actual relevante

Piezas actuales que la IA debe revisar antes de tocar codigo:

- `database/seeding.py`: contiene conversiones de rosters, lectura de `config/skills.json` y `config/base_teams.json`, y seeders hardcodeados para tablas de reglas.
- `models/base/roster.py`: define `BaseRoster`, `BasePlayer`, `BaseStats`, `BasePerk`.
- `models/base/advancement.py`: define `AdvancementRules`.
- `models/base/inducement.py`: define `InducementRules`, `InducementRule`, `PrayerToNuffleResult`.
- `routes/rules.py`: expone endpoints actuales como `/rules/advancements`, `/rules/inducements`, `/rules/weather`, `/rules/kickoff-events`.
- `services/rules_service.py`: obtiene documentos de `rules_catalog`.
- `routes/base_roster.py` y `services/base_roster_service.py`: exponen rosters.
- `config/skills.json`: catalogo canonico actual de habilidades/traits.
- `config/base_teams.json`: fuente actual de rosters backend.
- `blood-bowl-manager-front/assets/rules/teams.json`: fuente frontend antigua que puede servir como referencia de formato, pero no debe seguir siendo la fuente canonica final.
- `blood-bowl-manager-front/assets/rules/rules.json`: reglas frontend antiguas que pueden inspirar la normalizacion.

## Diseno propuesto de carpetas

Crear una carpeta nueva en el backend:

```text
catalog/
  README.md
  schemas/
    ruleset.schema.json
    teams.schema.json
    skills.schema.json
    inducements.schema.json
    advancement.schema.json
    tables.schema.json
    documents.schema.json
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
    bb2025/
      ruleset.json
      skills.json
      teams.json
      inducements.json
      advancement.json
      tables.json
      documents.json
      aliases.json
```

Notas:

- `catalog/schemas` define la forma permitida de cada fichero.
- `catalog/rulesets/<ruleset_id>` contiene los datos de una edicion concreta.
- `aliases.json` permite mapear IDs antiguos o nombres legacy a IDs canonicos.
- No guardar secretos ni configuracion de despliegue aqui.

## Convencion de IDs estables

Los IDs deben ser legibles, minuscula, snake_case o dot notation. Elegir una convencion y aplicarla a todo. Recomendacion: dot notation para dominios globales y snake_case para slug interno.

Ejemplos:

```text
ruleset.bb2020
skill.block
skill.dodge
trait.loner
team.lizardmen
position.lizardmen.skink_lineman
position.lizardmen.saurus_blocker
inducement.bribe
inducement.prayers_to_nuffle
table.prayers_to_nuffle
table.weather
table.kickoff_event
rule.advancement_costs
rule.expensive_mistakes
special_rule.bribery_and_corruption
```

Politica de estabilidad:

- Si el concepto es el mismo entre ediciones, mantener el mismo ID.
- Si cambia solo el texto, coste, limite o traduccion, mantener ID y cambiar contenido dentro del ruleset.
- Si el concepto cambia tanto que la logica deja de ser compatible, crear ID nuevo y declarar relacion en `replaces` o `related_ids`.
- No usar nombres visibles como identificador tecnico permanente si pueden cambiar por traduccion.
- No guardar IDs con espacios, apostrofes, tildes o signos raros.
- Mantener alias para datos antiguos: por ejemplo `shambling-undead` puede apuntar a `team.shambling_undead`.

## Modelo comun de localizacion

Todos los textos visibles deben usar el mismo formato:

```json
{
  "en": "Short user-owned summary",
  "es": "Resumen propio para mostrar en la app"
}
```

Reglas:

- Los campos `name` pueden contener nombres oficiales si son nombres cortos necesarios para identificar elementos del juego.
- Los campos `description`, `notes`, `summary` deben usar texto propio salvo que el usuario aporte contenido con permiso.
- Incluir `source_ref` para apuntar a libro, expansion, pagina o nota interna sin copiar texto largo.

Ejemplo:

```json
{
  "id": "inducement.bribe",
  "name": { "en": "Bribe", "es": "Soborno" },
  "summary": {
    "en": "Allows a coach to attempt to avoid a sending off according to the selected ruleset.",
    "es": "Permite intentar evitar una expulsion segun el ruleset seleccionado."
  },
  "source_ref": "User-owned rulebook reference, no copied text"
}
```

## Esquema de `ruleset.json`

Debe describir la edicion y activar los modulos disponibles.

```json
{
  "id": "ruleset.bb2020",
  "slug": "bb2020",
  "name": { "en": "Blood Bowl 2020", "es": "Blood Bowl 2020" },
  "status": "active",
  "version": 1,
  "default_locale": "es",
  "supported_locales": ["es", "en"],
  "modules": {
    "skills": "skills.json",
    "teams": "teams.json",
    "inducements": "inducements.json",
    "advancement": "advancement.json",
    "tables": "tables.json",
    "documents": "documents.json"
  },
  "source_refs": [
    {
      "label": "Referencia del usuario",
      "notes": "No incluir texto protegido copiado aqui"
    }
  ]
}
```

Campos obligatorios:

- `id`: ID tecnico global.
- `slug`: ID corto usado en URLs y comandos.
- `name`: texto localizado.
- `status`: `draft`, `active`, `deprecated`.
- `version`: entero que sube cuando cambia el fichero.
- `modules`: ficheros que debe cargar el loader.

## Esquema de `skills.json`

Debe reemplazar o envolver `config/skills.json` sin perder compatibilidad.

```json
{
  "ruleset_id": "ruleset.bb2020",
  "categories": [
    { "id": "category.general", "symbol": "G", "name": { "en": "General", "es": "General" } },
    { "id": "category.agility", "symbol": "A", "name": { "en": "Agility", "es": "Agilidad" } },
    { "id": "category.strength", "symbol": "S", "name": { "en": "Strength", "es": "Fuerza" } },
    { "id": "category.passing", "symbol": "P", "name": { "en": "Passing", "es": "Pase" } },
    { "id": "category.mutation", "symbol": "M", "name": { "en": "Mutation", "es": "Mutacion" } },
    { "id": "category.devious", "symbol": "D", "name": { "en": "Devious", "es": "Juego sucio" } },
    { "id": "category.trait", "symbol": "T", "name": { "en": "Trait", "es": "Rasgo" } }
  ],
  "skills": [
    {
      "id": "skill.block",
      "legacy_ids": ["block"],
      "name": { "en": "Block", "es": "Bloquear" },
      "category": "G",
      "type": "skill",
      "parameter_schema": null,
      "summary": { "en": "User-owned summary.", "es": "Resumen propio." },
      "source_ref": "Referencia sin texto copiado"
    }
  ]
}
```

Validaciones:

- `id` unico por ruleset.
- `legacy_ids` sin duplicados globales.
- `category` debe existir en `categories.symbol`.
- Si `parameter_schema` existe, debe definir valores permitidos como `2+`, `3+`, `4+`.

## Esquema de `teams.json`

Debe normalizar lo que hoy esta en `BaseRoster` y en los assets frontend.

```json
{
  "ruleset_id": "ruleset.bb2020",
  "teams": [
    {
      "id": "team.lizardmen",
      "legacy_ids": ["lizardmen"],
      "name": { "en": "Lizardmen", "es": "Hombres Lagarto" },
      "tier": 2,
      "leagues": ["league.lustrian_superleague"],
      "special_rules": [],
      "reroll_cost": 70000,
      "reroll_limit": { "min": 0, "max": 8 },
      "apothecary_allowed": true,
      "assets": {
        "icon": "lizardmen/icon.png",
        "wallpaper": "lizardmen/wallpaper.png"
      },
      "positions": [
        {
          "id": "position.lizardmen.skink_lineman",
          "legacy_type": "skink-lineman",
          "name": { "en": "Skink Lineman", "es": "Eslizon Linea" },
          "role": "Lineman",
          "tags": ["Lineman", "Lizardman"],
          "quantity": { "min": 0, "max": 16 },
          "cost": 60000,
          "stats": { "MA": 8, "ST": 2, "AG": 3, "PA": 4, "AV": 8 },
          "starting_skills": [
            { "id": "skill.dodge" },
            { "id": "trait.stunty" }
          ],
          "primary_access": ["A"],
          "secondary_access": ["G", "D", "P", "S"],
          "assets": {
            "image": null,
            "tag_image": null
          }
        }
      ],
      "constraints": [
        {
          "id": "constraint.lizardmen.example",
          "type": "max_group",
          "max": 1,
          "position_ids": []
        }
      ],
      "notes": []
    }
  ]
}
```

Conversion a modelo actual:

- `team.id` se puede mapear a `BaseRoster.id`, pero decidir si se guarda completo (`team.lizardmen`) o slug legacy (`lizardmen`).
- `positions[].id` se mapea a `BasePlayer.type` o a un campo nuevo `id` si se modifica el modelo.
- `quantity.max` se mapea a `BasePlayer.max`.
- `stats.PA = null` si el jugador no puede pasar.
- `starting_skills[].id` se resuelve contra `skills.json` y se convierte a `BasePerk`.

Decision recomendada:

- En DB nueva, guardar IDs canonicos completos.
- Mantener `legacy_ids` para aceptar URLs o equipos ya creados con IDs antiguos.
- Si cambiar `BaseRoster.id` rompe mucho, introducir `catalog_id` primero y migrar `id` despues.

## Esquema de `inducements.json`

Debe cubrir inducements, coste variable, disponibilidad y tablas relacionadas.

```json
{
  "ruleset_id": "ruleset.bb2020",
  "budget": {
    "id": "rule.inducement_budget",
    "petty_cash_top_up_limit": 50000,
    "lower_ctv_receives_difference": true,
    "lower_ctv_receives_opponent_treasury_spend": true,
    "unspent_petty_cash_lost": true,
    "equal_ctv_treasury_spend_allowed": false,
    "summary": { "en": "User-owned summary.", "es": "Resumen propio." }
  },
  "inducements": [
    {
      "id": "inducement.prayers_to_nuffle",
      "legacy_ids": ["prayers_to_nuffle"],
      "name": { "en": "Prayers to Nuffle", "es": "Plegarias a Nuffle" },
      "category": "special",
      "max_per_team": 16,
      "cost": 50000,
      "cost_options": [],
      "availability": "any",
      "required_special_rules": [],
      "duration": "game",
      "table_id": "table.prayers_to_nuffle",
      "usage_model": "separate_rolls",
      "summary": { "en": "User-owned summary.", "es": "Resumen propio." },
      "notes": []
    }
  ]
}
```

Validaciones:

- `inducements[].id` unico.
- Si `table_id` existe, debe existir en `tables.json`.
- `required_special_rules` deben existir en catalogo de special rules o ser strings legacy permitidos.
- `cost` o `cost_options` deben existir, salvo inducements gratuitos por reglas especiales.
- `max_per_team >= 1`.
- `usage_model` puede ser `single`, `stackable`, `separate_rolls`, `roster_addition`.

## Esquema de `advancement.json`

Debe cubrir costes de SPP, valor de equipo, categorias y tabla de caracteristicas.

```json
{
  "ruleset_id": "ruleset.bb2020",
  "id": "rule.advancement",
  "max_advancements": 6,
  "max_characteristic_improvements_per_stat": 2,
  "random_skill_rolls": 2,
  "random_skill_dice": "2D6",
  "cost_table": [
    {
      "advancement_number": 1,
      "level_name": { "en": "Level name", "es": "Nombre de nivel" },
      "random_primary_skill": 3,
      "choose_primary_skill": 6,
      "choose_secondary_skill": 12,
      "characteristic_improvement": 18
    }
  ],
  "characteristic_table": [
    {
      "min_roll": 1,
      "max_roll": 1,
      "choices": ["MA", "AV"],
      "summary": { "en": "User-owned summary.", "es": "Resumen propio." }
    }
  ],
  "value_increases": [
    { "advancement_type": "random_primary_skill", "value": 10000 }
  ],
  "summary": { "en": "User-owned summary.", "es": "Resumen propio." }
}
```

Validaciones:

- `advancement_number` debe ser consecutivo.
- Costes no negativos.
- `min_roll <= max_roll`.
- Rango total de la tabla no debe solaparse si se define como tabla cerrada.
- `choices` solo puede contener stats permitidas o IDs de opciones permitidas.

## Esquema de `tables.json`

Debe contener tablas tirables genericas: clima, patada inicial, plegarias, heridas, ganancias, errores caros, etc.

```json
{
  "ruleset_id": "ruleset.bb2020",
  "tables": [
    {
      "id": "table.prayers_to_nuffle",
      "legacy_ids": ["prayers_to_nuffle"],
      "name": { "en": "Prayers to Nuffle", "es": "Plegarias a Nuffle" },
      "dice": "D16",
      "roll_mode": "single",
      "results": [
        {
          "roll": { "min": 1, "max": 1 },
          "code": "example_result",
          "name": { "en": "Result name", "es": "Nombre del resultado" },
          "summary": { "en": "User-owned summary.", "es": "Resumen propio." },
          "effects": []
        }
      ],
      "source_ref": "Referencia sin texto copiado"
    }
  ]
}
```

Validaciones:

- `id` unico.
- `dice` reconocido: `D3`, `D6`, `2D6`, `D8`, `D16`, `custom`.
- Rangos de tirada sin solapes cuando la tabla sea cerrada.
- `code` unico dentro de la tabla.
- `effects` debe usar una lista controlada de tipos si se automatiza logica.

## Esquema de `documents.json`

Debe servir para texto navegable y secciones de ayuda, sin ser requisito para la logica.

```json
{
  "ruleset_id": "ruleset.bb2020",
  "documents": [
    {
      "id": "doc.league_pregame_sequence",
      "title": { "en": "Pre-game sequence", "es": "Secuencia previa al partido" },
      "sections": [
        {
          "id": "doc.league_pregame_sequence.inducements",
          "title": { "en": "Inducements", "es": "Incentivos" },
          "summary": { "en": "User-owned summary.", "es": "Resumen propio." },
          "links": ["rule.inducement_budget", "inducement.prayers_to_nuffle"]
        }
      ],
      "source_ref": "Referencia sin texto copiado"
    }
  ]
}
```

Reglas:

- La UI puede mostrar estos documentos, pero no debe depender de ellos para calcular reglas.
- Cada seccion puede enlazar a IDs estructurados.
- Evitar texto largo copiado.

## Cambios de base de datos propuestos

Fase inicial compatible:

- Anadir `ruleset_id` a documentos de catalogo nuevos.
- Mantener los IDs actuales de documentos en `rules_catalog` para endpoints legacy.
- Crear documentos adicionales con IDs namespaced si hace falta.

Colecciones posibles:

1. Mantener colecciones actuales:

   - `base_rosters`
   - `rules_catalog`
2. Anadir colecciones nuevas:

   - `rulesets`
   - `catalog_validation_reports`
3. Alternativa mas ambiciosa:

   - `catalog_items` generica con `ruleset_id`, `kind`, `id`, `payload`.

Recomendacion para este proyecto:

- Paso 1: mantener `base_rosters` y `rules_catalog` para minimizar cambios.
- Paso 2: anadir `ruleset_id` a cada documento.
- Paso 3: cuando el frontend ya use discovery por ruleset, evaluar si merece la pena una coleccion generica.

## Endpoints objetivo

Mantener endpoints actuales:

```text
GET /rules/advancements
GET /rules/inducements
GET /rules/weather
GET /rules/kickoff-events
GET /base-rosters
GET /base-rosters/{roster_id}
```

Anadir endpoints versionados:

```text
GET /rulesets
GET /rulesets/{ruleset_id}
GET /rulesets/{ruleset_id}/catalogue
GET /rulesets/{ruleset_id}/teams
GET /rulesets/{ruleset_id}/teams/{team_id}
GET /rulesets/{ruleset_id}/skills
GET /rulesets/{ruleset_id}/inducements
GET /rulesets/{ruleset_id}/advancement
GET /rulesets/{ruleset_id}/tables
GET /rulesets/{ruleset_id}/tables/{table_id}
GET /rulesets/{ruleset_id}/documents
GET /rulesets/{ruleset_id}/documents/{document_id}
```

Comportamiento:

- Si no se indica ruleset, usar el ruleset activo por defecto.
- Las ligas nuevas deben guardar `ruleset_id`.
- Los equipos creados dentro de una liga deben heredar `ruleset_id` de la liga.
- Los partidos deben resolver reglas desde el `ruleset_id` de la liga o del equipo.
- Para endpoints legacy, el backend puede usar `settings.DEFAULT_RULESET_ID`.

## Plan paso a paso para la IA

### Paso 0: Preparacion

1. Leer este README completo.
2. Leer `database/seeding.py`, `models/base/*`, `schemas/rules.py`, `services/rules_service.py`, `routes/rules.py`, `routes/base_roster.py`.
3. Ejecutar busqueda de usos de `BaseRoster.id`, `base_roster_id`, `AdvancementRules`, `InducementRules` y `rules_catalog`.
4. Confirmar comandos de validacion del backend:
   - Usar `C:\Users\Franchoped\Software\bbman\Scripts\python.exe` desde el backend.
   - Compilar con `python -m compileall`.
5. No tocar frontend todavia salvo que una fase lo indique.

Criterio de salida:

- La IA puede listar todos los seeders actuales y que endpoint/modelo alimenta cada uno.

### Paso 1: Inventario de catalogos actuales

Crear una tabla interna o markdown temporal con estas columnas:

```text
Seeder actual | Modelo Beanie | Coleccion | Endpoint | Fuente actual | Fuente futura | Riesgo
```

Incluir al menos:

- Base rosters.
- Skills/perks.
- Expensive mistakes.
- SPP rewards.
- Advancement.
- Injuries.
- Winnings.
- Dedicated fans.
- Inducements.
- Weather.
- Kickoff events.

Criterio de salida:

- No queda ningun bloque de reglas en `database/seeding.py` sin clasificar.

### Paso 2: Crear estructura de `catalog/`

1. Crear `catalog/README.md` con una version resumida de la convencion.
2. Crear `catalog/rulesets/bb2020/`.
3. Crear ficheros vacios validos para una primera carga:
   - `ruleset.json`
   - `skills.json`
   - `teams.json`
   - `inducements.json`
   - `advancement.json`
   - `tables.json`
   - `documents.json`
   - `aliases.json`
4. No mover aun la logica de seeding.

Criterio de salida:

- Los ficheros existen y contienen JSON valido minimo.

### Paso 3: Definir modelos Pydantic de entrada

Crear modulo nuevo, por ejemplo:

```text
catalog_loader/
  __init__.py
  models.py
  loader.py
  validation.py
  converters.py
```

En `catalog_loader/models.py`, definir modelos Pydantic para el formato de ficheros, no para DB. Separar:

- `LocalizedTextData`.
- `RulesetManifestData`.
- `SkillCatalogData`.
- `TeamCatalogData`.
- `InducementCatalogData`.
- `AdvancementCatalogData`.
- `TableCatalogData`.
- `DocumentCatalogData`.
- `AliasCatalogData`.

Criterio de salida:

- Cargar cada JSON con Pydantic falla con errores claros si falta un campo obligatorio.

### Paso 4: Implementar loader read-only

En `catalog_loader/loader.py`:

1. Resolver ruta base `catalog/rulesets`.
2. Listar rulesets disponibles leyendo cada `ruleset.json`.
3. Cargar un ruleset completo por `slug` o `id`.
4. No escribir en DB aun.
5. Devolver un objeto agregado `LoadedRuleset`.

Funciones sugeridas:

```python
def list_rulesets(base_path: Path) -> list[RulesetManifestData]: ...
def load_ruleset(base_path: Path, ruleset_slug: str) -> LoadedRuleset: ...
def load_json(path: Path) -> dict: ...
```

Validaciones basicas:

- Ficheros referenciados en `ruleset.json.modules` existen.
- `ruleset_id` interno coincide con el manifest.
- JSON parsea correctamente.

Criterio de salida:

- Existe test unitario que carga `bb2020` sin tocar MongoDB.

### Paso 5: Implementar validacion cruzada

En `catalog_loader/validation.py`, validar referencias entre ficheros:

- Skills usados por positions existen.
- Categorias de acceso existen.
- Special rules existen o estan marcadas como legacy/freeform.
- Tables referenciadas por inducements existen.
- Legacy IDs no colisionan.
- IDs canonicos no colisionan.
- Stats estan en rango aceptado.
- Costes son enteros no negativos.
- `quantity.max` no excede 16 salvo excepcion declarada.
- Localizaciones obligatorias estan presentes para `default_locale`.

Criterio de salida:

- Si se introduce un ID roto, el test falla antes de escribir en DB.

### Paso 6: Convertir catalogo a modelos actuales

En `catalog_loader/converters.py`, crear conversores hacia modelos existentes:

```python
def to_base_rosters(loaded: LoadedRuleset) -> list[BaseRoster]: ...
def to_advancement_rules(loaded: LoadedRuleset) -> AdvancementRules: ...
def to_inducement_rules(loaded: LoadedRuleset) -> InducementRules: ...
def to_generic_rule_documents(loaded: LoadedRuleset) -> list[dict]: ...
```

Reglas:

- No duplicar la logica vieja de parsing si se puede extraer de `database/seeding.py`.
- Resolver skills por ID canonico y por `legacy_ids`.
- Convertir `LocalizedTextData` al `LocalizedText` actual.
- Para documentos legacy, generar IDs que los endpoints actuales esperan, por ejemplo `advancement_rules` e `inducements`, mientras no se migren endpoints.

Criterio de salida:

- Los conversores producen objetos iguales o compatibles con los que hoy se siembran.

### Paso 7: Refactorizar `database/seeding.py`

Objetivo: que `seed_all_data()` pueda usar ficheros.

Estrategia segura:

1. Mantener funciones actuales temporalmente.
2. Anadir `seed_ruleset_catalog(ruleset_slug: str)`.
3. Dentro, cargar, validar, convertir y upsert.
4. Llamar a `seed_ruleset_catalog(DEFAULT_RULESET_ID)` desde `seed_all_data()`.
5. Dejar fallback a seeders antiguos solo si falla la carga y solo durante transicion.
6. Cuando tests pasen, eliminar fallback en otra PR/cambio.

Criterio de salida:

- El arranque siembra datos desde `catalog/rulesets/bb2020/*`.
- `database/seeding.py` deja de contener bloques enormes de contenido de reglas.

### Paso 8: Anadir `ruleset_id` en modelos de catalogo

Modificar modelos Beanie de catalogo para poder diferenciar ediciones:

- `BaseRoster`: anadir `ruleset_id: str = "ruleset.bb2020"`.
- `AdvancementRules`: anadir `ruleset_id`.
- `InducementRules`: anadir `ruleset_id`.
- Resto de modelos de reglas en `models/base/*`: anadir `ruleset_id`.

Indices recomendados:

- `ruleset_id + id` unico para documentos donde sea viable.
- Si Beanie/Mongo actual no lo tiene facil, validar unicidad en seeding primero.

Criterio de salida:

- Se pueden tener dos rulesets en DB sin que uno pise al otro.

### Paso 9: Endpoints versionados

Crear rutas nuevas sin romper las existentes.

Posible archivo:

```text
routes/rulesets.py
services/ruleset_service.py
schemas/ruleset.py
```

Endpoints minimos:

```text
GET /rulesets
GET /rulesets/{ruleset_id}
GET /rulesets/{ruleset_id}/teams
GET /rulesets/{ruleset_id}/teams/{team_id}
GET /rulesets/{ruleset_id}/inducements
GET /rulesets/{ruleset_id}/advancement
GET /rulesets/{ruleset_id}/tables/{table_id}
```

Criterio de salida:

- Frontend puede descubrir rulesets y pedir datos para uno concreto.
- Endpoints legacy siguen funcionando con default.

### Paso 10: Asociar ligas y equipos a ruleset

Modificar modelos de dominio:

- Liga: guardar `ruleset_id`.
- Equipo de usuario: guardar `ruleset_id`, heredado de liga o seleccionado al crear equipo fuera de liga.
- Partido: resolver reglas por `ruleset_id` de liga/equipos.

Reglas de compatibilidad:

- Documentos existentes sin `ruleset_id` usan default `ruleset.bb2020`.
- No cambiar datos existentes sin migracion explicita.
- El frontend puede ocultar selector de ruleset al principio y usar default.

Criterio de salida:

- Crear liga nueva persiste `ruleset_id`.
- Ver partido/prepartido usa inducements del ruleset correcto.

### Paso 11: Migrar frontend a backend canonico

Cuando endpoints backend esten listos:

1. Crear repositorio frontend para rulesets.
2. Sustituir lectura directa de `assets/rules/teams.json` para pantallas que ya tengan endpoint backend.
3. Mantener assets como fallback solo durante transicion.
4. Cachear catalogos por `ruleset_id` y `version`.
5. Usar IDs canonicos para enlaces de informacion.
6. Mostrar texto localizado segun idioma de la app.

Criterio de salida:

- El frontend puede renderizar equipos, habilidades e incentivos desde backend.
- Cambiar contenido en `catalog/rulesets/...` y reseedear cambia la app sin recompilar frontend.

### Paso 12: Tests backend

Tests minimos:

- Loader carga manifest.
- Loader falla si falta modulo requerido.
- Validator detecta skill inexistente en roster.
- Validator detecta tabla inexistente en inducement.
- Converter genera `BaseRoster` valido.
- Converter genera `InducementRules` valido.
- Seeding upsert no duplica documentos.
- Endpoints legacy devuelven default ruleset.
- Endpoints versionados devuelven ruleset solicitado.

Comandos esperados:

```powershell
cd C:\Users\Franchoped\Software\blood-bowl-manager
C:\Users\Franchoped\Software\bbman\Scripts\python.exe -m compileall .
C:\Users\Franchoped\Software\bbman\Scripts\python.exe -m pytest
```

Si no existe pytest configurado o falla por problemas no relacionados, documentar el bloqueo y ejecutar al menos compileall.

### Paso 13: Validacion de contenido

Crear script opcional:

```text
scripts/validate_catalog.py
```

Uso esperado:

```powershell
C:\Users\Franchoped\Software\bbman\Scripts\python.exe scripts/validate_catalog.py --ruleset bb2020
```

Debe imprimir:

- Ruleset cargado.
- Numero de skills.
- Numero de teams.
- Numero de positions.
- Numero de inducements.
- Numero de tables.
- Errores de referencias.
- Warnings de localizacion.

Criterio de salida:

- Se puede validar catalogo sin levantar API ni MongoDB.

### Paso 14: Migracion de datos existentes

Crear script opcional:

```text
scripts/migrate_ruleset_ids.py
```

Tareas:

- Anadir `ruleset_id` default a ligas existentes.
- Anadir `ruleset_id` default a equipos existentes.
- Anadir `ruleset_id` default a partidos existentes si aplica.
- Crear aliases para `base_roster_id` antiguos.

Criterio de salida:

- Datos antiguos siguen abriendo en la UI.

### Paso 15: Limpieza final

Cuando todo este migrado:

1. Eliminar bloques hardcodeados de reglas en `database/seeding.py`.
2. Dejar `database/seeding.py` como orquestador del loader.
3. Documentar como anadir una nueva edicion.
4. Eliminar assets frontend duplicados o marcarlos como fallback temporal.
5. Revisar README principal.

Criterio de salida:

- Para anadir una edicion nueva basta con crear `catalog/rulesets/<nuevo_ruleset>/`, validar y sembrar.

## Orden recomendado de commits

1. Documentacion y estructura `catalog/` vacia.
2. Modelos Pydantic del loader y tests de carga.
3. Validacion cruzada y tests.
4. Conversores a modelos actuales y tests.
5. Seeder desde ficheros para un ruleset.
6. `ruleset_id` en catalogos y endpoints versionados.
7. Migracion de ligas/equipos a `ruleset_id`.
8. Frontend consumiendo endpoints versionados.
9. Limpieza de datos hardcodeados.

## Criterios de aceptacion globales

La migracion se considera completa cuando:

- `database/seeding.py` no contiene contenido largo de reglas.
- El backend arranca y siembra desde `catalog/rulesets/bb2020`.
- Hay al menos un script que valida el catalogo sin DB.
- Hay endpoints para listar y consultar rulesets.
- Ligas/equipos/partidos guardan o resuelven `ruleset_id`.
- Frontend no necesita recompilarse para cambios de contenido del catalogo.
- Los IDs canonicos estan documentados y los legacy IDs estan mapeados.
- Tests o validaciones automaticas cubren referencias rotas.

## Instrucciones para una IA que implemente esto

Antes de editar:

- No asumas que todos los datos actuales son correctos.
- No cambies IDs existentes sin buscar sus usos.
- No borres seeders antiguos hasta que los tests demuestren equivalencia.
- No metas texto exacto de reglas protegido salvo que el usuario lo aporte explicitamente y confirme que tiene derecho a usarlo.
- Respeta el texto que existe actualmente para la ultima edicion de las reglas. Esta relativamente curado, asi que no debería cambiar.
- Mantén los cambios por fases pequenas y verificables.

Durante la implementacion:

- Preferir Pydantic para validar JSON antes de convertir.
- Preferir IDs canonicos a nombres visibles.
- Mantener endpoints legacy hasta que el frontend migre.
- Crear tests con fixtures pequenos antes de cargar el catalogo completo.
- Separar errores fatales de warnings.
- Documentar aliases cuando se encuentre un ID antiguo.

Antes de terminar cada fase:

- Ejecutar `compileall`.
- Ejecutar tests relevantes si existen.
- Validar JSON de catalogo.
- Revisar que no se han revertido cambios del usuario.
- Resumir archivos modificados y riesgos restantes.

## Ejemplo de flujo para anadir una nueva edicion

1. Copiar `catalog/rulesets/bb2020` a `catalog/rulesets/bb2025`.
2. Cambiar `ruleset.json`: `id`, `slug`, `name`, `version`, `status`.
3. Mantener IDs iguales para conceptos compartidos.
4. Cambiar solo valores, textos propios, tablas o costes que cambien en esa edicion.
5. Crear IDs nuevos solo para conceptos nuevos.
6. Anadir aliases si hay cambios de nombres visibles.
7. Ejecutar `scripts/validate_catalog.py --ruleset bb2025`.
8. Sembrar backend.
9. Probar endpoints `/rulesets/bb2025/...`.
10. Crear una liga de prueba con `ruleset_id = ruleset.bb2025`.

## Riesgos y mitigaciones

- Riesgo: duplicar fuente de verdad entre frontend y backend.
  Mitigacion: backend canonico, frontend solo cache/fallback temporal.
- Riesgo: validar demasiado tarde, despues de escribir en DB.
  Mitigacion: loader read-only y script de validacion antes de seeding.
- Riesgo: cambiar demasiadas cosas de golpe.
  Mitigacion: fases pequenas.

## Decision recomendada para empezar

Empezar por el camino minimo:

1. Crear `catalog/rulesets/bb2020` con rosters, skills, inducements, advancement y tablas principales.
2. Crear loader read-only con Pydantic.
3. Crear conversores hacia modelos existentes.
4. Hacer que `seed_all_data()` use el loader para `bb2020`.
5. Solo despues anadir endpoints versionados y migrar frontend.

Este orden reduce el riesgo porque primero cambia la fuente de datos, no la experiencia de usuario.
