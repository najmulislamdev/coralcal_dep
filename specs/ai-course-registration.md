---
feature: ai-course-registration
owns:
  - doctors_ai_course/
  - doctors_ai_course2/
last_verified: 8b9c0bee35f5f8e2e99d6b38922b20c1d575a5e8
---

## What it does

Two sequential cohorts of the same "AI for Doctors" course, registering one
or two doctors per territory (name, RPL ID, specialty, designation — no
gift, no image). `doctors_ai_course` ("old") is the closed first cohort;
`doctors_ai_course2` ("current", URL/label "AI for Doctors" without "Old")
is the active one reps are pointed to by `core.views.territory_home`.

## Entry points

- `doctors_ai_course/models.py` — `DoctorAiCourse.territory` is a
  **`OneToOneField`** to `Territory`: exactly one registration per territory,
  ever.
- `doctors_ai_course2/models.py` — `DoctorAiCourseUp.territory` is a plain
  **`ForeignKey`**: multiple registrations per territory allowed.
- `doctors_ai_course/urls.py` (`dac/`) → `views.py`: `dac_form` (GET renders
  the single existing registration if any, POST does
  `update_or_create(territory=...)` — editing in place, never creating a
  second row), `edit_dac_form` (superuser-only, targets a `?territory=` from
  the query string), `delete_dac`, `export_dac`.
- `doctors_ai_course2/urls.py` (`dac2/`) → `views.py`: `dac_form` (same
  update-style POST, but gated by `doctor.count() >= 2` → redirect to
  `dac2_history` instead of update_or_create bailing out at 1), plus its own
  `dac2_history`, `edit_dac_form`, `dac2_delete` — a rep-facing history page
  that v1 doesn't have (v1's cap of 1 makes a history list moot).
- Admin views: `dep_admin.views.doctors_ai_course` /
  `doctors_ai_course2` list both cohorts; `export_dac`/`export_wishlist`-
  style Excel export is done per-app here rather than centrally, but list
  filtering (`utils.filter_doctor_ai_course_data(request, model=1|2)`) is
  shared in `dep_admin/utils.py` — a `model` GET param picks which cohort's
  table to query. See [admin-console.md](admin-console.md).

## Key types

- `DoctorAiCourse` (`doctors_ai_course` table): `territory` (O2O, unique),
  `name`, `rpl_id`, `specialty`, `designation`.
- `DoctorAiCourseUp` (`doctors_ai_course_up` table): identical fields,
  `territory` is a `ForeignKey` (not unique) — this is the only structural
  difference between the two models.

## Invariants / gotchas

- Because v1's FK is `OneToOneField` but the POST handler uses
  `update_or_create`, a v1 "registration" is really a mutable single record
  per territory — there is no history of who was registered before an edit
  overwrote it. v2 intentionally moved to a plain FK specifically to allow
  a second doctor and keep both, so don't "fix" v2 by copying v1's O2O
  field.
- `dep_admin.utils.filter_doctor_ai_course_data(request, model=2)` defaults
  to the v2 (`DoctorAiCourseUp`) table — passing `model=1` is required to
  reach the old cohort; a caller that forgets the `model` kwarg silently
  gets v2 data.
- `edit_dac_form` in both apps trusts `request.GET.get('territory')` to pick
  which record to edit and only checks `request.user.is_superuser`, not
  whether that user's `UserProfile` scope (zone/region) actually covers the
  target territory — a zone/region reviewer with `is_superuser=False` is
  blocked entirely from editing (redirected to `home`), which is likely
  stricter than intended rather than a security gap.
