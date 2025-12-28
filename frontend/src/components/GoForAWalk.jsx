import { useState, useEffect, useRef, useCallback } from "react";
import { motion } from "framer-motion";

const tips = [
  "Walk briskly to boost your heart health.",
  "Keep a steady pace and breathe deeply.",
  "Walking outdoors improves mood and creativity.",
  "Try walking in nature for extra relaxation.",
  "Use your walk time to clear your mind.",
  "Good posture while walking helps prevent aches.",
  "Walk for at least 30 minutes daily for health benefits.",
  "Walking with a friend can make it more enjoyable.",
  "Remember to stretch gently before and after your walk.",
];

export default function GoForAWalk({ darkMode }) {
  // State variables
  const [seconds, setSeconds] = useState(0);
  const [running, setRunning] = useState(false);
  const [totalSeconds, setTotalSeconds] = useState(0);
  const [tipIndex, setTipIndex] = useState(0);
  const [tipFading, setTipFading] = useState(false);

  const tipTimeoutRef = useRef(null);

  useEffect(() => {
    const stored = localStorage.getItem("totalWalkSeconds");
    if (stored) {
      setTotalSeconds(parseInt(stored, 10));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem("totalWalkSeconds", totalSeconds);
  }, [totalSeconds]);

  useEffect(() => {
    let interval = null;
    if (running) {
      interval = setInterval(() => setSeconds((s) => s + 1), 1000);
    } else if (!running && seconds !== 0) {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [running, seconds]);

  useEffect(() => {
    if (!running && seconds !== 0) {
      setTotalSeconds((prev) => prev + seconds);
      setSeconds(0);
    }
  }, [running, seconds]);

  const formatTime = (sec) => {
    const m = Math.floor(sec / 60)
      .toString()
      .padStart(2, "0");
    const s = (sec % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  };

  const nextTip = useCallback(() => {
    if (tipTimeoutRef.current) return;
    setTipFading(true);
    tipTimeoutRef.current = setTimeout(() => {
      let next = Math.floor(Math.random() * tips.length);
      while (next === tipIndex) {
        next = Math.floor(Math.random() * tips.length);
      }
      setTipIndex(next);
      setTipFading(false);
      tipTimeoutRef.current = null;
    }, 300);
  }, [tipIndex]);

  const resetTracking = useCallback(() => {
    setSeconds(0);
    setTotalSeconds(0);
    setRunning(false);
    localStorage.removeItem("totalWalkSeconds");
  }, []);



  return (
    <div className="flex-1 flex flex-col bg-gray-50 dark:bg-gray-900">
      <div className="flex-1 flex items-start justify-center p-8 overflow-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="bg-white dark:bg-gray-800 rounded-3xl shadow-2xl p-8 w-full max-w-2xl border border-gray-200 dark:border-gray-700"
        >
          {/* Header */}
          <div className="flex items-center justify-center gap-3 mb-8">
            <div className="bg-gray-800 rounded-full w-16 h-16 flex items-center justify-center shadow-lg">
              <span className="text-3xl">🚶</span>
            </div>
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
                Go For a Walk
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Take a mindful break and move your body
              </p>
            </div>
          </div>

          {/* Timer Display */}
          <div className="text-center mb-8">
            <div className="bg-gradient-to-r from-orange-100 to-yellow-100 dark:from-orange-900 dark:to-yellow-900 
              rounded-3xl p-8 border border-orange-200 dark:border-orange-700 mb-6">
              <div className="text-6xl font-mono font-bold text-orange-600 dark:text-orange-400 mb-4">
                {formatTime(seconds)}
              </div>
              <p className="text-gray-600 dark:text-gray-400">
                {running ? "Walking in progress..." : "Ready to start your walk"}
              </p>
            </div>
          </div>

          {/* Controls */}
          <div className="flex justify-center gap-4 mb-8">
            {!running ? (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setRunning(true)}
                className="flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-500 
                  text-white rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl transition-all duration-200
                  focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z"/>
                </svg>
                Start Walk
              </motion.button>
            ) : (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setRunning(false)}
                className="flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-red-500 to-pink-500 
                  text-white rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl transition-all duration-200
                  focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                </svg>
                Stop Walk
              </motion.button>
            )}
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={resetTracking}
              className="flex items-center gap-2 px-6 py-4 bg-gradient-to-r from-gray-500 to-gray-600 
                text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M4 12a8 8 0 018-8V2.5L14.5 5 12 7.5V6a6 6 0 100 12 6 6 0 006-6h2a8 8 0 01-16 0z"/>
              </svg>
              Reset
            </motion.button>
          </div>

          {/* Total Time */}
          <div className="text-center mb-8">
            <div className="bg-gradient-to-r from-blue-100 to-indigo-100 dark:from-blue-900 dark:to-indigo-900 
              rounded-2xl p-6 border border-blue-200 dark:border-blue-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Total Walking Time
              </h3>
              <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                {formatTime(totalSeconds)}
              </div>
            </div>
          </div>

          {/* Walking Tips */}
          <div className="bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900 dark:to-pink-900 
            rounded-2xl p-6 border border-purple-200 dark:border-purple-700">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-2xl">💡</span>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Walking Tip
              </h3>
            </div>
            <motion.p 
              key={tipIndex}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="text-gray-700 dark:text-gray-300 mb-4 text-lg leading-relaxed"
            >
              {tips[tipIndex]}
            </motion.p>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={nextTip}
              className="px-4 py-2 bg-purple-500 text-white rounded-xl font-medium 
                hover:bg-purple-600 transition-all duration-200 shadow-md hover:shadow-lg
                focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
            >
              Next Tip
            </motion.button>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
