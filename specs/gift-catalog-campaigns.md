---
feature: gift-catalog-campaigns
owns:
  - dr_gift_catalogs/
  - gift_catalogs_2/
  - gift_voucher_catalog/
  - dr_boishakh_catalog/
  - doctor_development/
last_verified: 8b9c0bee35f5f8e2e99d6b38922b20c1d575a5e8
---

## What it does

Five independent, near-duplicate Django apps, each a seasonal/quarterly
campaign where a territory rep picks one gift for one doctor from a fixed
catalog of images. Each app was copy-pasted from the previous one and then
diverged slightly (submission limit, `create` vs `update_or_create`,
extra fields). Treat them as **one feature with five instances**, not five
features — new campaigns get added by copying whichever existing app is
closest and re-registering URLs/`INSTALLED_APPS`/`AccessControl` key.

| App | URL prefix | Cap per territory | Write pattern | Extra per-submission data |
|---|---|---|---|---|
| `dr_gift_catalogs` | `gift/` | 2 (`gift_choiced` beyond) | `create` (multiple rows/territory) | `conference_image` upload when gift = conference registration |
| `gift_catalogs_2` | `gift_catalogs_2/` | 1 (`update_or_create` keyed on territory) | `update_or_create` | region-exclusivity check via `TERRITORY_LIST`/`REGION_LIST` in `constant.py` |
| `gift_voucher_catalog` | `gvc/` | 1 | `update_or_create` | `admin` username can submit on behalf of any territory via `?id=` |
| `dr_boishakh_catalog` | `boishakh-gift/` | 5 | `create` | `size` (T-shirt size) alongside gift; `gifts` stores comma-joined codes |
| `doctor_development` | `dd/` | 1 (`.get()` — errors if >1 row ever created) | `create` | none |

## Entry points

Each app follows the same shape (module-specific view names in parens):
- `<app>/models.py` — one model FK'd to `core.Territory`, `dr_id` (unique),
  `dr_name`, a `gift` `TextChoices` field with a fixed catalog baked into
  the model, `created_at`/`updated_at`.
- `<app>/views.py` (or `<app>/views/` package for `gift_catalogs_2` and
  `gift_voucher_catalog`) — a form view keyed by `request.user.username` as
  the territory code (`gift_choice`, `gift_catalogs_2026_form`,
  `gift_voucher_catalog_26_form`, `boishakh_choice`, `dd_gift_choice`), plus
  `edit_*`/`delete_*` where present.
- Corresponding read/export/delete views for superusers live in
  [admin-console.md](admin-console.md) (`dep_admin`), not here — these apps
  own only the submission form and per-territory "view what I submitted"
  page.
- `IMAGE_TO_GIFT` dict (front-end image key → catalog string) is duplicated
  per app instead of derived from the model's `TextChoices`; when adding a
  gift, update **both** the model choices and this dict or submissions will
  store `None` for the gift.

## Key types

- `DrGiftCatalog`, `GiftCatalog2`, `GiftVoucherCatalog`,
  `PohelaBoishakhCatalog`, `DoctorDevelopment` — structurally identical
  (territory FK, `dr_id` unique, `dr_name`, gift field, timestamps).
- `DrGiftCatalog.conference_image` / `OrthopedicDr.image` (see
  [doctor-engagement-campaigns.md](doctor-engagement-campaigns.md)) use a
  shared upload-path pattern: path is built from
  `zone/region/territory/dr_id-dr_name/...` looked up live from `Territory`
  at save time (`get_image_upload_path` closures, copy-pasted per app, not
  shared).

## Invariants / gotchas

- **`dr_id` is globally unique per model**, not unique per territory — two
  reps cannot both submit for the same doctor ID in the same campaign; the
  second attempt raises an `IntegrityError` that most of these views do not
  catch specifically (falls into the generic `except Exception` → generic
  error message).
- Submission caps are enforced only in the **form GET view** (redirect once
  count reached) — the POST handlers do not re-check the cap, so a
  double-submit race (two POSTs before the redirect) can exceed the stated
  cap.
- `gift_catalogs_2026_form` has bespoke region-exclusivity logic
  (`TERRITORY_LIST`/`REGION_LIST` in `gift_catalogs_2/constant.py`) not
  present in any sibling app — read that file before assuming the "one
  submission per territory" rule is uniform.
- `gift_voucher_catalog`'s `admin` bypass (`user == 'admin'` branch reading
  `?id=`) means the literal username string `"admin"` is treated specially
  in application code, separate from Django's `is_superuser` flag used
  everywhere else — don't rename that account.
- `doctor_development.dd_gift_choice` uses `.get()` (expects 0 or 1 row) but
  the POST path uses `.create()`, not `update_or_create` — if a territory
  race-submits twice, `.get()` on the next GET raises
  `MultipleObjectsReturned`, uncaught.
