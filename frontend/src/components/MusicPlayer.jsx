import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const musicFiles = [
  "/music/calm1.mp3",
  "/music/calm2.mp3",
  "/music/calm3.mp3",
  "/music/calm4.mp3",
  "/music/calm5.mp3",
];

export default function MusicPlayer({ isOpen, onClose, darkMode }) {
  const [currentTrackIndex, setCurrentTrackIndex] = useState(0);
  const [isMinimized, setIsMinimized] = useState(false);

  useEffect(() => {
    if (isOpen) {
      const randomIndex = Math.floor(Math.random() * musicFiles.length);
      setCurrentTrackIndex(randomIndex);
      setIsMinimized(false);
    } else {
      setCurrentTrackIndex(0);
      setIsMinimized(false);
    }
  }, [isOpen]);

  const nextTrack = () => {
    setCurrentTrackIndex((prev) => (prev + 1) % musicFiles.length);
  };

  const prevTrack = () => {
    setCurrentTrackIndex((prev) =>
      prev === 0 ? musicFiles.length - 1 : prev - 1
    );
  };

  const currentTrack = musicFiles[currentTrackIndex];



  if (!isOpen) return null;

  return (
    <div className="flex-1 flex flex-col bg-gray-50 dark:bg-gray-900">
      <div className="flex-1 flex items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="bg-white dark:bg-gray-800 rounded-3xl shadow-2xl p-8 w-full max-w-md border border-gray-200 dark:border-gray-700"
        >
            {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="bg-gray-800 rounded-full w-12 h-12 flex items-center justify-center shadow-lg">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
                </svg>
              </div>
              <div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Calm Music
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Relaxing sounds for your mind
                </p>
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={onClose}
              className="p-2 rounded-xl text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 
                hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </motion.button>
          </div>

          {/* Track Info */}
          <div className="text-center mb-8">
            <div className="bg-gray-100 dark:bg-gray-800 
              rounded-2xl p-6 mb-6 border border-gray-200 dark:border-gray-700">
              <div className="text-6xl mb-4">🎵</div>
              <h4 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Calm Track {currentTrackIndex + 1}
              </h4>
              <p className="text-gray-600 dark:text-gray-400">
                Peaceful melodies for relaxation
              </p>
            </div>
          </div>

          {/* Audio Player */}
          <div className="mb-8">
            <audio
              key={currentTrack}
              src={currentTrack}
              controls
              autoPlay
              className="w-full rounded-xl shadow-lg focus:outline-none focus:ring-2 focus:ring-gray-500
                accent-gray-800 dark:accent-gray-600"
              style={{
                filter: 'drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1))'
              }}
            />
          </div>

          {/* Controls */}
          <div className="flex justify-center gap-4">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={prevTrack}
              className="flex items-center gap-2 px-6 py-3 bg-gray-800 hover:bg-gray-900 
                text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/>
              </svg>
              Previous
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={nextTrack}
              className="flex items-center gap-2 px-6 py-3 bg-gray-800 hover:bg-gray-900 
                text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            >
              Next
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
              </svg>
            </motion.button>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
