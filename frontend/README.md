# 🎨 MyDoc AI Frontend

Modern React.js frontend for MyDoc AI medical assistant application with beautiful UI/UX and smooth animations.

## 🏗️ Architecture

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Header.jsx       # Navigation header
│   │   ├── MainBox.jsx      # Main chat interface
│   │   ├── Sidebar.jsx      # Navigation sidebar
│   │   ├── ChatSettings.jsx # Settings modal
│   │   ├── Login.jsx        # Authentication
│   │   ├── Signup.jsx       # User registration
│   │   ├── SymptomChecker.jsx
│   │   ├── MedicalHistory.jsx
│   │   ├── DrugInteractions.jsx
│   │   ├── HealthTips.jsx
│   │   ├── HealthAnalyticsDashboard.jsx
│   │   ├── UserProfile.jsx
│   │   ├── LoadingSpinner.jsx
│   │   ├── ParticleBackground.jsx
│   │   └── ThemeProvider.jsx
│   ├── hooks/               # Custom React hooks
│   │   ├── useChat.js       # Chat functionality
│   │   ├── useApi.js        # API interactions
│   │   └── useAuthState.js  # Authentication state
│   ├── services/            # API services
│   │   └── api.js           # HTTP client
│   ├── utils/               # Utility functions
│   │   └── dataExport.js    # Data export utilities
│   ├── App.jsx              # Main application component
│   ├── main.jsx             # Application entry point
│   ├── index.css            # Global styles
│   └── App.css              # Component styles
├── public/                  # Static assets
├── dist/                    # Built application (generated)
├── package.json             # Dependencies and scripts
├── vite.config.js           # Vite configuration
├── tailwind.config.js       # Tailwind CSS configuration
├── postcss.config.js        # PostCSS configuration
└── .env.example             # Environment variables template
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- npm 8+

### Installation

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:5173`

## 📦 Dependencies

### Core Framework
- **React 18** - Modern UI library with concurrent features
- **Vite** - Fast build tool and development server
- **React DOM** - React rendering for web

### Styling & UI
- **Tailwind CSS** - Utility-first CSS framework
- **PostCSS** - CSS processing tool
- **Autoprefixer** - CSS vendor prefixing

### Animations & Interactions
- **Framer Motion** - Production-ready motion library
- **React Icons** - Popular icon library
- **React Markdown** - Markdown component for React

### Development Tools
- **ESLint** - JavaScript linting
- **Prettier** - Code formatting
- **@vitejs/plugin-react** - Vite React plugin

## ⚙️ Configuration

### Environment Variables (.env)

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Application Settings
VITE_APP_NAME=MyDoc AI
VITE_APP_VERSION=1.0.0
VITE_APP_DESCRIPTION=Intelligent Medical Assistant

# Feature Flags
VITE_ENABLE_VOICE=true
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_EXPORT=true

# Development Settings
VITE_DEBUG_MODE=false
VITE_MOCK_API=false
```

### Vite Configuration (vite.config.js)

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    open: true
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          animations: ['framer-motion'],
          icons: ['react-icons']
        }
      }
    }
  }
})
```

### Tailwind Configuration (tailwind.config.js)

```javascript
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
      },
      colors: {
        primary: {
          // Blue color palette
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        secondary: {
          // Gray color palette
          50: '#f8fafc',
          500: '#64748b',
          800: '#1e293b',
          900: '#0f172a',
        }
      },
      animation: {
        'float': 'float 3s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite',
        'shimmer': 'shimmer 1.5s infinite',
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
```

## 🎨 Design System

### Color Palette
- **Primary Blue**: `#3b82f6` - Main brand color
- **Secondary Gray**: `#64748b` - Supporting elements
- **Dark Gray**: `#1e293b` - Text and backgrounds
- **Light Gray**: `#f8fafc` - Subtle backgrounds

### Typography
- **Font Family**: Inter (Google Fonts)
- **Font Weights**: 300, 400, 500, 600, 700
- **Font Sizes**: Responsive scale using Tailwind classes

### Spacing & Layout
- **Border Radius**: Consistent 2xl (16px) for modern look
- **Spacing**: 8px grid system using Tailwind spacing
- **Breakpoints**: Mobile-first responsive design

### Animations
- **Duration**: 200-300ms for micro-interactions
- **Easing**: Cubic bezier curves for natural motion
- **Performance**: GPU-accelerated transforms

## 🧩 Component Architecture

### Core Components

#### App.jsx
Main application component handling:
- Route management
- Global state
- Theme provider
- Layout structure

#### Header.jsx
Navigation header featuring:
- Logo and branding
- Navigation menu
- Theme toggle
- User profile access

#### MainBox.jsx
Primary chat interface with:
- Message display
- Input handling
- Voice integration
- Quick suggestions

#### Sidebar.jsx
Navigation sidebar containing:
- Feature access
- User profile
- Settings
- Mobile-responsive design

### Feature Components

#### SymptomChecker.jsx
Symptom analysis tool with:
- Text input for symptoms
- AI-powered analysis
- Results display
- Medical disclaimers

#### MedicalHistory.jsx
Health record management:
- Record creation/editing
- History display
- Data organization
- Export functionality

#### HealthAnalyticsDashboard.jsx
Health data visualization:
- Statistics cards
- Charts and graphs
- Trend analysis
- Insights generation

### Utility Components

#### LoadingSpinner.jsx
Reusable loading indicator:
- Multiple sizes
- Customizable text
- Smooth animations
- Theme-aware colors

#### ParticleBackground.jsx
Animated background effects:
- Floating particles
- Performance optimized
- Theme integration
- Configurable density

## 🎯 Custom Hooks

### useChat.js
Chat functionality management:
```javascript
const {
  messages,
  input,
  setInput,
  isTyping,
  isListening,
  voiceEnabled,
  handleSend,
  startListening,
  stopListening,
  clearChat
} = useChat();
```

### useApi.js
API interaction utilities:
```javascript
const {
  get,
  post,
  put,
  delete: del,
  loading,
  error
} = useApi();
```

### useAuthState.js
Authentication state management:
```javascript
const {
  user,
  isAuthenticated,
  login,
  logout,
  loading
} = useAuthState();
```

## 🎬 Animation System

### Framer Motion Integration
- **Page transitions**: Smooth route changes
- **Component animations**: Enter/exit animations
- **Micro-interactions**: Button hovers and clicks
- **Loading states**: Skeleton screens and spinners

### Animation Patterns
```javascript
// Fade in animation
const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.3 }
};

// Stagger children
const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
};
```

## 🌙 Theme System

### Dark/Light Mode
- **System preference detection**
- **Manual toggle option**
- **Persistent user choice**
- **Smooth transitions**

### Theme Provider
```javascript
const { darkMode, toggleTheme, isTransitioning } = useTheme();
```

### CSS Variables
```css
:root {
  --gradient-primary: linear-gradient(135deg, #1e40af 0%, #1f2937 100%);
  --gradient-secondary: linear-gradient(135deg, #3b82f6 0%, #374151 100%);
  --glass-light: rgba(255, 255, 255, 0.1);
  --glass-dark: rgba(0, 0, 0, 0.2);
}
```

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Mobile Optimizations
- **Touch targets**: Minimum 44px
- **Gesture support**: Swipe interactions
- **Viewport handling**: Proper mobile scaling
- **Performance**: Optimized for mobile devices

## 🔧 Development

### Available Scripts

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Format code
npm run format

# Type checking
npm run type-check
```

### Code Style
- **ESLint**: JavaScript/React linting
- **Prettier**: Code formatting
- **Consistent naming**: camelCase for variables, PascalCase for components

### File Organization
```
src/
├── components/
│   ├── common/          # Reusable components
│   ├── features/        # Feature-specific components
│   └── layout/          # Layout components
├── hooks/               # Custom hooks
├── services/            # API services
├── utils/               # Utility functions
├── styles/              # Global styles
└── types/               # TypeScript types (if using TS)
```

## 🧪 Testing

### Testing Setup
```bash
# Install testing dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest

# Run tests
npm run test

# Run tests with coverage
npm run test:coverage
```

### Test Structure
```
src/
├── __tests__/           # Test files
│   ├── components/      # Component tests
│   ├── hooks/           # Hook tests
│   └── utils/           # Utility tests
└── setupTests.js        # Test configuration
```

## 🚀 Build & Deployment

### Production Build
```bash
npm run build
```

### Build Optimization
- **Code splitting**: Automatic chunk splitting
- **Tree shaking**: Remove unused code
- **Asset optimization**: Image and CSS optimization
- **Compression**: Gzip compression ready

### Deployment Options

#### Static Hosting (Netlify, Vercel)
```bash
npm run build
# Deploy dist/ folder
```

#### Docker
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🔍 Performance Optimization

### Bundle Analysis
```bash
npm run build -- --analyze
```

### Performance Tips
- **Lazy loading**: Route-based code splitting
- **Memoization**: React.memo for expensive components
- **Virtual scrolling**: For large lists
- **Image optimization**: WebP format and lazy loading

### Lighthouse Scores
- **Performance**: 90+
- **Accessibility**: 95+
- **Best Practices**: 90+
- **SEO**: 85+

## 🐛 Troubleshooting

### Common Issues

#### Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Styling Issues
```bash
# Rebuild Tailwind CSS
npm run build:css
```

#### Hot Reload Not Working
```bash
# Restart development server
npm run dev
```

### Performance Issues
- Check browser dev tools for console errors
- Monitor network requests in dev tools
- Use React DevTools Profiler
- Analyze bundle size with webpack-bundle-analyzer

## 📚 Resources

### Documentation
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Framer Motion Documentation](https://www.framer.com/motion/)

### Tools
- [React DevTools](https://chrome.google.com/webstore/detail/react-developer-tools/)
- [Tailwind CSS IntelliSense](https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss)
- [ES7+ React/Redux/React-Native snippets](https://marketplace.visualstudio.com/items?itemName=dsznajder.es7-react-js-snippets)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Ensure all tests pass
6. Submit a pull request

### Code Standards
- Follow React best practices
- Use functional components with hooks
- Implement proper error boundaries
- Add PropTypes or TypeScript types
- Write meaningful commit messages

---

**Frontend ready! 🎨 Beautiful, responsive, and performant medical AI interface.**