import { useEffect, useState, useRef, useCallback } from "react";
import { motion } from "framer-motion";

export default function Meditation({ isOpen, onClose, darkMode }) {
  const [duration, setDuration] = useState(5);
  const [secondsLeft, setSecondsLeft] = useState(null);
  const [isRunning, setIsRunning] = useState(false);

  const intervalRef = useRef(null);
  const audioRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const startMeditation = () => {
    if (duration > 0) {
      setSecondsLeft(duration * 60);
      setIsRunning(true);
      if (audioRef.current) {
        audioRef.current.play().catch(() => {});
      }
    }
  };

  useEffect(() => {
    if (!isRunning) return;

    intervalRef.current = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          clearInterval(intervalRef.current);
          if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current.currentTime = 0;
          }
          setIsRunning(false);
          onClose();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(intervalRef.current);
  }, [isRunning, onClose]);

  useEffect(() => {
    if (!isRunning && audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
  }, [isRunning]);

  useEffect(() => {
    function onKeyDown(e) {
      if (e.key === "Escape" && isOpen) {
        if (audioRef.current) {
          audioRef.current.pause();
          audioRef.current.currentTime = 0;
        }
        clearInterval(intervalRef.current);
        setIsRunning(false);
        onClose();
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [isOpen, onClose]);

  const togglePause = useCallback(() => {
    if (isRunning) {
      clearInterval(intervalRef.current);
      setIsRunning(false);
      if (audioRef.current) audioRef.current.pause();
    } else if (secondsLeft > 0) {
      setIsRunning(true);
      if (audioRef.current) audioRef.current.play().catch(() => {});
    }
  }, [isRunning, secondsLeft]);

  if (!isOpen) return null;



  const formatTime = (secs) => {
    const m = Math.floor(secs / 60)
      .toString()
      .padStart(2, "0");
    const s = (secs % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  };

  return (
    <div className="flex-1 flex flex-col bg-gray-50 dark:bg-gray-900">
      <div className="flex-1 flex items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="bg-white dark:bg-gray-800 rounded-3xl shadow-2xl p-8 w-full max-w-lg border border-gray-200 dark:border-gray-700 relative"
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="bg-gray-800 rounded-full w-12 h-12 flex items-center justify-center shadow-lg">
                <span className="text-2xl">🧘</span>
              </div>
              <div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Meditation
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Find your inner peace
                </p>
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => {
                if (audioRef.current) {
                  audioRef.current.pause();
                  audioRef.current.currentTime = 0;
                }
                clearInterval(intervalRef.current);
                setIsRunning(false);
                onClose();
              }}
              className="p-2 rounded-xl text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 
                hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </motion.button>
          </div>

          {!isRunning ? (
            <div className="text-center">
              {/* Duration Selector */}
              <div className="mb-8">
                <label className="block text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Choose your meditation duration
                </label>
                <div className="bg-gray-100 dark:bg-gray-800 
                  rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
                  <input
                    id="meditation-timer"
                    type="range"
                    min="1"
                    max="60"
                    value={duration}
                    onChange={(e) => setDuration(parseInt(e.target.value))}
                    ref={inputRef}
                    className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer 
                      dark:bg-gray-700 slider"
                    style={{
                      background: `linear-gradient(to right, #374151 0%, #374151 ${(duration/60)*100}%, #e5e7eb ${(duration/60)*100}%, #e5e7eb 100%)`
                    }}
                  />
                  <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mt-2">
                    <span>1 min</span>
                    <span className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                      {duration} minutes
                    </span>
                    <span>60 min</span>
                  </div>
                </div>
              </div>

              {/* Quick Duration Buttons */}
              <div className="grid grid-cols-3 gap-3 mb-8">
                {[5, 10, 15].map((mins) => (
                  <motion.button
                    key={mins}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setDuration(mins)}
                    className={`py-3 px-4 rounded-xl font-medium transition-all duration-200 ${
                      duration === mins
                        ? 'bg-gray-800 text-white shadow-lg'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                    }`}
                  >
                    {mins}m
                  </motion.button>
                ))}
              </div>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={startMeditation}
                className="w-full py-4 bg-gray-800 hover:bg-gray-900 text-white 
                  rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl transition-all duration-200
                  focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              >
                Begin Meditation
              </motion.button>
            </div>
          ) : (
            <div className="text-center">
              {/* Timer Display */}
              <div className="mb-8">
                <div className="bg-gray-100 dark:bg-gray-800 
                  rounded-3xl p-8 border border-gray-200 dark:border-gray-700 mb-6">
                  <div className="text-7xl font-mono font-bold text-gray-800 dark:text-gray-200 mb-4">
                    {formatTime(secondsLeft)}
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-gray-800 dark:bg-gray-600 h-2 rounded-full transition-all duration-1000"
                      style={{ width: `${((duration * 60 - secondsLeft) / (duration * 60)) * 100}%` }}
                    ></div>
                  </div>
                </div>
                <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
                  Breathe deeply and focus on the present moment
                </p>
              </div>

              {/* Controls */}
              <div className="flex gap-4">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={togglePause}
                  className="flex-1 py-3 bg-gray-800 hover:bg-gray-900 text-white 
                    rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-200
                    focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                >
                  {isRunning ? "⏸ Pause" : "▶️ Resume"}
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => {
                    clearInterval(intervalRef.current);
                    setIsRunning(false);
                    setSecondsLeft(null);
                    if (audioRef.current) {
                      audioRef.current.pause();
                      audioRef.current.currentTime = 0;
                    }
                    onClose();
                  }}
                  className="flex-1 py-3 bg-gray-600 hover:bg-gray-700 text-white 
                    rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-200
                    focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                >
                  Stop
                </motion.button>
              </div>

              <audio
                ref={audioRef}
                src="/music/meditation3.mp3"
                autoPlay
                loop
                muted={false}
                style={{ display: "none" }}
              />
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
