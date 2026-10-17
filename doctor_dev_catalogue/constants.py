# Access Control key for this module; its entry_limit sets how many entries a
# territory may submit.
ACCESS_KEY = 'doctor_dev_catalogue'
DEFAULT_ENTRY_LIMIT = 1

# Selectable items in display order. Shawls (SL-*) come in one size, the rest
# need a size picked from SIZE_LABELS.
ITEMS = [
    {'code': 'SW-01', 'image': 'doctor_dev_catalogue/images/SW-01.jpeg', 'needs_size': True},
    {'code': 'SB-02', 'image': 'doctor_dev_catalogue/images/SB-02.jpeg', 'needs_size': True},
    {'code': 'SG-03', 'image': 'doctor_dev_catalogue/images/SG-03.jpeg', 'needs_size': True},
    {'code': 'SB-04', 'image': 'doctor_dev_catalogue/images/SB-04.jpeg', 'needs_size': True},
    {'code': 'SL-05', 'image': 'doctor_dev_catalogue/images/SL-05.jpeg', 'needs_size': False},
    {'code': 'SL-06', 'image': 'doctor_dev_catalogue/images/SL-06.jpeg', 'needs_size': False},
]
ITEMS_BY_CODE = {item['code']: item for item in ITEMS}

# Only the short code is stored, the label is what the MIO sees in the dropdown.
SIZE_LABELS = {
    'S': 'S - Chest:39 - Height:26',
    'M': 'M - Chest:41 - Height:27',
    'L': 'L - Chest:43 - Height:28',
    'XL': 'XL - Chest:45 - Height:29',
    'XXL': 'XXL - Chest:47 - Height:30',
}
