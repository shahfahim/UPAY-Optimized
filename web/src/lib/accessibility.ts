/**
 * Accessibility & UX Module
 * Provides Voice interaction capabilities for low-income and low-literacy users.
 * Uses the Web Speech API for Text-to-Speech (TTS) configured for Bengali (bn-BD).
 */

// Check if the SpeechSynthesis API is supported in the current environment
const isSpeechSupported = (): boolean => {
  return typeof window !== 'undefined' && 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window;
};

/**
 * Speaks the given text in Bengali.
 * @param text The text to be spoken.
 */
export const speakBangla = (text: string): void => {
  if (!isSpeechSupported()) {
    console.warn('Text-to-Speech is not supported in this browser. Voice interaction disabled.');
    return;
  }

  try {
    // Stop any ongoing speech before starting a new one to avoid overlapping
    stopSpeaking();

    const utterance = new SpeechSynthesisUtterance(text);
    
    // Configure for Bengali (Bangladesh)
    utterance.lang = 'bn-BD';
    
    // Adjust rate and pitch for better UX among target users
    utterance.rate = 0.9; // Slightly slower for better comprehension
    utterance.pitch = 1.0;

    // Error handling for the utterance itself
    utterance.onerror = (event) => {
      console.error('Speech synthesis error occurred:', event.error);
    };

    // Speak the text
    window.speechSynthesis.speak(utterance);
  } catch (error) {
    console.error('An unexpected error occurred while attempting to speak:', error);
  }
};

/**
 * Stops any ongoing speech synthesis.
 */
export const stopSpeaking = (): void => {
  if (!isSpeechSupported()) {
    return;
  }

  try {
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
    }
  } catch (error) {
    console.error('An error occurred while trying to stop speech synthesis:', error);
  }
};
