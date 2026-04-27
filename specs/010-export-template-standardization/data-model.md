# Data Model: Export Assets & Metadata

## Asset Mapping
The following assets MUST be available in `backend/app/static/images/`:

- `new_civilization.png`: Left header logo.
- `rayon_energy.png`: Right header logo (currently `logo.png` in frontend).
- `stamp.png`: Footer circular stamp.

## Export Metadata (Dynamic Fields)
The `ExportService` will map incoming report data to the following template fields:

| Template Field | Report Source | Condition |
|----------------|---------------|-----------|
| **السيد (Mr.)** | `customer_name` | If present in data |
| **الموقع (Site)** | `site_location` / `address` | If present in data |
| **الهاتف (Phone)** | `phone` | If present in data |
| **العملية (Operation)** | `operation_type` / `category` | If present in data |

## Report Theme Constants
```python
BORDER_COLOR = colors.hexColor("#2F5597")  # Dark Blue
HEADER_BG_COLOR = colors.hexColor("#2F5597")  # Dark Blue
HEADER_TEXT_COLOR = colors.white
STRIPE_COLOR = colors.hexColor("#D9E1F2")  # Light Blue
```
