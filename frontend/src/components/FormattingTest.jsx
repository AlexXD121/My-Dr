import SimpleFormattedMessage from './SimpleFormattedMessage';

const FormattingTest = () => {
  const testMessage = `I'm so sorry to hear that you're feeling traumatized after watching a horror movie. It's completely normal to feel that way, especially if the movie triggered some intense or disturbing scenes. As a supportive assistant, I want to remind you that you're not alone in feeling this way. Many people experience a phenomenon called "post-traumatic movie experience" or "PTME," where they feel a strong emotional reaction to a scary or disturbing movie. Here are some suggestions that might help you cope with your feelings: 1. Allow yourself to feel your emotions: It's okay to acknowledge and process your feelings. Give yourself permission to feel scared, anxious, or upset, and don't try to suppress them. 2. Take a break from the movie: If you're feeling overwhelmed, take a break from thinking about the movie. Engage in something calming, like taking a warm bath, listening to soothing music, or practicing deep breathing exercises. 3. Talk to someone: Reach out to a trusted friend, family member, or mental health professional. Sharing your feelings with someone who cares about you can help you feel supported and validated. 4. Practice self-care: Engage in activities that bring you comfort and relaxation, such as exercise, meditation, or creative pursuits. 5. Remember that it's just a movie: Try to separate the movie from your real life. Remind yourself that it's just a fictional story, and it's not a reflection of your reality.`;

  return (
    <div className="p-6 max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-lg">
      <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
        🧪 Formatting Test
      </h2>
      
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">
          Original Message:
        </h3>
        <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded text-sm text-gray-700 dark:text-gray-300">
          {testMessage.substring(0, 200)}...
        </div>
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">
          Formatted Result:
        </h3>
        <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <SimpleFormattedMessage content={testMessage} />
        </div>
      </div>
    </div>
  );
};

export default FormattingTest;