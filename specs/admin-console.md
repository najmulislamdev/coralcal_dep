---
feature: admin-console
owns:
  - dep_admin/
last_verified: 8b9c0bee35f5f8e2e99d6b38922b20c1d575a5e8
---

## What it does

Single cross-cutting admin app that gives superusers, and read-scoped
zone/region reviewers, one list+search+sort+paginate+export view per
campaign module (see [gift-catalog-campaigns.md](gift-catalog-campaigns.md),
[doctor-engagement-campaigns.md](doctor-engagement-campaigns.md),
[doctor-profile-directory.md](doctor-profile-directory.md),
[ai-course-registration.md](ai-course-registration.md)), plus two
platform-wide controls: feature-flag toggles (`AccessControl`) and bulk
territory-list upload.

This app has no models of its own for campaign data — it imports every other
app's models directly (`dep_admin/utils.py` top-level imports). Adding a new
campaign module means adding matching functions here too.

## Entry points

- `dep_admin/urls.py` — one path per module, `views.py` for the original
  modules, `view/` package (`dep_admin/view/__init__.py` re-exports) for
  three modules added later: gift_catalogs_2026, nfc_admin,
  orthopedic_dr_dev. Both are wired into the same `urlpatterns` list.
- `dep_admin/views.py` (844 lines) — one `list`, one `export_*` (Excel via
  `openpyxl`), and for some modules one `delete_*` view per campaign, plus:
  - `index` — admin landing page.
  - `access_control_view` — GET renders current `AccessControl` flags; POST
    accepts a JSON body (`json.loads(request.body)`) of `{key: bool}` and
    updates each `AccessControl.is_active`.
  - `territory_upload` — accepts an uploaded `.xlsx`/`.xls`, writes it to a
    `NamedTemporaryFile`, calls `add_territories` management command with
    that path, then calls `create_users` to sync Django users, then deletes
    the temp file in a `finally`.
  - `download_gift_catalogs` / `download_anniverysary` /
    `download_boishakh_catalogs` — zip and stream uploaded doctor images.
- `dep_admin/utils.py` (560 lines) — one `filter_<module>_data(request)` per
  module: applies zone/region row-level scoping, `search` query param
  (icontains across dr_id/name/territory/region/zone/module field), and
  `sort`/`direction` query params, returning a queryset.

## Key types

- `AccessControl` (`access_control` table): `key` (matches the dict keys in
  `core.views.territory_home`), `is_active`. No FK — it's a flat feature-flag
  table seeded manually per campaign.

## Invariants / gotchas

- **Row-level scoping is duplicated per filter function**, not centralized:
  each `filter_*_data` repeats the same
  `try: profile = request.user.userprofile; if zone: ...; elif region: ...`
  `except UserProfile.DoesNotExist: if not superuser: return .none()`
  pattern. A superuser with no `UserProfile` still sees everything; a
  non-superuser with no `UserProfile` sees nothing.
- Pagination/search/sort query-param names (`search`, `page`, `per_page`,
  `sort`, `direction`) are conventioned across every list view but not
  shared via a helper — copy an existing `filter_*_data` function when
  adding a module rather than inventing new param names.
- `access_control_view` POST silently continues updating remaining keys
  after logging an error for one bad key (per-key `try/except` inside the
  loop), then reports success referencing only the **last** key processed —
  a partial-failure UX bug, not enforced correctness.
- `territory_upload` re-running `create_users` resets **every** territory
  user's password to the hardcoded default (`coralcal`) for newly created
  users only (existing users are left alone) — see
  [core-platform.md](core-platform.md).
- Image zip/download views assume the upload actually happened under
  `MEDIA_ROOT/<campaign>_images/...`; a record with a null image field will
  produce a missing-file error rather than being skipped (check each
  `download_*` view before reuse).
