# Repair Tracker 2 - Frontend

Modern React 19 frontend for the repair tracker application.

## Modern Technology Stack

Built with the latest versions of modern web technologies:

- **React 19.2.0** - Latest React with improved performance and features
- **Vite 7.2.4** - Lightning-fast build tool and dev server
- **React Router 7.9.6** - Modern routing for React applications
- **Chart.js 4.5.1** - Modern charting library
- **date-fns 4.1.0** - Modern JavaScript date utility library

## Quick Start

### Install Dependencies
```bash
npm install
```

### Development Server
```bash
npm run dev
```
Runs on `http://localhost:5173` with hot module replacement.

The dev server automatically proxies:
- `/api/*` → `http://localhost:8000` (backend API)
- `/ws` → `ws://localhost:8000` (WebSocket)

### Build for Production
```bash
npm run build
```
Creates optimized static files in `dist/` ready for nginx deployment.

### Preview Production Build
```bash
npm run preview
```

## Project Structure

See [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) for detailed information about the project organization, development workflow, and deployment instructions.

## Key Features

- Real-time WebSocket updates
- Dark/light theme with CSS variables
- Barcode scanner support
- Chart.js visualizations + custom canvas charts
- Keyboard shortcuts (Ctrl+Shift, Ctrl+Click, etc.)
- Path aliases for clean imports (`@components`, `@hooks`, etc.)
- Optimized for static deployment to nginx

## Development

The project uses modern React 19 features and best practices. All dependencies are kept at their latest stable versions for security and performance.

For detailed component structure and implementation guidance, see `/_overview/TODO.txt` in the project root.
