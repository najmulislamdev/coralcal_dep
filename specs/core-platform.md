---
feature: core-platform
owns:
  - core/
  - coralcal_dep/
last_verified: 8b9c0bee35f5f8e2e99d6b38922b20c1d575a5e8
---

## What it does

Provides the whole project's identity model, login flow, and the rep-facing
landing dashboard. Every other app depends on `core.models.Territory` (FK)
and most depend on `core.models.UserProfile` for role checks.

There are no doctor-facing accounts. Django `User` rows represent **reps**
(territory code as username), or roll-up **zone**/**region** reviewers, or
**superuser** admins — never the doctors themselves.

## Entry points

- `coralcal_dep/urls.py` — root URLConf; mounts every app under its own
  prefix (e.g. `dd/`, `gift/`, `dep/admin/`) plus `core.urls` at `''`.
- `coralcal_dep/settings.py` — single `DATABASES['default']` (MySQL), one
  global `TEMPLATES` dir (`core/templates`) with `APP_DIRS=True` so every
  app's own `templates/` also resolves, `MEDIA_ROOT`/`STATIC_ROOT` at repo
  root, `TIME_ZONE = 'Asia/Dhaka'`.
- `core/urls.py` → `core/views.py`: `home` (redirect to login), `login_view`,
  `user_logout`, `territory_home` (the post-login dashboard at `home/`).
- `core/management/commands/`:
  - `add_territories.py` — bulk upsert `Territory` rows from an Excel file
    (default `core/data/territories.xlsx`; columns `ZoneName`, `RegionName`,
    `SAPAreaCode`→`territory`, `AreaName`→`territory_name`).
  - `create_user(s).py` — creates one Django `User` per `Territory`
    (username = territory code, password `coralcal`), one admin superuser
    (`admin`/`coralcal@123`), and one user per distinct zone/region name.
  - `vendor_pull.py` — pulls vendor static assets via
    `helpers.downloader.download_to_local` (invoked by devs per README, not
    at runtime).

## Key types

- `Territory` (`rpl_territory`): `territory` (unique code, used as the
  username reps log in with), `territory_name`, `region_name`, `zone_name`.
  Every campaign model FKs to this.
- `UserProfile` (1:1 with `User`): `user_type` ∈
  `territory|admin|super_admin|zone|region`. Missing profile + non-superuser
  ⇒ treated as no access in `dep_admin.utils` filters (raises
  `UserProfile.DoesNotExist`, caught and used to return `.none()`).

## Invariants / gotchas

- **Login identifies a territory, not a person.** `login_view` authenticates
  Django username/password, then branches purely on
  `user.userprofile.user_type == 'territory'` → `territory_home`; everyone
  else (zone/region/admin/superuser) → `knowledge_series` (a `dep_admin`
  admin view). A superuser is always routed to admin regardless of profile.
- Views that need "which territory is this rep" do
  `Territory.objects.get(territory=request.user.username)` — i.e. the
  **username itself is the territory code**. This lookup pattern is repeated
  in nearly every campaign app rather than centralized.
- `territory_home` hard-codes the campaign list and reads
  `AccessControl` (owned by `dep_admin`, see
  [admin-console.md](admin-console.md)) by `key`; adding a new campaign
  requires updating this dict **and** seeding a matching `AccessControl` row,
  or the view raises `KeyError` on the missing key.
- `SECRET_KEY`, DB password, and `ALLOWED_HOSTS = ['*']` are hard-coded in
  `settings.py` with `DEBUG = True` — this is a deployed dev-style config,
  not a hardened one.
- `helpers.download_to_local` swallows `requests.RequestException` (prints
  and returns `None`) rather than raising — callers must check the return
  value if failure needs handling.
