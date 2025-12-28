# MyDoc AI Design System - Quick Start Guide

## 🎨 Your Custom Color Scheme

Your design system now uses your specified color palette:

- **Primary (Buttons, Highlights)**: Calm Blue `#2D9CDB`
- **Secondary (Chat bubbles, subtle UI)**: Light Sky Blue `#56CCF2`
- **Accent (Success, health tone)**: Healthy Green `#27AE60`
- **Background**: Soft White `#F8F9FA`
- **Text Main**: Deep Charcoal `#1A1A1A`
- **Text Subtle**: Medium Gray `#6B7280`

## 🚀 Quick Usage

### Import Components
```jsx
import { Button, Card, Modal, Icon, MedicalEmoji } from './components/ui';
```

### Buttons
```jsx
// Primary button with your custom blue
<Button variant="primary">Save Changes</Button>

// Medical-themed button
<Button variant="medical" icon="stethoscope">Analyze Symptoms</Button>

// Success button with your green accent
<Button variant="success" icon="check">Health Check Complete</Button>

// Different sizes
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>

// With loading state
<Button loading>Processing...</Button>
```

### Cards
```jsx
// Default card with glass effect
<Card>
  <h3>Patient Information</h3>
  <p>Medical details here...</p>
</Card>

// Medical-themed card
<Card medical>
  <h3>Vital Signs</h3>
  <p>Heart rate, blood pressure...</p>
</Card>

// Clickable card
<Card clickable onClick={handleClick}>
  <h3>Click me!</h3>
</Card>
```

### Icons
```jsx
// Medical icons
<Icon name="stethoscope" size={24} medical />
<Icon name="heart" size={20} animated />

// Medical emojis
<MedicalEmoji type="pill" size={32} animated />
<MedicalEmoji type="thermometer" size={24} />
```

### Modals
```jsx
<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Medical History"
  medical
  footer={
    <div className="flex gap-3">
      <Button variant="ghost" onClick={() => setIsOpen(false)}>
        Cancel
      </Button>
      <Button variant="medical">
        Save
      </Button>
    </div>
  }
>
  <p>Modal content here...</p>
</Modal>
```

## 🎨 Tailwind Classes

### Your Custom Colors
```jsx
// Primary colors (Calm Blue)
<div className="bg-primary-500 text-white">Primary</div>
<div className="text-primary-600">Primary text</div>

// Secondary colors (Light Sky Blue)
<div className="bg-secondary-400">Secondary</div>

// Accent colors (Healthy Green)
<div className="bg-accent-500">Success/Health</div>

// Background
<div className="bg-background-50">Soft white background</div>

// Text colors
<div className="text-textMain-900">Main text (Deep Charcoal)</div>
<div className="text-textSubtle-800">Subtle text (Medium Gray)</div>
```

### Glass Effects
```jsx
// Standard glass effect
<div className="glass p-6 rounded-2xl">Glass effect</div>

// Medical-themed glass
<div className="glass-medical p-6 rounded-2xl">Medical glass</div>

// Success-themed glass
<div className="glass-success p-6 rounded-2xl">Success glass</div>
```

### Gradient Text
```jsx
<h1 className="gradient-text text-4xl font-bold">MyDoc AI</h1>
<h2 className="gradient-text-success text-2xl">Health Success</h2>
```

### Animations
```jsx
// Medical-specific animations
<div className="animate-heartbeat">❤️</div>
<div className="animate-pulse-medical">Monitoring...</div>
<div className="animate-float">Floating element</div>
```

## 🔄 Migration from Old Components

### Old Button → New Button
```jsx
// Old way:
<button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
  Save
</button>

// New way:
<Button variant="primary">Save</Button>
```

### Old Modal → New Modal
```jsx
// Old way:
{isOpen && (
  <div className="fixed inset-0 bg-black/50 z-50">
    <div className="bg-white rounded-lg p-6 max-w-md mx-auto mt-20">
      <h2>Title</h2>
      <p>Content</p>
      <button onClick={onClose}>Close</button>
    </div>
  </div>
)}

// New way:
<Modal isOpen={isOpen} onClose={onClose} title="Title">
  <p>Content</p>
</Modal>
```

## 🧪 Testing Your Implementation

1. **View the Test Page**: Click "UI Test" in the header navigation to see all components in action
2. **Check Colors**: Verify your custom color scheme is applied correctly
3. **Test Responsiveness**: Components work on mobile, tablet, and desktop
4. **Accessibility**: All components include proper ARIA labels and keyboard navigation

## 📱 Mobile Considerations

All components include:
- Touch-friendly tap targets (minimum 44px)
- Responsive sizing
- Proper spacing for mobile devices
- Swipe gesture support where applicable

## 🎯 Best Practices

1. **Use Medical Styling**: Add `medical` prop to components in medical contexts
2. **Consistent Icons**: Use the centralized Icon component instead of importing icons directly
3. **Glass Effects**: Use glass effects for overlays and cards to maintain the modern aesthetic
4. **Color Consistency**: Stick to your defined color palette for brand consistency
5. **Accessibility**: Always include proper labels and keyboard navigation

## 🔧 Customization

To modify colors or add new variants:
1. Update `frontend/tailwind.config.js`
2. Modify `frontend/src/theme/colors.js`
3. Add new glass effects in `frontend/src/theme/glass.js`
4. Extend component variants as needed

Your design system is now ready to use! Start by gradually migrating existing components to use the new system for better consistency and maintainability.