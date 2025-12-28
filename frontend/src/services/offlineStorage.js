class OfflineStorage {
  constructor() {
    this.dbName = 'MyDocAI';
    this.version = 1;
    this.db = null;
    this.init();
  }

  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve(this.db);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // Messages store
        if (!db.objectStoreNames.contains('messages')) {
          const messagesStore = db.createObjectStore('messages', { 
            keyPath: 'id', 
            autoIncrement: true 
          });
          messagesStore.createIndex('timestamp', 'timestamp', { unique: false });
          messagesStore.createIndex('conversationId', 'conversationId', { unique: false });
          messagesStore.createIndex('synced', 'synced', { unique: false });
        }

        // Medical records store
        if (!db.objectStoreNames.contains('medicalRecords')) {
          const recordsStore = db.createObjectStore('medicalRecords', { 
            keyPath: 'id', 
            autoIncrement: true 
          });
          recordsStore.createIndex('date', 'date', { unique: false });
          recordsStore.createIndex('type', 'type', { unique: false });
          recordsStore.createIndex('synced', 'synced', { unique: false });
        }

        // Conversations store
        if (!db.objectStoreNames.contains('conversations')) {
          const conversationsStore = db.createObjectStore('conversations', { 
            keyPath: 'id', 
            autoIncrement: true 
          });
          conversationsStore.createIndex('lastMessageAt', 'lastMessageAt', { unique: false });
          conversationsStore.createIndex('synced', 'synced', { unique: false });
        }

        // Sync queue store
        if (!db.objectStoreNames.contains('syncQueue')) {
          const syncStore = db.createObjectStore('syncQueue', { 
            keyPath: 'id', 
            autoIncrement: true 
          });
          syncStore.createIndex('type', 'type', { unique: false });
          syncStore.createIndex('timestamp', 'timestamp', { unique: false });
        }
      };
    });
  }

  // Generic database operations
  async add(storeName, data) {
    const transaction = this.db.transaction([storeName], 'readwrite');
    const store = transaction.objectStore(storeName);
    return store.add({
      ...data,
      timestamp: Date.now(),
      synced: false
    });
  }

  async get(storeName, id) {
    const transaction = this.db.transaction([storeName], 'readonly');
    const store = transaction.objectStore(storeName);
    return store.get(id);
  }

  async getAll(storeName, indexName = null, query = null) {
    const transaction = this.db.transaction([storeName], 'readonly');
    const store = transaction.objectStore(storeName);
    
    if (indexName) {
      const index = store.index(indexName);
      return query ? index.getAll(query) : index.getAll();
    }
    
    return store.getAll();
  }

  async update(storeName, data) {
    const transaction = this.db.transaction([storeName], 'readwrite');
    const store = transaction.objectStore(storeName);
    return store.put(data);
  }

  async delete(storeName, id) {
    const transaction = this.db.transaction([storeName], 'readwrite');
    const store = transaction.objectStore(storeName);
    return store.delete(id);
  }

  // Message operations
  async saveMessage(message) {
    return this.add('messages', {
      ...message,
      id: message.id || `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    });
  }

  async getMessages(conversationId = null) {
    if (conversationId) {
      return this.getAll('messages', 'conversationId', conversationId);
    }
    return this.getAll('messages');
  }

  async getUnsyncedMessages() {
    return this.getAll('messages', 'synced', false);
  }

  async markMessageSynced(messageId) {
    const message = await this.get('messages', messageId);
    if (message) {
      message.synced = true;
      return this.update('messages', message);
    }
  }

  // Medical record operations
  async saveMedicalRecord(record) {
    return this.add('medicalRecords', {
      ...record,
      id: record.id || `record_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    });
  }

  async getMedicalRecords() {
    return this.getAll('medicalRecords');
  }

  async getUnsyncedMedicalRecords() {
    return this.getAll('medicalRecords', 'synced', false);
  }

  async markMedicalRecordSynced(recordId) {
    const record = await this.get('medicalRecords', recordId);
    if (record) {
      record.synced = true;
      return this.update('medicalRecords', record);
    }
  }

  // Conversation operations
  async saveConversation(conversation) {
    return this.add('conversations', {
      ...conversation,
      id: conversation.id || `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    });
  }

  async getConversations() {
    return this.getAll('conversations');
  }

  async updateConversation(conversation) {
    return this.update('conversations', conversation);
  }

  // Sync queue operations
  async addToSyncQueue(type, data, action = 'create') {
    return this.add('syncQueue', {
      type,
      action,
      data,
      retryCount: 0,
      maxRetries: 3
    });
  }

  async getSyncQueue() {
    return this.getAll('syncQueue');
  }

  async removeSyncItem(id) {
    return this.delete('syncQueue', id);
  }

  async incrementRetryCount(id) {
    const item = await this.get('syncQueue', id);
    if (item) {
      item.retryCount = (item.retryCount || 0) + 1;
      return this.update('syncQueue', item);
    }
  }

  // Sync operations
  async syncWithServer() {
    if (!navigator.onLine) {
      console.log('Cannot sync: offline');
      return;
    }

    const syncQueue = await this.getSyncQueue();
    const results = [];

    for (const item of syncQueue) {
      try {
        const result = await this.syncItem(item);
        results.push({ success: true, item, result });
        await this.removeSyncItem(item.id);
      } catch (error) {
        console.error('Sync failed for item:', item, error);
        
        if (item.retryCount < item.maxRetries) {
          await this.incrementRetryCount(item.id);
        } else {
          // Max retries reached, remove from queue
          await this.removeSyncItem(item.id);
        }
        
        results.push({ success: false, item, error });
      }
    }

    return results;
  }

  async syncItem(item) {
    const { type, action, data } = item;
    
    switch (type) {
      case 'message':
        return this.syncMessage(data, action);
      case 'medicalRecord':
        return this.syncMedicalRecord(data, action);
      case 'conversation':
        return this.syncConversation(data, action);
      default:
        throw new Error(`Unknown sync type: ${type}`);
    }
  }

  async syncMessage(message, action) {
    const endpoint = '/api/chat';
    const method = action === 'create' ? 'POST' : 'PUT';
    
    const response = await fetch(endpoint, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(message)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    
    // Mark as synced in local storage
    if (message.id) {
      await this.markMessageSynced(message.id);
    }
    
    return result;
  }

  async syncMedicalRecord(record, action) {
    const endpoint = '/api/medical-history';
    const method = action === 'create' ? 'POST' : action === 'update' ? 'PUT' : 'DELETE';
    
    const response = await fetch(endpoint, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: method !== 'DELETE' ? JSON.stringify(record) : undefined
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = method !== 'DELETE' ? await response.json() : null;
    
    // Mark as synced in local storage
    if (record.id) {
      await this.markMedicalRecordSynced(record.id);
    }
    
    return result;
  }

  async syncConversation(conversation, action) {
    const endpoint = '/api/conversations';
    const method = action === 'create' ? 'POST' : 'PUT';
    
    const response = await fetch(endpoint, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(conversation)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Utility methods
  async clearAllData() {
    const stores = ['messages', 'medicalRecords', 'conversations', 'syncQueue'];
    
    for (const storeName of stores) {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      await store.clear();
    }
  }

  async getStorageUsage() {
    const estimate = await navigator.storage.estimate();
    return {
      used: estimate.usage,
      quota: estimate.quota,
      percentage: (estimate.usage / estimate.quota) * 100
    };
  }

  async exportData() {
    const data = {};
    const stores = ['messages', 'medicalRecords', 'conversations'];
    
    for (const storeName of stores) {
      data[storeName] = await this.getAll(storeName);
    }
    
    return data;
  }

  async importData(data) {
    for (const [storeName, items] of Object.entries(data)) {
      if (Array.isArray(items)) {
        for (const item of items) {
          await this.add(storeName, item);
        }
      }
    }
  }
}

// Create singleton instance
const offlineStorage = new OfflineStorage();

export default offlineStorage;