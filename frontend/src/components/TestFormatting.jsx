import FormattedAIMessage from './FormattedAIMessage';

const TestFormatting = () => {
  const testMessage = `I'm so sorry to hear that you're feeling traumatized after watching a horror movie. It's completely normal to feel that way, especially if the movie triggered some intense or disturbing scenes. As a supportive assistant, I want to remind you that you're not alone in feeling this way. Many people experience a phenomenon called "post-traumatic movie experience" or "PTME," where they feel a strong emotional reaction to a scary or disturbing movie. Here are some suggestions that might help you cope with your feelings: 1. Allow yourself to feel your emotions: It's okay to acknowledge and process your feelings. Give yourself permission to feel scared, anxious, or upset, and don't try to suppress them. 2. Take a break from the movie: If you're feeling overwhelmed, take a break from thinking about the movie. Engage in something calming, like taking a warm bath, listening to soothing music, or practicing deep breathing exercises. 3. Talk to someone: Reach out to a trusted friend, family member, or mental health professional. Sharing your feelings with someone who cares about you can help you feel supported and validated. 4. Practice self-care: Engage in activities that bring you comfort and relaxation, such as exercise, meditation, or creative pursuits. 5. Remember that it's just a movie: Try to separate the movie from your real life. Remind yourself that it's just a fictional story, and it's not a reflection of your reality. Remember, I'm here to support you, but I'm not a substitute for professional help. If your feelings of trauma or anxiety persist or worsen, please consider seeking guidance from a mental health professional. How are you feeling right now? Is there anything specific that's bothering you about the movie?`;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Formatting Test</h2>
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border">
        <FormattedAIMessage content={testMessage} />
      </div>
    </div>
  );
};

export default TestFormatting;