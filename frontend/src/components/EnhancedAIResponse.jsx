import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { 
  FiInfo, FiAlertTriangle, FiCheckCircle, FiXCircle, 
  FiHeart, FiActivity, FiShield, FiBook, FiStar,
  FiClock, FiTrendingUp, FiTarget, FiZap
} from 'react-icons/fi';

/**
 * Enhanced AI Response Component
 * Provides beautifully formatted, structured AI responses with visual hierarchy
 */
const EnhancedAIResponse = ({ content, isTyping = false, onComplete }) => {
  const [processedContent, setProcessedContent] = useState('');
  const [sections, setSections] = useState([]);
  const [currentSection, setCurrentSection] = useState(0);

  useEffect(() => {
    if (content && !isTyping) {
      const formatted = formatAIResponse(content);
      setProcessedContent(formatted.content);
      setSections(formatted.sections);
    }
  }, [content, isTyping]);

  // Format AI response with enhanced structure
  const formatAIResponse = (text) => {
    let formattedText = text;
    const sections = [];
    let sectionIndex = 0;

    // First, let's break the text into sentences for better processing
    const sentences = text.split(/(?<=[.!?])\s+/);
    
    // Enhanced formatting with more comprehensive patterns
    let processedSentences = [];
    let currentSection = null;
    
    sentences.forEach((sentence, idx) => {
      const lowerSentence = sentence.toLowerCase();
      
      // Check for different types of content
      if (lowerSentence.includes('symptom') || lowerSentence.includes('feel') || lowerSentence.includes('experience')) {
        if (currentSection !== 'symptoms') {
          processedSentences.push('\n## 🩺 **Symptoms & Signs**\n');
          currentSection = 'symptoms';
          sections.push({ type: 'symptoms', index: sectionIndex++, content: sentence });
        }
        processedSentences.push(`• **${sentence.trim()}**\n`);
      }
      else if (lowerSentence.includes('treatment') || lowerSentence.includes('medication') || lowerSentence.includes('therapy')) {
        if (currentSection !== 'treatment') {
          processedSentences.push('\n## 💊 **Treatment Options**\n');
          currentSection = 'treatment';
          sections.push({ type: 'treatment', index: sectionIndex++, content: sentence });
        }
        processedSentences.push(`• **${sentence.trim()}**\n`);
      }
      else if (lowerSentence.includes('prevent') || lowerSentence.includes('avoid') || lowerSentence.includes('self-care')) {
        if (currentSection !== 'prevention') {
          processedSentences.push('\n## 🛡️ **Prevention & Self-Care**\n');
          currentSection = 'prevention';
          sections.push({ type: 'prevention', index: sectionIndex++, content: sentence });
        }
        processedSentences.push(`• **${sentence.trim()}**\n`);
      }
      else if (lowerSentence.includes('important') || lowerSentence.includes('seek') || lowerSentence.includes('professional') || lowerSentence.includes('emergency')) {
        if (currentSection !== 'warning') {
          processedSentences.push('\n## ⚠️ **Important Information**\n');
          currentSection = 'warning';
          sections.push({ type: 'warning', index: sectionIndex++, content: sentence });
        }
        processedSentences.push(`> **${sentence.trim()}**\n`);
      }
      else if (lowerSentence.includes('suggest') || lowerSentence.includes('recommend') || lowerSentence.includes('try') || lowerSentence.includes('consider')) {
        if (currentSection !== 'recommendations') {
          processedSentences.push('\n## ✅ **Recommendations**\n');
          currentSection = 'recommendations';
          sections.push({ type: 'recommendations', index: sectionIndex++, content: sentence });
        }
        processedSentences.push(`• **${sentence.trim()}**\n`);
      }
      else {
        // General content - add some basic formatting
        if (idx === 0) {
          // First sentence as introduction
          processedSentences.push(`## 🩺 **Medical Assessment**\n\n${sentence.trim()}\n`);
        } else {
          processedSentences.push(`${sentence.trim()}\n\n`);
        }
      }
    });

    // If no sections were detected, apply basic formatting
    if (sections.length === 0) {
      formattedText = applyBasicFormatting(text);
    } else {
      formattedText = processedSentences.join('');
    }

    // Add general formatting improvements
    formattedText = enhanceGeneralFormatting(formattedText);

    return {
      content: formattedText,
      sections
    };
  };

  // Apply basic formatting when no specific sections are detected
  const applyBasicFormatting = (text) => {
    let formatted = text;
    
    // Add main heading
    formatted = `## 🩺 **Medical Information**\n\n${formatted}`;
    
    // Format numbered lists
    formatted = formatted.replace(/(\d+)\.\s+([^\n]+)/g, '\n• **$2**');
    
    // Format common medical terms
    const medicalTerms = ['symptoms', 'treatment', 'medication', 'diagnosis', 'condition', 'therapy'];
    medicalTerms.forEach(term => {
      const regex = new RegExp(`\\b(${term})\\b`, 'gi');
      formatted = formatted.replace(regex, '**$1**');
    });
    
    // Add line breaks for better readability
    formatted = formatted.replace(/\. ([A-Z])/g, '.\n\n$1');
    
    return formatted;
  };

  // Format list items for better readability
  const formatListItems = (text) => {
    // Split by common separators and format as list
    const items = text.split(/[,;]|and(?=\s)|or(?=\s)/)
      .map(item => item.trim())
      .filter(item => item.length > 0);

    if (items.length > 1) {
      return items.map(item => `• **${item}**`).join('\n');
    }
    return `**${text.trim()}**`;
  };

  // Enhance general formatting
  const enhanceGeneralFormatting = (text) => {
    let enhanced = text;

    // Add emphasis to important medical terms
    const medicalTerms = [
      'diagnosis', 'treatment', 'medication', 'symptoms', 'condition',
      'doctor', 'physician', 'healthcare', 'medical', 'emergency',
      'urgent', 'serious', 'chronic', 'acute', 'infection', 'therapy',
      'professional', 'traumatized', 'anxiety', 'depression', 'stress',
      'mental health', 'self-care', 'coping', 'support'
    ];

    medicalTerms.forEach(term => {
      const regex = new RegExp(`\\b(${term})\\b`, 'gi');
      enhanced = enhanced.replace(regex, '**$1**');
    });

    // Format dosages and measurements
    enhanced = enhanced.replace(/(\d+)\s*(mg|ml|mcg|g|kg|lbs?|oz)/gi, '**$1 $2**');

    // Format time periods
    enhanced = enhanced.replace(/(\d+)\s*(days?|weeks?|months?|hours?|minutes?)/gi, '**$1 $2**');

    // Format numbered lists more aggressively
    enhanced = enhanced.replace(/(\d+)\.\s*\*\*([^*]+)\*\*/g, '\n• **$2**');
    enhanced = enhanced.replace(/(\d+)\.\s*([^.\n]+)/g, '\n• **$2**');

    // Format "Here are" lists
    enhanced = enhanced.replace(/Here are some ([^:]+):/gi, '\n## 💡 **$1:**\n');
    enhanced = enhanced.replace(/Here are ([^:]+):/gi, '\n## 💡 **$1:**\n');

    // Format "Remember" statements
    enhanced = enhanced.replace(/Remember[,:]\s*/gi, '\n> 💭 **Remember:** ');

    // Format "Important" statements
    enhanced = enhanced.replace(/Important[,:]\s*/gi, '\n> ⚠️ **Important:** ');

    // Add line breaks for better readability
    enhanced = enhanced.replace(/\.\s+([A-Z])/g, '.\n\n$1');
    enhanced = enhanced.replace(/\?\s+([A-Z])/g, '?\n\n$1');
    enhanced = enhanced.replace(/!\s+([A-Z])/g, '!\n\n$1');

    // Clean up extra line breaks
    enhanced = enhanced.replace(/\n{3,}/g, '\n\n');

    return enhanced.trim();
  };

  // Custom markdown components with medical styling
  const markdownComponents = {
    h1: ({ children }) => (
      <motion.h1 
        className="text-2xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
      >
        {children}
      </motion.h1>
    ),
    h2: ({ children }) => (
      <motion.h2 
        className="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-3 mt-6 flex items-center gap-2 border-l-4 border-blue-500 pl-3"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        {children}
      </motion.h2>
    ),
    h3: ({ children }) => (
      <motion.h3 
        className="text-lg font-medium text-gray-700 dark:text-gray-200 mb-2 mt-4"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        {children}
      </motion.h3>
    ),
    p: ({ children }) => (
      <motion.p 
        className="text-gray-700 dark:text-gray-300 mb-3 leading-relaxed"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        {children}
      </motion.p>
    ),
    ul: ({ children }) => (
      <motion.ul 
        className="space-y-2 mb-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        {children}
      </motion.ul>
    ),
    li: ({ children }) => (
      <motion.li 
        className="flex items-start gap-3 text-gray-700 dark:text-gray-300"
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
      >
        <span className="text-blue-500 mt-1">•</span>
        <span>{children}</span>
      </motion.li>
    ),
    strong: ({ children }) => (
      <strong className="font-semibold text-gray-900 dark:text-white bg-blue-50 dark:bg-blue-900/30 px-1 py-0.5 rounded">
        {children}
      </strong>
    ),
    em: ({ children }) => (
      <em className="italic text-blue-600 dark:text-blue-400 font-medium">
        {children}
      </em>
    ),
    blockquote: ({ children }) => (
      <motion.blockquote 
        className="border-l-4 border-orange-500 bg-orange-50 dark:bg-orange-900/20 p-4 my-4 rounded-r-lg"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-start gap-3">
          <FiAlertTriangle className="text-orange-500 mt-1 flex-shrink-0" size={20} />
          <div className="text-orange-800 dark:text-orange-200">
            {children}
          </div>
        </div>
      </motion.blockquote>
    ),
    code: ({ inline, children }) => {
      if (inline) {
        return (
          <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-sm font-mono text-blue-600 dark:text-blue-400">
            {children}
          </code>
        );
      }
      return (
        <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg overflow-x-auto my-4">
          <code className="text-sm font-mono text-gray-800 dark:text-gray-200">
            {children}
          </code>
        </pre>
      );
    }
  };

  // Section icons mapping
  const getSectionIcon = (type) => {
    const icons = {
      symptoms: FiActivity,
      causes: FiInfo,
      treatment: FiHeart,
      prevention: FiShield,
      warning: FiAlertTriangle,
      recommendations: FiCheckCircle,
      default: FiBook
    };
    return icons[type] || icons.default;
  };

  // Section color mapping
  const getSectionColor = (type) => {
    const colors = {
      symptoms: 'text-red-500',
      causes: 'text-blue-500',
      treatment: 'text-green-500',
      prevention: 'text-purple-500',
      warning: 'text-orange-500',
      recommendations: 'text-teal-500',
      default: 'text-gray-500'
    };
    return colors[type] || colors.default;
  };

  if (isTyping) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          >
            <FiZap className="text-blue-500" size={20} />
          </motion.div>
          <span className="text-gray-600 dark:text-gray-400">
            Analyzing and formatting response...
          </span>
        </div>
        
        {/* Skeleton loading */}
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <motion.div
              key={i}
              className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"
              style={{ width: `${Math.random() * 40 + 60}%` }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: i * 0.2 }}
            />
          ))}
        </div>
      </div>
    );
  }

  // Get the content to display
  const displayContent = processedContent || content || 'No content available';

  return (
    <motion.div
      className="space-y-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      onAnimationComplete={onComplete}
    >
      {/* Section navigation */}
      {sections.length > 0 && (
        <motion.div
          className="flex flex-wrap gap-2 mb-6 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <span className="text-sm font-medium text-gray-600 dark:text-gray-400 mr-2">
            Quick Navigation:
          </span>
          {sections.map((section, index) => {
            const IconComponent = getSectionIcon(section.type);
            const colorClass = getSectionColor(section.type);
            
            return (
              <motion.button
                key={index}
                onClick={() => setCurrentSection(index)}
                className={`flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium transition-all ${
                  currentSection === index
                    ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                    : 'hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400'
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <IconComponent className={colorClass} size={12} />
                <span className="capitalize">{section.type}</span>
              </motion.button>
            );
          })}
        </motion.div>
      )}

      {/* Main content */}
      <motion.div
        className="prose prose-sm dark:prose-invert max-w-none"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <ReactMarkdown components={markdownComponents}>
          {displayContent}
        </ReactMarkdown>
      </motion.div>

      {/* Medical disclaimer */}
      <motion.div
        className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.8 }}
      >
        <div className="flex items-start gap-3">
          <FiInfo className="text-blue-500 mt-0.5 flex-shrink-0" size={16} />
          <div className="text-sm text-blue-800 dark:text-blue-200">
            <p className="font-medium mb-1">Medical Disclaimer</p>
            <p>
              This information is for educational purposes only and should not replace 
              professional medical advice. Always consult with a healthcare provider 
              for medical concerns.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Action buttons */}
      <motion.div
        className="flex flex-wrap gap-2 mt-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 1 }}
      >
        <button className="flex items-center gap-2 px-3 py-2 text-sm bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors">
          <FiCheckCircle size={14} />
          Helpful
        </button>
        <button className="flex items-center gap-2 px-3 py-2 text-sm bg-gray-50 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
          <FiBook size={14} />
          Learn More
        </button>
        <button className="flex items-center gap-2 px-3 py-2 text-sm bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors">
          <FiTarget size={14} />
          Follow Up
        </button>
      </motion.div>
    </motion.div>
  );
};

export default EnhancedAIResponse;