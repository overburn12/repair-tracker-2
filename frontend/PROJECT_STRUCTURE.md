# Repair Tracker 2 - Frontend Project Structure

## Technology Stack

- **Framework**: React 18
- **Build Tool**: Vite
- **Routing**: React Router v6
- **Charts**: Chart.js + React-Chartjs-2 + custom canvas charts
- **WebSocket**: Native WebSocket API
- **State Management**: React Context API
- **Styling**: CSS with CSS Variables for theming

## Project Structure

```
frontend/
├── public/                 # Static assets served as-is
├── src/
│   ├── components/         # Reusable React components
│   │   ├── layout/         # Layout components (App, Layout, Navbar)
│   │   ├── modals/         # Modal components (WorkbookModal)
│   │   ├── search/         # Search-related components
│   │   ├── ui/             # Shared UI components (buttons, inputs, etc.)
│   │   ├── tables/         # Table components
│   │   └── charts/         # Chart components
│   ├── pages/              # Page components (one per route)
│   ├── hooks/              # Custom React hooks
│   ├── utils/              # Utility functions
│   ├── services/           # API service layer
│   ├── context/            # React context providers
│   ├── styles/             # Global styles and CSS
│   ├── assets/             # Static assets (images, fonts, etc.)
│   ├── App.jsx             # Root component
│   └── main.jsx            # Entry point
├── vite.config.js          # Vite configuration
├── package.json            # Dependencies
└── README.md               # Project documentation
```

## Development

### Prerequisites
- Node.js v18+ (v20+ recommended)
- npm v10+

### Setup
```bash
npm install
```

### Development Server
```bash
npm run dev
```
Runs on `http://localhost:5173` with hot module replacement.

### Build for Production
```bash
npm run build
```
Builds static files to `dist/` directory for nginx deployment.

### Preview Production Build
```bash
npm run preview
```

## Key Features

### Path Aliases
Configured in `vite.config.js` for cleaner imports:
- `@` → `src/`
- `@components` → `src/components/`
- `@pages` → `src/pages/`
- `@hooks` → `src/hooks/`
- `@utils` → `src/utils/`
- `@services` → `src/services/`
- `@context` → `src/context/`
- `@styles` → `src/styles/`
- `@assets` → `src/assets/`

Example:
```javascript
import { useWebSocket } from '@hooks/useWebSocket';
import Button from '@components/ui/Button';
```

### Development Proxy
API requests to `/api/*` and WebSocket connections to `/ws` are proxied to `http://localhost:8000` during development.

### WebSocket Integration
- Native WebSocket API
- Automatic reconnection handling
- Channel-based subscriptions (main:*, order:*)
- Real-time updates for orders and units

### Theming
- Dark theme (default)
- Light theme
- CSS Variables for all colors
- Theme persistence in localStorage
- Smooth transitions on theme change

### Keyboard Shortcuts
- **Ctrl+Shift**: Show delete buttons
- **Ctrl+Click**: Add to workbook
- **Shift+Enter**: Submit comment (repair unit page)
- **Ctrl+Enter**: Submit repair (repair unit page)
- **Escape**: Cancel inline edit

### Barcode Scanner Support
Input fields detect rapid input (10+ chars in <500ms) and auto-submit for barcode scanner compatibility.

## Deployment

### Static File Deployment to Nginx

1. Build the project:
```bash
npm run build
```

2. The `dist/` directory contains all static files ready for deployment.

3. Nginx configuration example:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/dist;
    index index.html;

    # Serve static files
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Proxy WebSocket connections
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Next Steps

1. Copy CSS styles from `_old_pages/base.html` to `src/styles/index.css`
2. Implement core layout components (Layout, Navbar)
3. Set up React Router with all routes
4. Implement WebSocket hook and context
5. Build page components one by one, starting with simple pages
6. Implement API service layer
7. Add Chart.js integration
8. Implement custom canvas charts
9. Add authentication flow
10. Test and polish

## Reference

Original Flask/Jinja2 frontend is in `/_old_pages/` for reference during conversion.
Detailed component analysis is in `/_overview/TODO.txt`.
