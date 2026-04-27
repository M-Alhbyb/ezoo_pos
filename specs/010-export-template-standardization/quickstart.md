# Quickstart: Testing Standardized Exports

## 1. Asset Setup
Ensure the images are copied to the backend:
```bash
mkdir -p backend/app/static/images
cp frontend/public/new_civilization.png backend/app/static/images/
cp frontend/public/logo.png backend/app/static/images/rayon_energy.png
cp frontend/public/stamp.png backend/app/static/images/
```

## 2. Generate Test Report
Navigate to the Sales Report page in the UI and click **Export PDF**.

## 3. Verification Checklist
- [ ] **Header**: "New Civilization" logo on the left, "Rayon Energy" on the right.
- [ ] **Title**: Centered report title (e.g., Sales Report).
- [ ] **Table**: Blue borders, dark blue header row, light blue alternating row colors.
- [ ] **Arabic**: Text is correctly reshaped and aligned.
- [ ] **Footer**: Stamp is visible on the last page near the "Signature" placeholder.

## 4. Excel Verification
- [ ] Open the exported `.xlsx` file.
- [ ] Logos are visible in the top rows.
- [ ] Data table starts below the header (Row 7+).
- [ ] Columns are sortable and filters work correctly.
