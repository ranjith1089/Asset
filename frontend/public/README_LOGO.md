# Logo Setup Instructions

Please add your logo file to this directory (`frontend/public/`).

## Supported Formats
- PNG (recommended)
- SVG (recommended for scalability)
- JPG/JPEG

## Recommended File Name
- `logo.png` (preferred)
- `logo.svg`
- `logo.jpg`

## Recommended Size
- For header/login: 200x60px or similar aspect ratio
- Width should be 2-3x the height for best appearance

## Steps
1. Place your logo file in this `frontend/public/` directory
2. Name it `logo.png` (or update the image src in the components if using a different name)
3. The logo will automatically appear on:
   - Login page (centered at top)
   - Header (left side)
   - Dashboard landing page (top left)

The application will gracefully handle if the logo is not found (it will just hide the image element).


