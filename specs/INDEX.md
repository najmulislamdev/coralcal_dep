# Specs Index

CoralCal is a Django 5 project (`coralcal_dep`) used by a pharma company to run
territory-rep-driven doctor engagement campaigns: reps ("MIOs") log in with a
territory code and submit gift/engagement/registration forms on behalf of
doctors; superusers/zone/region users review and export the data via a shared
admin console.

| Spec | What it covers | Owns |
|---|---|---|
| [core-platform.md](core-platform.md) | Auth, Territory/UserProfile models, access-control-gated rep dashboard, management commands, base template dir | `core/`, `coralcal_dep/` |
| [admin-console.md](admin-console.md) | Superadmin/zone/region views: list, search, sort, export-to-Excel, delete for every campaign module; AccessControl toggles | `dep_admin/` |
| [gift-catalog-campaigns.md](gift-catalog-campaigns.md) | Near-identical "doctor picks a gift" campaigns, one dr_id submission (or 2/3) per territory per campaign | `dr_gift_catalogs/`, `gift_catalogs_2/`, `gift_voucher_catalog/`, `dr_boishakh_catalog/`, `doctor_development/` |
| [doctor-engagement-campaigns.md](doctor-engagement-campaigns.md) | One-off doctor engagement forms not centered on gift selection (book wish, anniversary photo, plants, opinion/testimonial, orthopedic photo) | `knowledge_series/`, `anniversary/`, `green_corner/`, `plant_module/`, `doctors_opinion/`, `orthopedic_dr_dev/` |
| [doctor-profile-directory.md](doctor-profile-directory.md) | Structured doctor reference data: chamber directory and NFC digital-card info | `doctors_data/`, `nfc_card_info/` |
| [ai-course-registration.md](ai-course-registration.md) | One-doctor-per-territory AI course registration (old + current cohort) | `doctors_ai_course/`, `doctors_ai_course2/` |

Not covered by a dedicated spec: `helpers/` (a single `download_to_local`
utility used by `vendor_pull`) and root `static/` (collected/vendor static
assets) — both are plumbing with no independent behavior to document.
