# Urban Pulse Website

A modern, navigable website for construction and real estate intelligence, built to match Lovable's design standards.

## Features

- **Modern Design**: Clean, professional interface with gradient backgrounds and smooth animations
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile devices
- **Theme-Based Navigation**: Four main categories (Opportunities, Practices, Systems & Codes, Vision)
- **Real-time Data**: Fetches live articles from the V3 API
- **Interactive Cards**: Hover effects and smooth transitions
- **Loading States**: Professional loading spinners and error handling

## Design Elements

### Color Scheme
- **Primary Gradient**: Blue to Purple (`#667eea` to `#764ba2`)
- **Opportunities**: Blue gradient (`#4facfe` to `#00f2fe`)
- **Practices**: Green gradient (`#43e97b` to `#38f9d7`)
- **Systems**: Pink to Yellow (`#fa709a` to `#fee140`)
- **Vision**: Teal to Pink (`#a8edea` to `#fed6e3`)

### Typography
- **Font**: System fonts (San Francisco, Segoe UI, Roboto)
- **Headings**: Bold weights with proper hierarchy
- **Body Text**: Optimized line height for readability

### Layout
- **Grid System**: CSS Grid for responsive layouts
- **Card Design**: Rounded corners with subtle shadows
- **Spacing**: Consistent padding and margins
- **Navigation**: Sticky header with smooth scrolling

## Running the Website

### Option 1: Simple Python Server
```bash
cd website
python3 server.py
```
Then visit: http://localhost:8080

### Option 2: Any Web Server
Simply serve the `index.html` file from any web server.

## API Integration

The website connects to the V3 API endpoints:
- `https://newsletter-api-v3-clean.onrender.com/api/v3/opportunities`
- `https://newsletter-api-v3-clean.onrender.com/api/v3/practices`
- `https://newsletter-api-v3-clean.onrender.com/api/v3/systems`
- `https://newsletter-api-v3-clean.onrender.com/api/v3/vision`

## Structure

```
website/
├── index.html          # Main website file
├── server.py           # Simple Python HTTP server
└── README.md          # This file
```

## Customization

To modify the design:
1. Edit the CSS in the `<style>` section of `index.html`
2. Update the `THEMES` configuration in the JavaScript
3. Modify the API endpoints in the `API_BASE` variable

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+
