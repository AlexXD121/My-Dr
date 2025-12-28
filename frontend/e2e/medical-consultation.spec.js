import { test, expect } from '@playwright/test';

test.describe('Medical Consultation Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    
    // Mock authentication for testing
    await page.addInitScript(() => {
      window.localStorage.setItem('auth_token', 'test_token_123');
      window.localStorage.setItem('user_id', 'test_user_123');
    });
  });

  test('should complete a basic medical consultation', async ({ page }) => {
    // Navigate to chat interface
    await page.click('[data-testid="chat-button"]');
    
    // Wait for chat interface to load
    await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();
    
    // Type a medical question
    const messageInput = page.locator('[data-testid="message-input"]');
    await messageInput.fill('I have been experiencing headaches for the past 2 days');
    
    // Send the message
    await page.click('[data-testid="send-button"]');
    
    // Wait for AI response
    await expect(page.locator('[data-testid="ai-message"]').first()).toBeVisible({ timeout: 30000 });
    
    // Verify response contains medical advice
    const aiResponse = await page.locator('[data-testid="ai-message"]').first().textContent();
    expect(aiResponse).toContain('headache');
    
    // Verify medical disclaimer is present
    await expect(page.locator('[data-testid="medical-disclaimer"]')).toBeVisible();
  });

  test('should handle emergency detection', async ({ page }) => {
    await page.click('[data-testid="chat-button"]');
    await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();
    
    // Send emergency-related message
    const messageInput = page.locator('[data-testid="message-input"]');
    await messageInput.fill('I am having severe chest pain and difficulty breathing');
    await page.click('[data-testid="send-button"]');
    
    // Wait for emergency alert
    await expect(page.locator('[data-testid="emergency-alert"]')).toBeVisible({ timeout: 30000 });
    
    // Verify emergency recommendations
    const emergencyAlert = page.locator('[data-testid="emergency-alert"]');
    await expect(emergencyAlert).toContainText('emergency');
    await expect(emergencyAlert).toContainText('911');
  });

  test('should save conversation history', async ({ page }) => {
    await page.click('[data-testid="chat-button"]');
    
    // Send a message
    const messageInput = page.locator('[data-testid="message-input"]');
    await messageInput.fill('Test message for history');
    await page.click('[data-testid="send-button"]');
    
    // Wait for response
    await expect(page.locator('[data-testid="ai-message"]').first()).toBeVisible({ timeout: 30000 });
    
    // Navigate to conversation history
    await page.click('[data-testid="history-button"]');
    
    // Verify conversation appears in history
    await expect(page.locator('[data-testid="conversation-item"]').first()).toBeVisible();
    await expect(page.locator('[data-testid="conversation-item"]').first()).toContainText('Test message');
  });
});

test.describe('Symptom Checker', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.addInitScript(() => {
      window.localStorage.setItem('auth_token', 'test_token_123');
      window.localStorage.setItem('user_id', 'test_user_123');
    });
  });

  test('should complete symptom analysis', async ({ page }) => {
    // Navigate to symptom checker
    await page.click('[data-testid="symptom-checker-button"]');
    
    // Fill out symptom form
    await page.selectOption('[data-testid="symptom-select"]', 'headache');
    await page.fill('[data-testid="severity-input"]', '7');
    await page.fill('[data-testid="duration-input"]', '3 days');
    
    // Submit form
    await page.click('[data-testid="analyze-symptoms-button"]');
    
    // Wait for results
    await expect(page.locator('[data-testid="symptom-results"]')).toBeVisible({ timeout: 30000 });
    
    // Verify urgency score is displayed
    await expect(page.locator('[data-testid="urgency-score"]')).toBeVisible();
    
    // Verify recommendations are shown
    await expect(page.locator('[data-testid="recommendations"]')).toBeVisible();
  });
});

test.describe('Medical History Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.addInitScript(() => {
      window.localStorage.setItem('auth_token', 'test_token_123');
      window.localStorage.setItem('user_id', 'test_user_123');
    });
  });

  test('should add and view medical records', async ({ page }) => {
    // Navigate to medical history
    await page.click('[data-testid="medical-history-button"]');
    
    // Add new record
    await page.click('[data-testid="add-record-button"]');
    
    // Fill out form
    await page.fill('[data-testid="record-title"]', 'Annual Physical');
    await page.fill('[data-testid="record-description"]', 'Routine checkup');
    await page.fill('[data-testid="record-date"]', '2024-01-15');
    await page.fill('[data-testid="healthcare-provider"]', 'Dr. Smith');
    
    // Save record
    await page.click('[data-testid="save-record-button"]');
    
    // Verify record appears in list
    await expect(page.locator('[data-testid="medical-record"]').first()).toBeVisible();
    await expect(page.locator('[data-testid="medical-record"]').first()).toContainText('Annual Physical');
  });
});

test.describe('Drug Interaction Checker', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.addInitScript(() => {
      window.localStorage.setItem('auth_token', 'test_token_123');
      window.localStorage.setItem('user_id', 'test_user_123');
    });
  });

  test('should check drug interactions', async ({ page }) => {
    // Navigate to drug interaction checker
    await page.click('[data-testid="drug-interaction-button"]');
    
    // Add medications
    await page.fill('[data-testid="medication-input"]', 'aspirin');
    await page.click('[data-testid="add-medication-button"]');
    
    await page.fill('[data-testid="medication-input"]', 'warfarin');
    await page.click('[data-testid="add-medication-button"]');
    
    // Check interactions
    await page.click('[data-testid="check-interactions-button"]');
    
    // Wait for results
    await expect(page.locator('[data-testid="interaction-results"]')).toBeVisible({ timeout: 30000 });
    
    // Verify interaction warning is shown
    await expect(page.locator('[data-testid="interaction-warning"]')).toBeVisible();
  });
});

test.describe('Mobile Responsiveness', () => {
  test('should work on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Verify mobile navigation
    await expect(page.locator('[data-testid="mobile-menu-button"]')).toBeVisible();
    
    // Test mobile chat interface
    await page.click('[data-testid="mobile-menu-button"]');
    await page.click('[data-testid="chat-button"]');
    
    // Verify chat interface is mobile-friendly
    await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();
    await expect(page.locator('[data-testid="message-input"]')).toBeVisible();
  });
});