---
feature: doctor-engagement-campaigns
owns:
  - knowledge_series/
  - anniversary/
  - green_corner/
  - plant_module/
  - doctors_opinion/
  - orthopedic_dr_dev/
last_verified: 8b9c0bee35f5f8e2e99d6b38922b20c1d575a5e8
---

## What it does

Six one-off doctor engagement forms that share the same
"rep logs in as their territory, fills a form about one doctor" shape as
[gift-catalog-campaigns.md](gift-catalog-campaigns.md) but aren't a gift
picker — each collects different structured data:

| App | URL prefix | Collects | Cap per territory |
|---|---|---|---|
| `knowledge_series` | `ks` | book choice (`BookWishes`) | 1 (`.get()`) |
| `anniversary` | `anniversary/` | doctor photo + anniversary date (`Anniversary`) | unbounded, list view |
| `green_corner` | `rgc/` | 3 flower + 2 medicinal plant picks (`GreenCorner`) | 1 (`dr_id` unique) |
| `plant_module` | `plant/` | free-text plant pick + specialty/designation/location (`PlantModule`) | 1 (`dr_id` unique) |
| `doctors_opinion` | `doctors_opinion/` | doctor contact info + N free-text "indications" (`DoctorOpinion` + `DoctorIndication`) | unbounded, list view |
| `orthopedic_dr_dev` | `odd/` | one doctor photo, editable in place (`OrthopedicDr`) | exactly 1, always edited not re-created |

## Entry points

- Each app: `models.py` (FK to `core.Territory`), `views.py` (form +
  `edit_*`/`delete_*`/`*_history` as applicable), `urls.py`, `templates/`.
- `doctors_opinion` is the only one with a real child table:
  `DoctorIndication` (FK `doctor_opinion`) — one row per free-text
  indication string; `do_edit_view` fully replaces indications on every edit
  (`obj.indications.all().delete()` then re-create).
- `orthopedic_dr_dev/views.py` — the odd one out: `anniversary(request, pk=None)`
  (unfortunate name clash with the *other* `anniversary` app — same function
  name, different app, not shared code) either creates the rep's single
  entry or edits it in place, and handles keeping the on-disk image path in
  sync when `dr_id`/`dr_name` change without a new upload
  (`move_image_to_current_path`), since the upload path is derived from
  those fields.
- Admin-side list/search/export views for all six live in `dep_admin` — see
  [admin-console.md](admin-console.md).

## Key types

- `BookWishes`, `GreenCorner`, `PlantModule` — flat models, `dr_id` unique,
  free-text or `TextChoices` payload field(s).
- `Anniversary`, `OrthopedicDr` — add an `ImageField` using the same
  `zone/region/territory/dr_id-dr_name/...` upload-path pattern described in
  [gift-catalog-campaigns.md](gift-catalog-campaigns.md); `OrthopedicDr` additionally
  uses a custom `OverwriteStorage` (deletes any existing file at the target
  path instead of suffixing a new name) so re-uploads replace in place.
- `DoctorOpinion` + `DoctorIndication` — the only 1:N model pair in this
  group.

## Invariants / gotchas

- **Cap enforcement is inconsistent and mostly cosmetic**, same caveat as
  gift-catalog-campaigns: `knowledge_series.book_choice` uses `.get()`
  assuming ≤1 row, but `.create()` on POST — concurrent submissions raise
  `MultipleObjectsReturned` on the next GET, uncaught.
- `green_corner.rgc_form`'s validation-failure branch calls
  `redirect('rgc_upload')` without `return`, so on a validation error it
  logs the message *and* falls through to attempt the `try` block anyway
  with missing fields — check this before trusting "all fields required"
  actually blocks the save.
- `orthopedic_dr_dev.anniversary` is reused for both the rep's own form
  (`pk=None`, territory from `request.user.username`) and the admin's
  per-record edit (`pk` from URL, territory from the fetched object) — the
  same view function serves two different callers with different identity
  sources; `redirect_target(pk)` is what tells them apart on redirect.
- Image-owning models (`Anniversary`, `OrthopedicDr`) build their upload
  folder from a **live** `Territory.objects.get(...)` lookup inside the
  `upload_to` callable — if the territory's zone/region name changes after
  upload, old files stay under the old zone/region path and are not moved
  (only `orthopedic_dr_dev` bothers to re-home a file, and only when
  `dr_id`/`dr_name` change, not zone/region).
- Folder-delete safety checks (`os.path.commonpath` against
  `MEDIA_ROOT/<campaign>_images`) are copy-pasted per app in `anniversary`
  and `orthopedic_dr_dev`'s `delete_*` views — not shared, so a future
  campaign's delete view needs the same guard written again by hand.
