import ReactMarkdown from 'react-markdown';

/**
 * Simple Formatted Message Component
 * Direct, inline formatting without external dependencies
 */
const SimpleFormattedMessage = ({ content }) => {
  // Direct formatting function
  const formatContent = (text) => {
    if (!text) return text;
    
    let formatted = text.trim();
    
    // Step 1: Remove AI references
    formatted = formatted.replace(/As a supportive assistant,?\s*/gi, '');
    formatted = formatted.replace(/As an AI,?\s*/gi, '');
    
    // Step 2: Add heading based on content
    if (formatted.toLowerCase().includes('mental') || formatted.toLowerCase().includes('trauma')) {
      formatted = `## 🧠 **Mental Health Support**\n\n${formatted}`;
    } else {
      formatted = `## 🩺 **Medical Information**\n\n${formatted}`;
    }
    
    // Step 3: Convert numbered lists to bullet points
    formatted = formatted.replace(/(\d+)\.\s*([^\n]+)/g, '\n• **$2**');
    
    // Step 4: Format "Here are" statements
    formatted = formatted.replace(/Here are some ([^:]+):/gi, '\n## 💡 **$1**\n');
    
    // Step 5: Highlight key terms
    const terms = ['traumatized', 'anxiety', 'stress', 'emotions', 'feelings', 'mental health', 'professional', 'self-care'];
    terms.forEach(term => {
      const regex = new RegExp(`\\b(${term})\\b`, 'gi');
      formatted = formatted.replace(regex, '**$1**');
    });
    
    // Step 6: Add disclaimer
    formatted += `\n\n---\n\n> 💡 **Medical Disclaimer:** This information is for educational purposes only. Always consult with a healthcare provider for medical concerns.`;
    
    return formatted;
  };

  const formattedContent = formatContent(content);

  // Custom markdown components
  const components = {
    h2: ({ children }) => (
      <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-3 mt-4 flex items-center gap-2 border-l-4 border-blue-500 pl-3">
        {children}
      </h2>
    ),
    p: ({ children }) => (
      <p className="text-gray-700 dark:text-gray-300 mb-3 leading-relaxed">
        {children}
      </p>
    ),
    ul: ({ children }) => (
      <ul className="space-y-2 mb-4">{children}</ul>
    ),
    li: ({ children }) => (
      <li className="flex items-start gap-3 text-gray-700 dark:text-gray-300">
        <span className="text-blue-500 mt-1">•</span>
        <span>{children}</span>
      </li>
    ),
    strong: ({ children }) => (
      <strong className="font-semibold text-gray-900 dark:text-white bg-blue-50 dark:bg-blue-900/30 px-1 py-0.5 rounded">
        {children}
      </strong>
    ),
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-900/20 p-4 my-4 rounded-r-lg">
        <div className="text-blue-800 dark:text-blue-200">{children}</div>
      </blockquote>
    )
  };

  return (
    <div className="space-y-4">
      <div className="prose prose-sm dark:prose-invert max-w-none">
        <ReactMarkdown components={components}>
          {formattedContent}
        </ReactMarkdown>
      </div>
    </div>
  );
};

export default SimpleFormattedMessage;