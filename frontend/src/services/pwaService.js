class PWAService {
  constructor() {
    this.deferredPrompt = null;
    this.isInstalled = false;
    this.isOnline = navigator.onLine;
    this.offlineQueue = [];
    
    this.init();
  }

  init() {
    // Register service worker
    this.registerServiceWorker();
    
    // Listen for install prompt
    this.setupInstallPrompt();
    
    // Setup offline/online detection
    this.setupNetworkDetection();
    
    // Setup push notifications
    this.setupPushNotifications();
  }

  async registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js');
        console.log('Service Worker registered successfully:', registration);
        
        // Listen for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // New content is available
              this.showUpdateAvailable();
            }
          });
        });
        
        return registration;
      } catch (error) {
        console.error('Service Worker registration failed:', error);
      }
    }
  }

  setupInstallPrompt() {
    window.addEventListener('beforeinstallprompt', (e) => {
      // Prevent the mini-infobar from appearing on mobile
      e.preventDefault();
      // Stash the event so it can be triggered later
      this.deferredPrompt = e;
      // Show install button
      this.showInstallButton();
    });

    window.addEventListener('appinstalled', () => {
      console.log('PWA was installed');
      this.isInstalled = true;
      this.hideInstallButton();
    });
  }

  setupNetworkDetection() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.syncOfflineData();
      this.showOnlineStatus();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.showOfflineStatus();
    });
  }

  async setupPushNotifications() {
    if ('Notification' in window && 'serviceWorker' in navigator) {
      const permission = await Notification.requestPermission();
      if (permission === 'granted') {
        console.log('Notification permission granted');
        await this.subscribeToPush();
      }
    }
  }

  async subscribeToPush() {
    try {
      const registration = await navigator.serviceWorker.ready;
      
      // Skip push subscription if no VAPID key is configured
      const vapidKey = import.meta.env.VITE_VAPID_PUBLIC_KEY;
      if (!vapidKey) {
        console.log('Push notifications disabled: No VAPID key configured');
        return;
      }
      
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.urlBase64ToUint8Array(vapidKey)
      });
      
      // Send subscription to server
      await this.sendSubscriptionToServer(subscription);
    } catch (error) {
      console.error('Failed to subscribe to push notifications:', error);
    }
  }

  urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  async sendSubscriptionToServer(subscription) {
    // Send to your backend
    try {
      await fetch('/api/push-subscription', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(subscription)
      });
    } catch (error) {
      console.error('Failed to send subscription to server:', error);
    }
  }

  async installApp() {
    if (this.deferredPrompt) {
      // Show the install prompt
      this.deferredPrompt.prompt();
      
      // Wait for the user to respond to the prompt
      const { outcome } = await this.deferredPrompt.userChoice;
      console.log(`User response to the install prompt: ${outcome}`);
      
      // Clear the deferredPrompt
      this.deferredPrompt = null;
    }
  }

  showInstallButton() {
    // Dispatch custom event to show install button in UI
    window.dispatchEvent(new CustomEvent('pwa-install-available'));
  }

  hideInstallButton() {
    // Dispatch custom event to hide install button in UI
    window.dispatchEvent(new CustomEvent('pwa-install-completed'));
  }

  showUpdateAvailable() {
    // Dispatch custom event to show update notification
    window.dispatchEvent(new CustomEvent('pwa-update-available'));
  }

  showOnlineStatus() {
    // Dispatch custom event for online status
    window.dispatchEvent(new CustomEvent('network-online'));
  }

  showOfflineStatus() {
    // Dispatch custom event for offline status
    window.dispatchEvent(new CustomEvent('network-offline'));
  }

  // Offline data management
  addToOfflineQueue(data) {
    this.offlineQueue.push({
      ...data,
      timestamp: Date.now(),
      id: Math.random().toString(36).substr(2, 9)
    });
    this.saveOfflineQueue();
  }

  saveOfflineQueue() {
    localStorage.setItem('mydoc-offline-queue', JSON.stringify(this.offlineQueue));
  }

  loadOfflineQueue() {
    const saved = localStorage.getItem('mydoc-offline-queue');
    if (saved) {
      this.offlineQueue = JSON.parse(saved);
    }
  }

  async syncOfflineData() {
    this.loadOfflineQueue();
    
    for (const item of this.offlineQueue) {
      try {
        await this.syncItem(item);
        // Remove from queue after successful sync
        this.offlineQueue = this.offlineQueue.filter(q => q.id !== item.id);
      } catch (error) {
        console.error('Failed to sync item:', error);
      }
    }
    
    this.saveOfflineQueue();
  }

  async syncItem(item) {
    // Implement sync logic based on item type
    switch (item.type) {
      case 'message':
        return await this.syncMessage(item);
      case 'medical-record':
        return await this.syncMedicalRecord(item);
      default:
        console.warn('Unknown sync item type:', item.type);
    }
  }

  async syncMessage(item) {
    return await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(item.data)
    });
  }

  async syncMedicalRecord(item) {
    return await fetch('/api/medical-history', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(item.data)
    });
  }

  // Notification scheduling
  async scheduleNotification(title, body, delay) {
    if ('serviceWorker' in navigator && 'Notification' in window) {
      const registration = await navigator.serviceWorker.ready;
      
      setTimeout(() => {
        registration.showNotification(title, {
          body,
          icon: '/icons/icon-192x192.png',
          badge: '/icons/badge-72x72.png',
          vibrate: [200, 100, 200],
          tag: 'medication-reminder',
          requireInteraction: true,
          actions: [
            {
              action: 'taken',
              title: 'Mark as Taken'
            },
            {
              action: 'snooze',
              title: 'Remind Later'
            }
          ]
        });
      }, delay);
    }
  }

  // Medication reminder scheduling
  scheduleMedicationReminder(medication, time) {
    const now = new Date();
    const reminderTime = new Date(time);
    const delay = reminderTime.getTime() - now.getTime();
    
    if (delay > 0) {
      this.scheduleNotification(
        'Medication Reminder',
        `Time to take your ${medication}`,
        delay
      );
    }
  }

  // Check if app is running in standalone mode
  isStandalone() {
    return window.matchMedia('(display-mode: standalone)').matches ||
           window.navigator.standalone === true;
  }

  // Get installation status
  getInstallationStatus() {
    return {
      isInstallable: !!this.deferredPrompt,
      isInstalled: this.isInstalled || this.isStandalone(),
      isOnline: this.isOnline
    };
  }
}

// Create singleton instance
const pwaService = new PWAService();

export default pwaService;