// Helper functions for migrating existing components to the new design system

export const getButtonVariant = (className) => {
  if (className.includes('bg-blue') || className.includes('bg-primary')) return 'primary';
  if (className.includes('bg-green') || className.includes('bg-success')) return 'success';
  if (className.includes('bg-red') || className.includes('bg-error')) return 'error';
  if (className.includes('bg-yellow') || className.includes('bg-warning')) return 'warning';
  if (className.includes('glass')) return 'secondary';
  if (className.includes('medical')) return 'medical';
  return 'primary';
};

export const getButtonSize = (className) => {
  if (className.includes('text-xs') || className.includes('py-1')) return 'xs';
  if (className.includes('text-sm') || className.includes('py-2')) return 'sm';
  if (className.includes('text-lg') || className.includes('py-4')) return 'lg';
  if (className.includes('text-xl') || className.includes('py-5')) return 'xl';
  return 'md';
};

export const extractIconFromEmoji = (text) => {
  const emojiMap = {
    '🩺': 'stethoscope',
    '💊': 'pill',
    '❤️': 'heart',
    '🧠': 'brain',
    '🌡️': 'thermometer',
    '💉': 'syringe',
    '🩹': 'bandage',
    '🔬': 'microscope',
    '🧬': 'dna',
    '🚑': 'ambulance',
    '🏥': 'hospital',
    '👨‍⚕️': 'doctor',
    '👩‍⚕️': 'nurse',
    '😷': 'mask',
    '🦷': 'tooth',
    '🦴': 'bone',
    '🫁': 'lungs',
    '🫃': 'stomach',
  };
  
  return emojiMap[text] || null;
};

// Color mapping from old system to new system
export const mapOldColorToNew = (oldColor) => {
  const colorMap = {
    'blue-600': 'primary-500',
    'blue-500': 'primary-500',
    'blue-700': 'primary-600',
    'green-600': 'accent-500',
    'green-500': 'accent-500',
    'green-700': 'accent-600',
    'gray-600': 'textSubtle-800',
    'gray-700': 'textMain-900',
    'gray-800': 'textMain-900',
    'gray-900': 'textMain-900',
    'white': 'background-50',
  };
  
  return colorMap[oldColor] || oldColor;
};

// Helper to convert old button classes to new Button component props
export const convertButtonProps = (className, children) => {
  const variant = getButtonVariant(className);
  const size = getButtonSize(className);
  const fullWidth = className.includes('w-full');
  const medical = className.includes('medical') || children?.toString().includes('🩺');
  
  return {
    variant,
    size,
    fullWidth,
    medical,
  };
};

// Helper to identify components that should use medical styling
export const shouldUseMedicalStyling = (content) => {
  const medicalKeywords = [
    'symptom', 'medical', 'health', 'doctor', 'patient', 'diagnosis',
    'medication', 'treatment', 'hospital', 'clinic', 'prescription',
    'vital', 'blood', 'pressure', 'heart', 'pulse', 'temperature'
  ];
  
  const contentLower = content?.toString().toLowerCase() || '';
  return medicalKeywords.some(keyword => contentLower.includes(keyword));
};