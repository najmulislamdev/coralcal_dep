---
feature: doctor-profile-directory
owns:
  - doctors_data/
  - nfc_card_info/
last_verified: 8b9c0bee35f5f8e2e99d6b38922b20c1d575a5e8
---

## What it does

Two apps that capture reference/directory data about a doctor rather than a
campaign gift or engagement action:

- `doctors_data` (`dd/`) — a doctor's chamber directory: one `Doctor` with
  many `Chamber` rows (address, phone, division/district/upazila/thana,
  visiting days). Not territory-scoped for writes — anyone can submit
  (`dd_form` has no `@login_required`), reads/edits are.
- `nfc_card_info` (`nfc/`) — the info printed/encoded on a doctor's NFC
  business card (degree, specialty, institute, designation). Territory-
  scoped like the campaign apps, capped at 3 submissions per territory.

## Entry points

- `doctors_data/models.py` — `Doctor` (custom `id = BigIntegerField` primary
  key, i.e. the caller supplies the doctor's ID directly — no auto PK) with
  `Chamber` FK'd to it (`related_name='chambers'`).
- `doctors_data/views.py` — `dd_form` (create, **not** `@login_required**),
  `edit_doctors_data`, `delete_doctors_data`. Multi-chamber submission uses
  parallel `request.POST.getlist(...)` arrays (`chamber_address[]`,
  `chamber_phone[]`, etc.) zipped by index — the form's JS must keep these
  lists in lockstep or data misaligns silently.
- `doctors_data/templatetags/custom_tags.py` — `get_item` filter (dict
  lookup by key in templates), used to render the per-chamber
  `visiting_days` map back into the edit form.
- `nfc_card_info/models.py` — flat `NfcCardInfo`, `dr_rpl_id` unique.
- `nfc_card_info/views/` package (not a single `views.py`):
  `nfc_form.py` (create, capped at 3/territory), `nfc_history.py` (rep's own
  paginated/search/sort list), `nfc_edit.py`, `nfc_delete.py`.
- Admin-side list/export for both live in `dep_admin`
  (`doctors_data`/`doctors_data_export` in `dep_admin/views.py`,
  `nfc_admin_view`/`nfc_export` in `dep_admin/view/nfc_admin.py`) — see
  [admin-console.md](admin-console.md).

## Key types

- `Doctor.id` — `BigIntegerField(primary_key=True)`, expected to be the
  doctor's real-world RPL/ID number supplied by the form, not
  auto-incremented. Re-submitting the same `dr_id` will hit the model's
  natural PK collision (`IntegrityError`), not a friendly "already exists"
  message — `dd_form` does not pre-check for an existing `Doctor.id`.
- `Chamber.visiting_days` — stored as a single delimited string
  (`"Day:Time; Day:Time"` built client-side into `final_visiting_data`,
  split on `' || '` per chamber and then `';'`/`':'` per day) rather than a
  structured model — parsing lives in `edit_doctors_data`'s
  `visiting_map` reconstruction.
- `NfcCardInfo.created_at`/`updated_at` — **field names are swapped**
  relative to convention: `created_at = models.DateTimeField(auto_now=True)`
  and `updated_at = models.DateTimeField(auto_now_add=True)`. In this model
  `created_at` actually updates on every save and `updated_at` is the
  original creation time — the opposite of every other model in this
  codebase. Don't copy this file as a template for a new campaign.

## Invariants / gotchas

- `dd_form` (create) has no auth decorator while `edit_doctors_data`/
  `delete_doctors_data` do — the create endpoint is reachable by anyone who
  can POST to `dd/`, unlike every other campaign's submission form.
- Chamber phone validation in `dd_form` only enforces
  `startswith('01') and len == 11` — a Bangladesh mobile number shape, not
  validated for numeric-only content beyond that.
- `nfc_form_view`'s cap check reads `obj_count` from a variable set inside a
  `try/except Territory.DoesNotExist()` block — note `DoesNotExist()` is
  called (instantiated) rather than referenced as a class in the `except`
  clause, so it won't actually match Django's real `Territory.DoesNotExist`
  exception; if the territory lookup fails, `obj_count` is undefined and the
  cap check below raises `NameError` instead of showing the intended error
  message.
