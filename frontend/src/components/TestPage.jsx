import { useState } from 'react';
import { Button, Card, Modal, Icon, MedicalEmoji } from './ui';

const TestPage = () => {
  const [modalOpen, setModalOpen] = useState(false);
  
  return (
    <div className="min-h-screen bg-background-50 p-8 space-y-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold gradient-text mb-2">UI Component Test Page</h1>
        <p className="text-textSubtle-800 mb-8">Testing the new design system with your custom color scheme</p>
        
        {/* Color Palette Display */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-textMain-900 mb-6">Color Palette</h2>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <Card className="text-center">
              <div className="w-16 h-16 bg-primary-500 rounded-xl mx-auto mb-3"></div>
              <h3 className="font-semibold text-textMain-900">Primary</h3>
              <p className="text-textSubtle-800 text-sm">#2D9CDB</p>
            </Card>
            <Card className="text-center">
              <div className="w-16 h-16 bg-secondary-400 rounded-xl mx-auto mb-3"></div>
              <h3 className="font-semibold text-textMain-900">Secondary</h3>
              <p className="text-textSubtle-800 text-sm">#56CCF2</p>
            </Card>
            <Card className="text-center">
              <div className="w-16 h-16 bg-accent-500 rounded-xl mx-auto mb-3"></div>
              <h3 className="font-semibold text-textMain-900">Accent</h3>
              <p className="text-textSubtle-800 text-sm">#27AE60</p>
            </Card>
            <Card className="text-center">
              <div className="w-16 h-16 bg-background-50 border-2 border-background-200 rounded-xl mx-auto mb-3"></div>
              <h3 className="font-semibold text-textMain-900">Background</h3>
              <p className="text-textSubtle-800 text-sm">#F8F9FA</p>
            </Card>
            <Card className="text-center">
              <div className="w-16 h-16 bg-textMain-900 rounded-xl mx-auto mb-3"></div>
              <h3 className="font-semibold text-textMain-900">Text Main</h3>
              <p className="text-textSubtle-800 text-sm">#1A1A1A</p>
            </Card>
          </div>
        </section>

        {/* Buttons */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-textMain-900 mb-6">Buttons</h2>
          <div className="space-y-4">
            <div className="flex flex-wrap gap-4">
              <Button variant="primary">Primary Button</Button>
              <Button variant="medical" icon="stethoscope">Medical Button</Button>
              <Button variant="success" icon="check">Success Button</Button>
              <Button variant="warning" icon="alert">Warning Button</Button>
              <Button variant="error" icon="error">Error Button</Button>
            </div>
            <div className="flex flex-wrap gap-4">
              <Button variant="secondary">Secondary</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="outline">Outline</Button>
              <Button loading>Loading</Button>
              <Button disabled>Disabled</Button>
            </div>
            <div className="flex flex-wrap gap-4">
              <Button size="xs">Extra Small</Button>
              <Button size="sm">Small</Button>
              <Button size="md">Medium</Button>
              <Button size="lg">Large</Button>
              <Button size="xl">Extra Large</Button>
            </div>
          </div>
        </section>
        
        {/* Icons */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-textMain-900 mb-6">Icons</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="text-center">
              <Icon name="stethoscope" size={32} medical className="mx-auto mb-2" />
              <p className="text-sm text-textSubtle-800">Medical Icons</p>
            </Card>
            <Card className="text-center">
              <Icon name="heart" size={32} animated className="mx-auto mb-2 text-error-500" />
              <p className="text-sm text-textSubtle-800">Animated Icons</p>
            </Card>
            <Card className="text-center">
              <MedicalEmoji type="pill" size={32} animated className="mx-auto mb-2" />
              <p className="text-sm text-textSubtle-800">Medical Emojis</p>
            </Card>
            <Card className="text-center">
              <div className="flex justify-center gap-2 mb-2">
                <Icon name="home" size={24} />
                <Icon name="settings" size={24} />
                <Icon name="user" size={24} />
              </div>
              <p className="text-sm text-textSubtle-800">UI Icons</p>
            </Card>
          </div>
        </section>
        
        {/* Cards */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-textMain-900 mb-6">Cards</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <div className="flex items-center gap-3 mb-4">
                <Icon name="activity" size={24} className="text-primary-500" />
                <h3 className="font-semibold text-textMain-900">Default Card</h3>
              </div>
              <p className="text-textSubtle-800">This is a default card with glass effect and your custom colors.</p>
            </Card>
            <Card medical>
              <div className="flex items-center gap-3 mb-4">
                <MedicalEmoji type="stethoscope" size={24} />
                <h3 className="font-semibold text-textMain-900">Medical Card</h3>
              </div>
              <p className="text-textSubtle-800">This is a medical-themed card with enhanced styling.</p>
            </Card>
            <Card variant="success">
              <div className="flex items-center gap-3 mb-4">
                <Icon name="checkCircle" size={24} className="text-success-600" />
                <h3 className="font-semibold text-textMain-900">Success Card</h3>
              </div>
              <p className="text-textSubtle-800">This is a success-themed card with green accents.</p>
            </Card>
          </div>
        </section>

        {/* Glass Effects */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-textMain-900 mb-6">Glass Effects</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="glass p-6 rounded-2xl text-center">
              <h3 className="font-semibold text-textMain-900 mb-2">Default Glass</h3>
              <p className="text-textSubtle-800 text-sm">Standard glass effect</p>
            </div>
            <div className="glass-medical p-6 rounded-2xl text-center">
              <h3 className="font-semibold text-textMain-900 mb-2">Medical Glass</h3>
              <p className="text-textSubtle-800 text-sm">Medical themed glass</p>
            </div>
            <div className="glass-success p-6 rounded-2xl text-center">
              <h3 className="font-semibold text-textMain-900 mb-2">Success Glass</h3>
              <p className="text-textSubtle-800 text-sm">Success themed glass</p>
            </div>
            <div className="glass-warning p-6 rounded-2xl text-center">
              <h3 className="font-semibold text-textMain-900 mb-2">Warning Glass</h3>
              <p className="text-textSubtle-800 text-sm">Warning themed glass</p>
            </div>
          </div>
        </section>

        {/* Gradient Text */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-textMain-900 mb-6">Gradient Text</h2>
          <div className="space-y-4">
            <h3 className="text-3xl font-bold gradient-text">MyDoc AI - Primary Gradient</h3>
            <h3 className="text-3xl font-bold gradient-text-success">Health Success - Green Gradient</h3>
            <h3 className="text-3xl font-bold gradient-text-warning">Warning Alert - Orange Gradient</h3>
            <h3 className="text-3xl font-bold gradient-text-error">Critical Alert - Red Gradient</h3>
          </div>
        </section>
        
        {/* Modal */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-textMain-900 mb-6">Modal</h2>
          <div className="flex gap-4">
            <Button onClick={() => setModalOpen(true)} icon="info">
              Open Modal
            </Button>
          </div>
          <Modal
            isOpen={modalOpen}
            onClose={() => setModalOpen(false)}
            title="Test Modal"
            medical
            footer={
              <div className="flex justify-end gap-3">
                <Button variant="ghost" onClick={() => setModalOpen(false)}>
                  Cancel
                </Button>
                <Button variant="medical" onClick={() => setModalOpen(false)}>
                  Confirm
                </Button>
              </div>
            }
          >
            <div className="space-y-4">
              <p className="text-textSubtle-800">
                This is a test modal with medical styling using your custom color scheme.
              </p>
              <div className="flex items-center gap-3 p-4 bg-success-50 border border-success-200 rounded-xl">
                <Icon name="checkCircle" className="text-success-600" />
                <p className="text-success-800">Modal is working perfectly with the new design system!</p>
              </div>
            </div>
          </Modal>
        </section>

        {/* Typography */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-textMain-900 mb-6">Typography</h2>
          <Card>
            <div className="space-y-4">
              <h1 className="text-4xl font-bold text-textMain-900">Heading 1 - Main Text</h1>
              <h2 className="text-3xl font-semibold text-textMain-900">Heading 2 - Main Text</h2>
              <h3 className="text-2xl font-medium text-textMain-900">Heading 3 - Main Text</h3>
              <p className="text-base text-textMain-900">
                Body text using your custom Deep Charcoal color (#1A1A1A) for excellent readability.
              </p>
              <p className="text-sm text-textSubtle-800">
                Subtle text using your custom Medium Gray color (#6B7280) for secondary information.
              </p>
            </div>
          </Card>
        </section>
      </div>
    </div>
  );
};

export default TestPage;