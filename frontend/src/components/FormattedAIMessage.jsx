import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

/**
 * Formatted AI Message Component
 * Ensures all AI responses are properly formatted with medical structure
 */
const FormattedAIMessage = ({ content }) => {
    const [formattedContent, setFormattedContent] = useState('');

    useEffect(() => {
        if (content) {
            const formatted = formatMessage(content);
            console.log('🎨 Formatting AI response...');
            console.log('Original:', content.substring(0, 100) + '...');
            console.log('Formatted:', formatted.substring(0, 200) + '...');
            setFormattedContent(formatted);
        }
    }, [content]);

    // Simple, reliable formatting function
    const formatMessage = (text) => {
        if (!text) return text;
        
        let formatted = text.trim();
        
        // Remove AI assistant references
        formatted = formatted.replace(/As a supportive assistant,?\s*/gi, '');
        formatted = formatted.replace(/As an AI,?\s*/gi, '');
        formatted = formatted.replace(/I'm here to support you,?\s*/gi, '');
        
        // Add main heading based on content
        if (formatted.toLowerCase().includes('mental') || formatted.toLowerCase().includes('trauma') || formatted.toLowerCase().includes('anxiety')) {
            formatted = `## 🧠 **Mental Health Support**\n\n${formatted}`;
        } else if (formatted.toLowerCase().includes('symptom')) {
            formatted = `## 🩺 **Symptom Information**\n\n${formatted}`;
        } else if (formatted.toLowerCase().includes('treatment') || formatted.toLowerCase().includes('medication')) {
            formatted = `## 💊 **Treatment Information**\n\n${formatted}`;
        } else {
            formatted = `## 🩺 **Medical Information**\n\n${formatted}`;
        }
        
        // Format numbered lists to bullet points
        formatted = formatted.replace(/(\d+)\.\s*([^:\n]+):/g, '\n### 💡 **$2**\n');
        formatted = formatted.replace(/(\d+)\.\s*([^\n]+)/g, '\n• **$2**');
        
        // Format "Here are" statements
        formatted = formatted.replace(/Here are some ([^:]+):/gi, '\n## 💡 **$1**\n');
        formatted = formatted.replace(/Here are ([^:]+):/gi, '\n## 💡 **$1**\n');
        
        // Highlight important medical terms
        const medicalTerms = [
            'traumatized', 'trauma', 'anxiety', 'depression', 'stress', 'emotions', 'feelings',
            'mental health', 'professional', 'therapy', 'counseling', 'support',
            'symptoms', 'treatment', 'medication', 'self-care', 'coping', 'healing'
        ];
        
        medicalTerms.forEach(term => {
            const regex = new RegExp(`\\b(${term})\\b`, 'gi');
            formatted = formatted.replace(regex, '**$1**');
        });
        
        // Format important statements
        formatted = formatted.replace(/Remember[,:]\s*/gi, '\n> 💭 **Remember:** ');
        formatted = formatted.replace(/Important[,:]\s*/gi, '\n> ⚠️ **Important:** ');
        
        // Add medical disclaimer
        formatted += `\n\n---\n\n> 💡 **Medical Disclaimer:** This information is for educational purposes only and should not replace **professional** medical advice. Always consult with a healthcare provider for medical concerns.`;
        
        // Clean up spacing
        formatted = formatted.replace(/\n{3,}/g, '\n\n');
        
        return formatted.trim();
    };



    // Custom markdown components for better styling
    const markdownComponents = {
        h1: ({ children }) => (
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                {children}
            </h1>
        ),
        h2: ({ children }) => (
            <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-3 mt-6 flex items-center gap-2 border-l-4 border-blue-500 pl-3">
                {children}
            </h2>
        ),
        h3: ({ children }) => (
            <h3 className="text-lg font-medium text-gray-700 dark:text-gray-200 mb-2 mt-4">
                {children}
            </h3>
        ),
        p: ({ children }) => (
            <p className="text-gray-700 dark:text-gray-300 mb-3 leading-relaxed">
                {children}
            </p>
        ),
        ul: ({ children }) => (
            <ul className="space-y-2 mb-4">
                {children}
            </ul>
        ),
        li: ({ children }) => (
            <li className="flex items-start gap-3 text-gray-700 dark:text-gray-300">
                <span className="text-blue-500 mt-1 flex-shrink-0">•</span>
                <span>{children}</span>
            </li>
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
            <blockquote className="border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-900/20 p-4 my-4 rounded-r-lg">
                <div className="text-blue-800 dark:text-blue-200">
                    {children}
                </div>
            </blockquote>
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

    // Ensure we always have content to display
    const displayContent = formattedContent || content || 'No content available';

    return (
        <motion.div
            className="space-y-4"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
        >
            {/* Debug info (remove in production) */}
            {process.env.NODE_ENV === 'development' && (
                <div className="text-xs text-gray-500 bg-yellow-50 p-2 rounded">
                    🎨 FormattedAIMessage active - Content length: {content?.length || 0}
                </div>
            )}
            
            {/* Main content */}
            <div className="prose prose-sm dark:prose-invert max-w-none">
                <ReactMarkdown components={markdownComponents}>
                    {displayContent}
                </ReactMarkdown>
            </div>


        </motion.div>
    );
};

export default FormattedAIMessage;