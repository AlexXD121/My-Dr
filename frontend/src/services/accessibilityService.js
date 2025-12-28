class AccessibilityService {
  constructor() {
    this.settings = {
      highContrast: false,
      fontSize: 'medium', // small, medium, large, extra-large
      reducedMotion: false,
      screenReader: false,
      keyboardNavigation: true,
      focusVisible: true,
      announcements: true
    };
    
    this.init();
  }

  init() {
    this.loadSettings();
    this.detectPreferences();
    this.setupKeyboardNavigation();
    this.setupFocusManagement();
    this.setupScreenReaderSupport();
  }

  // Load saved accessibility settings
  loadSettings() {
    const saved = localStorage.getItem('mydoc-accessibility-settings');
    if (saved) {
      this.settings = { ...this.settings, ...JSON.parse(saved) };
    }
    this.applySettings();
  }

  // Save accessibility settings
  saveSettings() {
    localStorage.setItem('mydoc-accessibility-settings', JSON.stringify(this.settings));
    this.applySettings();
  }

  // Detect system preferences
  detectPreferences() {
    // Detect reduced motion preference
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      this.settings.reducedMotion = true;
    }

    // Detect high contrast preference
    if (window.matchMedia('(prefers-contrast: high)').matches) {
      this.settings.highContrast = true;
    }

    // Detect screen reader
    this.settings.screenReader = this.detectScreenReader();

    this.applySettings();
  }

  // Detect if screen reader is active
  detectScreenReader() {
    // Check for common screen reader indicators
    const indicators = [
      'speechSynthesis' in window,
      navigator.userAgent.includes('NVDA'),
      navigator.userAgent.includes('JAWS'),
      navigator.userAgent.includes('VoiceOver'),
      window.speechSynthesis && window.speechSynthesis.getVoices().length > 0
    ];

    return indicators.some(indicator => indicator);
  }

  // Apply accessibility settings
  applySettings() {
    const root = document.documentElement;

    // High contrast mode
    if (this.settings.highContrast) {
      root.classList.add('high-contrast');
    } else {
      root.classList.remove('high-contrast');
    }

    // Font size
    root.classList.remove('font-small', 'font-medium', 'font-large', 'font-extra-large');
    root.classList.add(`font-${this.settings.fontSize}`);

    // Reduced motion
    if (this.settings.reducedMotion) {
      root.classList.add('reduced-motion');
    } else {
      root.classList.remove('reduced-motion');
    }

    // Focus visible
    if (this.settings.focusVisible) {
      root.classList.add('focus-visible');
    } else {
      root.classList.remove('focus-visible');
    }

    // Dispatch settings change event
    window.dispatchEvent(new CustomEvent('accessibility-settings-changed', {
      detail: this.settings
    }));
  }

  // Setup keyboard navigation
  setupKeyboardNavigation() {
    let focusableElements = [];
    let currentFocusIndex = -1;

    const updateFocusableElements = () => {
      focusableElements = Array.from(document.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"]), [contenteditable]'
      )).filter(el => {
        return !el.disabled && 
               !el.hidden && 
               el.offsetWidth > 0 && 
               el.offsetHeight > 0 &&
               window.getComputedStyle(el).visibility !== 'hidden';
      });
    };

    document.addEventListener('keydown', (e) => {
      updateFocusableElements();

      switch (e.key) {
        case 'Tab':
          // Enhanced tab navigation
          if (e.shiftKey) {
            currentFocusIndex = Math.max(0, currentFocusIndex - 1);
          } else {
            currentFocusIndex = Math.min(focusableElements.length - 1, currentFocusIndex + 1);
          }
          break;

        case 'Escape':
          // Close modals, dropdowns, etc.
          this.handleEscapeKey();
          break;

        case 'Enter':
        case ' ':
          // Activate buttons and links
          if (document.activeElement && 
              (document.activeElement.tagName === 'BUTTON' || 
               document.activeElement.getAttribute('role') === 'button')) {
            e.preventDefault();
            document.activeElement.click();
          }
          break;

        case 'ArrowUp':
        case 'ArrowDown':
        case 'ArrowLeft':
        case 'ArrowRight':
          // Handle arrow key navigation for custom components
          this.handleArrowKeys(e);
          break;

        case 'Home':
          // Go to first focusable element
          if (focusableElements.length > 0) {
            e.preventDefault();
            focusableElements[0].focus();
            currentFocusIndex = 0;
          }
          break;

        case 'End':
          // Go to last focusable element
          if (focusableElements.length > 0) {
            e.preventDefault();
            focusableElements[focusableElements.length - 1].focus();
            currentFocusIndex = focusableElements.length - 1;
          }
          break;
      }
    });

    // Update focusable elements when DOM changes
    const observer = new MutationObserver(updateFocusableElements);
    observer.observe(document.body, { 
      childList: true, 
      subtree: true, 
      attributes: true, 
      attributeFilter: ['disabled', 'hidden', 'tabindex'] 
    });
  }

  // Handle escape key for closing modals
  handleEscapeKey() {
    // Close any open modals
    const modals = document.querySelectorAll('[role="dialog"], .modal, [data-modal]');
    modals.forEach(modal => {
      if (modal.style.display !== 'none' && !modal.hidden) {
        const closeButton = modal.querySelector('[data-close], .close, [aria-label*="close"]');
        if (closeButton) {
          closeButton.click();
        }
      }
    });

    // Close dropdowns
    const dropdowns = document.querySelectorAll('[role="menu"], .dropdown-menu, [data-dropdown]');
    dropdowns.forEach(dropdown => {
      if (dropdown.style.display !== 'none' && !dropdown.hidden) {
        dropdown.style.display = 'none';
        dropdown.hidden = true;
      }
    });
  }

  // Handle arrow key navigation
  handleArrowKeys(e) {
    const activeElement = document.activeElement;
    const role = activeElement.getAttribute('role');

    // Handle menu navigation
    if (role === 'menuitem' || activeElement.closest('[role="menu"]')) {
      this.handleMenuNavigation(e);
    }

    // Handle tab navigation
    if (role === 'tab' || activeElement.closest('[role="tablist"]')) {
      this.handleTabNavigation(e);
    }

    // Handle listbox navigation
    if (role === 'option' || activeElement.closest('[role="listbox"]')) {
      this.handleListboxNavigation(e);
    }
  }

  // Menu navigation with arrow keys
  handleMenuNavigation(e) {
    const menu = document.activeElement.closest('[role="menu"]');
    if (!menu) return;

    const items = Array.from(menu.querySelectorAll('[role="menuitem"]'));
    const currentIndex = items.indexOf(document.activeElement);

    let nextIndex;
    switch (e.key) {
      case 'ArrowDown':
        nextIndex = (currentIndex + 1) % items.length;
        break;
      case 'ArrowUp':
        nextIndex = (currentIndex - 1 + items.length) % items.length;
        break;
      default:
        return;
    }

    e.preventDefault();
    items[nextIndex].focus();
  }

  // Tab navigation with arrow keys
  handleTabNavigation(e) {
    const tablist = document.activeElement.closest('[role="tablist"]');
    if (!tablist) return;

    const tabs = Array.from(tablist.querySelectorAll('[role="tab"]'));
    const currentIndex = tabs.indexOf(document.activeElement);

    let nextIndex;
    switch (e.key) {
      case 'ArrowLeft':
        nextIndex = (currentIndex - 1 + tabs.length) % tabs.length;
        break;
      case 'ArrowRight':
        nextIndex = (currentIndex + 1) % tabs.length;
        break;
      default:
        return;
    }

    e.preventDefault();
    tabs[nextIndex].focus();
    tabs[nextIndex].click();
  }

  // Listbox navigation with arrow keys
  handleListboxNavigation(e) {
    const listbox = document.activeElement.closest('[role="listbox"]');
    if (!listbox) return;

    const options = Array.from(listbox.querySelectorAll('[role="option"]'));
    const currentIndex = options.indexOf(document.activeElement);

    let nextIndex;
    switch (e.key) {
      case 'ArrowDown':
        nextIndex = (currentIndex + 1) % options.length;
        break;
      case 'ArrowUp':
        nextIndex = (currentIndex - 1 + options.length) % options.length;
        break;
      default:
        return;
    }

    e.preventDefault();
    options[nextIndex].focus();
  }

  // Setup focus management
  setupFocusManagement() {
    // Focus trap for modals
    this.setupFocusTrap();
    
    // Skip links
    this.setupSkipLinks();
    
    // Focus indicators
    this.setupFocusIndicators();
  }

  // Setup focus trap for modals
  setupFocusTrap() {
    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Tab') return;

      const modal = document.querySelector('[role="dialog"]:not([hidden]), .modal:not([hidden])');
      if (!modal) return;

      const focusableElements = modal.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );

      if (focusableElements.length === 0) return;

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    });
  }

  // Setup skip links
  setupSkipLinks() {
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'skip-link';
    skipLink.style.cssText = `
      position: absolute;
      top: -40px;
      left: 6px;
      background: #000;
      color: #fff;
      padding: 8px;
      text-decoration: none;
      border-radius: 4px;
      z-index: 1000;
      transition: top 0.3s;
    `;

    skipLink.addEventListener('focus', () => {
      skipLink.style.top = '6px';
    });

    skipLink.addEventListener('blur', () => {
      skipLink.style.top = '-40px';
    });

    document.body.insertBefore(skipLink, document.body.firstChild);
  }

  // Setup focus indicators
  setupFocusIndicators() {
    // Add focus-visible polyfill behavior
    let hadKeyboardEvent = true;

    const keyboardThrottledEventListener = (e) => {
      if (e.type === 'keydown' && e.metaKey || e.altKey || e.ctrlKey) {
        return;
      }
      hadKeyboardEvent = true;
    };

    const pointerEventListener = () => {
      hadKeyboardEvent = false;
    };

    document.addEventListener('keydown', keyboardThrottledEventListener, true);
    document.addEventListener('mousedown', pointerEventListener, true);
    document.addEventListener('pointerdown', pointerEventListener, true);
    document.addEventListener('touchstart', pointerEventListener, true);

    document.addEventListener('focus', (e) => {
      if (hadKeyboardEvent || e.target.matches(':focus-visible')) {
        e.target.classList.add('focus-visible');
      }
    }, true);

    document.addEventListener('blur', (e) => {
      e.target.classList.remove('focus-visible');
    }, true);
  }

  // Setup screen reader support
  setupScreenReaderSupport() {
    // Live region for announcements
    this.createLiveRegion();
    
    // ARIA labels and descriptions
    this.enhanceARIA();
  }

  // Create live region for screen reader announcements
  createLiveRegion() {
    const liveRegion = document.createElement('div');
    liveRegion.id = 'live-region';
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.style.cssText = `
      position: absolute;
      left: -10000px;
      width: 1px;
      height: 1px;
      overflow: hidden;
    `;
    document.body.appendChild(liveRegion);

    this.liveRegion = liveRegion;
  }

  // Announce message to screen readers
  announce(message, priority = 'polite') {
    if (!this.settings.announcements) return;

    if (this.liveRegion) {
      this.liveRegion.setAttribute('aria-live', priority);
      this.liveRegion.textContent = message;
      
      // Clear after announcement
      setTimeout(() => {
        this.liveRegion.textContent = '';
      }, 1000);
    }
  }

  // Enhance ARIA attributes
  enhanceARIA() {
    // Add missing labels
    const unlabeledInputs = document.querySelectorAll('input:not([aria-label]):not([aria-labelledby])');
    unlabeledInputs.forEach(input => {
      const label = input.closest('label') || document.querySelector(`label[for="${input.id}"]`);
      if (label) {
        input.setAttribute('aria-labelledby', label.id || this.generateId('label'));
      }
    });

    // Add button roles to clickable elements
    const clickableElements = document.querySelectorAll('[onclick]:not(button):not([role])');
    clickableElements.forEach(el => {
      el.setAttribute('role', 'button');
      el.setAttribute('tabindex', '0');
    });
  }

  // Generate unique ID
  generateId(prefix = 'id') {
    return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
  }

  // Update setting
  updateSetting(key, value) {
    this.settings[key] = value;
    this.saveSettings();
  }

  // Get current settings
  getSettings() {
    return { ...this.settings };
  }

  // Reset to defaults
  resetSettings() {
    this.settings = {
      highContrast: false,
      fontSize: 'medium',
      reducedMotion: false,
      screenReader: this.detectScreenReader(),
      keyboardNavigation: true,
      focusVisible: true,
      announcements: true
    };
    this.saveSettings();
  }
}

// Create singleton instance
const accessibilityService = new AccessibilityService();

export default accessibilityService;