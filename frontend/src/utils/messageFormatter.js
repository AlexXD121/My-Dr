/**
 * Message Formatter Utility
 * Simple, reliable formatting for AI medical responses
 */

export const formatMedicalMessage = (text) => {
  if (!text || typeof text !== 'string') {
    return text;
  }

  let formatted = text.trim();

  // Step 1: Remove AI assistant references
  formatted = formatted.replace(/As a supportive assistant,?\s*/gi, '');
  formatted = formatted.replace(/As an AI,?\s*/gi, '');
  formatted = formatted.replace(/I'm here to support you,?\s*/gi, '');

  // Step 2: Add main heading
  formatted = `## 🩺 **Medical Support & Information**\n\n${formatted}`;

  // Step 3: Format numbered lists
  formatted = formatted.replace(/(\d+)\.\s*([^:\n]+):/g, '\n### $2\n');
  formatted = formatted.replace(/(\d+)\.\s*([^\n]+)/g, '\n• **$2**');

  // Step 4: Format "Here are" statements
  formatted = formatted.replace(/Here are some ([^:]+):/gi, '\n## 💡 **$1**\n');
  formatted = formatted.replace(/Here are ([^:]+):/gi, '\n## 💡 **$1**\n');

  // Step 5: Format important statements
  formatted = formatted.replace(/Remember[,:]\s*/gi, '\n> 💭 **Remember:** ');
  formatted = formatted.replace(/Important[,:]\s*/gi, '\n> ⚠️ **Important:** ');
  formatted = formatted.replace(/Note[,:]\s*/gi, '\n> 📝 **Note:** ');

  // Step 6: Highlight medical and emotional terms
  const importantTerms = [
    'traumatized', 'trauma', 'anxiety', 'depression', 'stress', 'emotions', 'feelings',
    'mental health', 'professional', 'therapy', 'counseling', 'support',
    'symptoms', 'treatment', 'medication', 'self-care', 'coping', 'healing'
  ];

  importantTerms.forEach(term => {
    const regex = new RegExp(`\\b(${term})\\b`, 'gi');
    formatted = formatted.replace(regex, '**$1**');
  });

  // Step 7: Format questions at the end
  formatted = formatted.replace(/\?\s*([A-Z][^?]*\?)/g, '?\n\n**$1**');

  // Step 8: Clean up spacing
  formatted = formatted.replace(/\n{3,}/g, '\n\n');
  formatted = formatted.replace(/^\n+/, '');

  // Step 9: Add medical disclaimer
  formatted += `\n\n---\n\n> 💡 **Medical Disclaimer:** This information is for educational purposes only and should not replace professional medical advice. Always consult with a healthcare provider for medical concerns.`;

  return formatted.trim();
};

export const detectMessageType = (text) => {
  const lowerText = text.toLowerCase();
  
  if (lowerText.includes('emergency') || lowerText.includes('urgent') || lowerText.includes('911')) {
    return 'emergency';
  }
  
  if (lowerText.includes('symptom') || lowerText.includes('pain') || lowerText.includes('feel')) {
    return 'symptoms';
  }
  
  if (lowerText.includes('treatment') || lowerText.includes('medication') || lowerText.includes('therapy')) {
    return 'treatment';
  }
  
  if (lowerText.includes('mental') || lowerText.includes('anxiety') || lowerText.includes('depression')) {
    return 'mental-health';
  }
  
  return 'general';
};

export const addContextualFormatting = (text, messageType) => {
  let formatted = text;
  
  switch (messageType) {
    case 'emergency':
      formatted = `> 🚨 **EMERGENCY INFORMATION**\n> This response contains urgent medical information.\n\n${formatted}`;
      break;
      
    case 'mental-health':
      formatted = `## 🧠 **Mental Health Support**\n\n${formatted}`;
      break;
      
    case 'symptoms':
      formatted = `## 🩺 **Symptom Information**\n\n${formatted}`;
      break;
      
    case 'treatment':
      formatted = `## 💊 **Treatment Information**\n\n${formatted}`;
      break;
      
    default:
      // Keep general formatting
      break;
  }
  
  return formatted;
};