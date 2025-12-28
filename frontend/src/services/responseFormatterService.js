/**
 * Response Formatter Service
 * Enhances AI responses with better structure, formatting, and visual hierarchy
 */

class ResponseFormatterService {
  constructor() {
    this.medicalKeywords = {
      symptoms: [
        'symptom', 'symptoms', 'sign', 'signs', 'indicator', 'indicators',
        'manifestation', 'manifestations', 'presentation', 'presents with'
      ],
      causes: [
        'cause', 'causes', 'reason', 'reasons', 'factor', 'factors',
        'trigger', 'triggers', 'due to', 'because of', 'result of'
      ],
      treatment: [
        'treatment', 'treatments', 'therapy', 'therapies', 'medication',
        'medications', 'medicine', 'medicines', 'drug', 'drugs', 'remedy'
      ],
      prevention: [
        'prevention', 'prevent', 'preventing', 'avoid', 'avoiding',
        'precaution', 'precautions', 'prophylaxis', 'protective'
      ],
      diagnosis: [
        'diagnosis', 'diagnose', 'diagnostic', 'test', 'tests',
        'examination', 'screening', 'assessment', 'evaluation'
      ],
      emergency: [
        'emergency', 'urgent', 'serious', 'severe', 'critical',
        'seek immediate', 'call 911', 'go to hospital', 'ER'
      ]
    };

    this.formatPatterns = [
      {
        name: 'medical_list',
        regex: /(?:include|such as|like|are|following):\s*([^.!?]*(?:[.!?]|$))/gi,
        format: this.formatAsList.bind(this)
      },
      {
        name: 'dosage',
        regex: /(\d+(?:\.\d+)?)\s*(mg|ml|mcg|g|kg|lbs?|oz|tablets?|capsules?)/gi,
        format: (match, amount, unit) => `**${amount} ${unit}**`
      },
      {
        name: 'time_period',
        regex: /(\d+(?:-\d+)?)\s*(days?|weeks?|months?|years?|hours?|minutes?)/gi,
        format: (match, number, period) => `**${number} ${period}**`
      },
      {
        name: 'important_actions',
        regex: /\b(should|must|need to|have to|important to|essential to)\s+([^.!?]*)/gi,
        format: (match, modal, action) => `${modal} **${action.trim()}**`
      }
    ];
  }

  /**
   * Main method to format AI response
   */
  formatResponse(text) {
    if (!text || typeof text !== 'string') {
      return { formatted: text, sections: [], metadata: {} };
    }

    let formatted = text.trim();
    const sections = [];
    const metadata = this.analyzeResponse(text);

    // Step 1: Identify and format sections
    const identifiedSections = this.identifySections(formatted);
    sections.push(...identifiedSections);

    // Step 2: Apply general formatting patterns
    formatted = this.applyFormatPatterns(formatted);

    // Step 3: Structure the content
    formatted = this.structureContent(formatted, identifiedSections);

    // Step 4: Add visual enhancements
    formatted = this.addVisualEnhancements(formatted);

    // Step 5: Clean up formatting
    formatted = this.cleanupFormatting(formatted);

    return {
      formatted,
      sections,
      metadata
    };
  }

  /**
   * Identify medical sections in the response
   */
  identifySections(text) {
    const sections = [];
    const sentences = this.splitIntoSentences(text);

    sentences.forEach((sentence, index) => {
      const sectionType = this.identifySectionType(sentence);
      if (sectionType) {
        sections.push({
          type: sectionType,
          content: sentence.trim(),
          index,
          confidence: this.calculateConfidence(sentence, sectionType)
        });
      }
    });

    return this.mergeSimilarSections(sections);
  }

  /**
   * Identify the type of medical section
   */
  identifySectionType(sentence) {
    const lowerSentence = sentence.toLowerCase();
    
    for (const [type, keywords] of Object.entries(this.medicalKeywords)) {
      for (const keyword of keywords) {
        if (lowerSentence.includes(keyword)) {
          return type;
        }
      }
    }

    return null;
  }

  /**
   * Apply formatting patterns to text
   */
  applyFormatPatterns(text) {
    let formatted = text;

    this.formatPatterns.forEach(pattern => {
      formatted = formatted.replace(pattern.regex, pattern.format);
    });

    return formatted;
  }

  /**
   * Structure content with proper headings and sections
   */
  structureContent(text, sections) {
    let structured = text;

    // Group sections by type
    const sectionGroups = this.groupSectionsByType(sections);

    // Add headings for each section type
    Object.entries(sectionGroups).forEach(([type, sectionList]) => {
      const heading = this.getSectionHeading(type);
      const icon = this.getSectionIcon(type);
      
      if (sectionList.length > 0) {
        // Find the first occurrence of this section type
        const firstSection = sectionList[0];
        const sectionContent = this.formatSectionContent(sectionList);
        
        // Replace the original content with structured version
        structured = structured.replace(
          firstSection.content,
          `\n## ${icon} **${heading}**\n\n${sectionContent}\n`
        );

        // Remove duplicate sections
        sectionList.slice(1).forEach(section => {
          structured = structured.replace(section.content, '');
        });
      }
    });

    return structured;
  }

  /**
   * Add visual enhancements to the formatted text
   */
  addVisualEnhancements(text) {
    let enhanced = text;

    // Highlight important medical terms
    const importantTerms = [
      'diagnosis', 'treatment', 'medication', 'emergency', 'urgent',
      'serious', 'chronic', 'acute', 'infection', 'inflammation'
    ];

    importantTerms.forEach(term => {
      const regex = new RegExp(`\\b(${term})\\b`, 'gi');
      enhanced = enhanced.replace(regex, '**$1**');
    });

    // Add emphasis to warnings
    enhanced = enhanced.replace(
      /\b(warning|caution|important|note|remember)\b:?\s*/gi,
      '\n> ⚠️ **$1:** '
    );

    // Format numbered lists
    enhanced = enhanced.replace(
      /(\d+)\.\s+([^\n]+)/g,
      '\n$1. **$2**'
    );

    // Add spacing for better readability
    enhanced = enhanced.replace(/([.!?])\s+([A-Z])/g, '$1\n\n$2');

    return enhanced;
  }

  /**
   * Clean up formatting inconsistencies
   */
  cleanupFormatting(text) {
    let cleaned = text;

    // Remove excessive line breaks
    cleaned = cleaned.replace(/\n{3,}/g, '\n\n');

    // Fix spacing around headings
    cleaned = cleaned.replace(/\n##\s*/g, '\n\n## ');

    // Ensure proper spacing after headings
    cleaned = cleaned.replace(/(##[^\n]+)\n([^\n])/g, '$1\n\n$2');

    // Clean up list formatting
    cleaned = cleaned.replace(/\n•\s*/g, '\n• ');

    // Remove trailing whitespace
    cleaned = cleaned.replace(/[ \t]+$/gm, '');

    return cleaned.trim();
  }

  /**
   * Format content as a list
   */
  formatAsList(match, content) {
    const items = content
      .split(/[,;]|and(?=\s)|or(?=\s)/)
      .map(item => item.trim())
      .filter(item => item.length > 0);

    if (items.length > 1) {
      return ':\n\n' + items.map(item => `• **${item}**`).join('\n');
    }
    return `: **${content.trim()}**`;
  }

  /**
   * Split text into sentences
   */
  splitIntoSentences(text) {
    return text
      .split(/[.!?]+/)
      .map(sentence => sentence.trim())
      .filter(sentence => sentence.length > 0);
  }

  /**
   * Calculate confidence score for section identification
   */
  calculateConfidence(sentence, sectionType) {
    const keywords = this.medicalKeywords[sectionType] || [];
    const lowerSentence = sentence.toLowerCase();
    
    let matches = 0;
    keywords.forEach(keyword => {
      if (lowerSentence.includes(keyword)) {
        matches++;
      }
    });

    return matches / keywords.length;
  }

  /**
   * Merge similar sections together
   */
  mergeSimilarSections(sections) {
    const merged = [];
    const typeGroups = {};

    sections.forEach(section => {
      if (!typeGroups[section.type]) {
        typeGroups[section.type] = [];
      }
      typeGroups[section.type].push(section);
    });

    Object.entries(typeGroups).forEach(([type, sectionList]) => {
      if (sectionList.length === 1) {
        merged.push(sectionList[0]);
      } else {
        // Merge multiple sections of the same type
        const mergedContent = sectionList
          .map(s => s.content)
          .join(' ');
        
        merged.push({
          type,
          content: mergedContent,
          index: Math.min(...sectionList.map(s => s.index)),
          confidence: Math.max(...sectionList.map(s => s.confidence))
        });
      }
    });

    return merged.sort((a, b) => a.index - b.index);
  }

  /**
   * Group sections by type
   */
  groupSectionsByType(sections) {
    const groups = {};
    
    sections.forEach(section => {
      if (!groups[section.type]) {
        groups[section.type] = [];
      }
      groups[section.type].push(section);
    });

    return groups;
  }

  /**
   * Format content for a specific section
   */
  formatSectionContent(sectionList) {
    return sectionList
      .map(section => section.content)
      .join('\n\n• ')
      .replace(/^/, '• ');
  }

  /**
   * Get heading for section type
   */
  getSectionHeading(type) {
    const headings = {
      symptoms: 'Symptoms & Signs',
      causes: 'Possible Causes',
      treatment: 'Treatment Options',
      prevention: 'Prevention Tips',
      diagnosis: 'Diagnostic Information',
      emergency: 'Important Warnings'
    };

    return headings[type] || 'Information';
  }

  /**
   * Get icon for section type
   */
  getSectionIcon(type) {
    const icons = {
      symptoms: '🩺',
      causes: '🔍',
      treatment: '💊',
      prevention: '🛡️',
      diagnosis: '📋',
      emergency: '⚠️'
    };

    return icons[type] || '📌';
  }

  /**
   * Analyze response for metadata
   */
  analyzeResponse(text) {
    const wordCount = text.split(/\s+/).length;
    const sentenceCount = text.split(/[.!?]+/).length;
    const hasEmergencyKeywords = this.medicalKeywords.emergency.some(
      keyword => text.toLowerCase().includes(keyword)
    );

    return {
      wordCount,
      sentenceCount,
      readingTime: Math.ceil(wordCount / 200), // Average reading speed
      urgencyLevel: hasEmergencyKeywords ? 'high' : 'normal',
      complexity: wordCount > 200 ? 'high' : wordCount > 100 ? 'medium' : 'low'
    };
  }

  /**
   * Format response for specific medical contexts
   */
  formatForContext(text, context = 'general') {
    const contextFormatters = {
      emergency: this.formatEmergencyResponse.bind(this),
      symptoms: this.formatSymptomsResponse.bind(this),
      treatment: this.formatTreatmentResponse.bind(this),
      prevention: this.formatPreventionResponse.bind(this)
    };

    const formatter = contextFormatters[context];
    return formatter ? formatter(text) : this.formatResponse(text);
  }

  /**
   * Format emergency response with special highlighting
   */
  formatEmergencyResponse(text) {
    const formatted = this.formatResponse(text);
    
    // Add emergency banner
    const emergencyBanner = `
> 🚨 **EMERGENCY INFORMATION**
> 
> This response contains urgent medical information. 
> Please seek immediate medical attention if applicable.

---

`;

    return {
      ...formatted,
      formatted: emergencyBanner + formatted.formatted
    };
  }

  /**
   * Format symptoms response with symptom checker integration
   */
  formatSymptomsResponse(text) {
    const formatted = this.formatResponse(text);
    
    // Add symptom checker suggestion
    const suggestion = `

---

💡 **Tip:** Use our [Symptom Checker](/symptoms) for a more detailed analysis of your symptoms.

`;

    return {
      ...formatted,
      formatted: formatted.formatted + suggestion
    };
  }

  /**
   * Format treatment response with medication safety info
   */
  formatTreatmentResponse(text) {
    const formatted = this.formatResponse(text);
    
    // Add medication safety reminder
    const safetyReminder = `

---

⚕️ **Medication Safety Reminder:**
- Always follow prescribed dosages
- Check for drug interactions
- Consult your pharmacist or doctor with questions

`;

    return {
      ...formatted,
      formatted: formatted.formatted + safetyReminder
    };
  }

  /**
   * Format prevention response with actionable tips
   */
  formatPreventionResponse(text) {
    const formatted = this.formatResponse(text);
    
    // Add prevention action plan
    const actionPlan = `

---

📋 **Your Prevention Action Plan:**
1. Review the prevention tips above
2. Choose 2-3 tips to implement this week
3. Track your progress
4. Consult with healthcare providers for personalized advice

`;

    return {
      ...formatted,
      formatted: formatted.formatted + actionPlan
    };
  }
}

// Create singleton instance
const responseFormatterService = new ResponseFormatterService();

export default responseFormatterService;