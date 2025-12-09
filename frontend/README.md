# Document Understanding - Frontend

Beautiful React chat interface for Document Understanding API.

## Features

- 🎨 Modern, gradient-based UI with Tailwind CSS
- 💬 Real-time chat interface
- 🧠 Thinking indicator showing AI processing steps
- 📚 Collapsible sources panel to view retrieved document chunks
- 🤖 Switch between Qwen (local) and Gemini (API) models
- ⚡ Smooth animations and transitions
- 📱 Fully responsive design

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **React Markdown** - Markdown rendering

## Installation

```bash
cd frontend
npm install
```

## Development

```bash
npm run dev
```

Frontend will run at http://localhost:3000

Backend API should be running at http://localhost:1201

## Build for Production

```bash
npm run build
```

Build output will be in `dist/` directory.

## Preview Production Build

```bash
npm run preview
```

## UI Components

### Header
- App branding with gradient background
- Online status indicator

### ChatContainer
- Main chat interface
- Message list with auto-scroll
- Input area with LLM provider selector
- Clear history button

### MessageBubble
- User messages (right-aligned, dark theme)
- Assistant messages (left-aligned, light theme)
- Error messages (red theme)
- Markdown support for AI responses
- Timestamp display

### ThinkingIndicator
- Animated loading state
- Shows AI processing steps:
  - Searching documents
  - Analyzing information
  - Generating answer
- Progress bar animation

### SourcesPanel
- Collapsible panel showing retrieved document chunks
- Displays filename, page number, and content preview
- Beautiful gradient cards
- Smooth expand/collapse animation

## Customization

### Colors

Edit `tailwind.config.js` to customize color scheme:

```js
colors: {
  primary: { ... },   // Main brand color
  secondary: { ... }, // Accent color
}
```

### Animations

Modify animations in `tailwind.config.js`:

```js
animation: {
  'gradient': 'gradient 8s linear infinite',
  'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
}
```

## API Integration

API service is in `src/services/api.js`:

```js
// Change API base URL if needed
const API_BASE_URL = '/api/v1';
```

Proxy is configured in `vite.config.js` to forward `/api` requests to backend.

## Screenshots

(Add screenshots here)

## License

MIT
