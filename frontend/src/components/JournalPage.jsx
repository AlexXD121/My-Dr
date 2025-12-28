import { useState, useEffect } from "react";
import { collection, addDoc, serverTimestamp } from "firebase/firestore";
import { db } from "../firebase";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";

export default function JournalPage({ darkMode, onClose }) {
  const [entry, setEntry] = useState("");
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [windowHeight, setWindowHeight] = useState(window.innerHeight);
  const [focused, setFocused] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  // Load draft from localStorage on mount
  useEffect(() => {
    const draft = localStorage.getItem("journalDraft");
    if (draft) setEntry(draft);
  }, []);

  // Auto-save draft every 5 seconds if not saved
  useEffect(() => {
    if (saved) return; // don't auto-save once saved
    const interval = setInterval(() => {
      localStorage.setItem("journalDraft", entry);
    }, 5000);
    return () => clearInterval(interval);
  }, [entry, saved]);

  useEffect(() => {
    const handleResize = () => setWindowHeight(window.innerHeight);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const inputBg = darkMode ? "bg-gray-800" : "bg-white";
  const borderColor = darkMode ? "border-gray-600" : "border-gray-300";
  const buttonBg = darkMode
    ? "bg-gray-700 hover:bg-gray-600"
    : "bg-gray-800 hover:bg-gray-900";
  const textColor = darkMode ? "text-gray-100" : "text-gray-900";

  // Calculate max height for container so it fits window but leaves space for header & padding etc
  const containerMaxHeight = windowHeight - 170;

  const saveEntry = async () => {
    if (!entry.trim()) {
      alert("Please write something before saving.");
      return;
    }
    setLoading(true);
    try {
      await addDoc(collection(db, "journalEntries"), {
        text: entry,
        createdAt: serverTimestamp(),
      });
      alert("✅ Your journal entry has been saved!");
      setSaved(true);
      localStorage.removeItem("journalDraft");
    } catch (error) {
      console.error("Error saving entry: ", error);
      alert("❌ Failed to save your entry. Try again.");
    }
    setLoading(false);
  };

  const newEntry = () => {
    setEntry("");
    setSaved(false);
    localStorage.removeItem("journalDraft");
    setShowPreview(false);
  };

  // Character count
  const charCount = entry.length;

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
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="bg-gray-800 rounded-full w-12 h-12 flex items-center justify-center shadow-lg">
                <span className="text-2xl">📝</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Daily Journal
                </h1>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Reflect on your thoughts and feelings
                </p>
              </div>
            </div>

            {onClose && (
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
            )}
          </div>

          {/* Prompts section */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
              Reflection Prompts
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {[
                { emoji: "✨", text: "What good happened today?" },
                { emoji: "🌧️", text: "What challenges did you face?" },
                { emoji: "📅", text: "How was your overall day?" },
                { emoji: "🧠", text: "How was your mental health?" },
                { emoji: "📈", text: "What progress did you make?" },
                { emoji: "💭", text: "Goals for tomorrow?" }
              ].map((prompt, index) => (
                <motion.div
                  key={index}
                  whileHover={{ scale: 1.02 }}
                  className="bg-gray-50 dark:bg-gray-800 
                    rounded-xl p-3 border border-gray-200 dark:border-gray-700 cursor-pointer
                    hover:shadow-md transition-all duration-200"
                  onClick={() => setEntry(prev => prev + (prev ? '\n\n' : '') + `${prompt.emoji} ${prompt.text}\n`)}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{prompt.emoji}</span>
                    <span className="text-sm text-gray-700 dark:text-gray-300">{prompt.text}</span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Edit/Preview toggle */}
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowPreview(false)}
                className={`px-4 py-2 rounded-xl font-medium transition-all duration-200 ${!showPreview
                  ? 'bg-gray-800 text-white shadow-lg'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
              >
                ✏️ Write
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowPreview(true)}
                className={`px-4 py-2 rounded-xl font-medium transition-all duration-200 ${showPreview
                  ? 'bg-gray-800 text-white shadow-lg'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
              >
                👁️ Preview
              </motion.button>
            </div>

            <div className="text-sm text-gray-500 dark:text-gray-400">
              {charCount} characters
            </div>
          </div>

          <AnimatePresence mode="wait">
            {!saved ? (
              <motion.div
                key="addEntry"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
                className="mb-2 text-right flex-shrink-0"
              >
                <button
                  onClick={saveEntry}
                  disabled={loading || !entry.trim()}
                  onFocus={() => setFocused(true)}
                  onBlur={() => setFocused(false)}
                  className={`
                  px-5 py-2 text-white rounded-md font-medium transition 
                  disabled:opacity-50 disabled:cursor-not-allowed
                  ${buttonBg} 
                  hover:scale-105 hover:shadow-lg
                  ${focused ? "animate-pulse" : ""}
                `}
                >
                  {loading ? "Saving..." : "➕ Add Entry"}
                </button>
              </motion.div>
            ) : (
              <motion.div
                key="newEntry"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
                className="mb-2 text-center flex-shrink-0"
              >
                <button
                  onClick={newEntry}
                  className="px-5 py-2 bg-gray-800 hover:bg-gray-900 text-white rounded-md font-medium transition hover:scale-105 hover:shadow-lg"
                >
                  🆕 New Entry
                </button>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Textarea or Markdown Preview */}
          {showPreview ? (
            <motion.div
              key="preview"
              className={`p-4 rounded-lg border ${inputBg} ${borderColor} overflow-auto`}
              style={{ height: containerMaxHeight - 160, fontSize: "0.9rem" }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.4 }}
            >
              {entry.trim() ? (
                <ReactMarkdown>{entry}</ReactMarkdown>
              ) : (
                <p className={textColor}>Nothing to preview yet...</p>
              )}
            </motion.div>
          ) : (
            <motion.textarea
              key="edit"
              rows="12"
              placeholder="Start writing your thoughts here..."
              value={entry}
              onChange={(e) => setEntry(e.target.value)}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              className={`w-full p-4 rounded-lg border ${inputBg} ${borderColor} focus:outline-none focus:ring-2 focus:ring-gray-500 text-sm ${textColor} resize-none`}
              style={{
                height: containerMaxHeight - 160,
                overflowY: "auto",
                scrollbarWidth: "thin",
                scrollbarColor: darkMode ? "#6B7280 #1f2937" : "#9CA3AF #f3f4f6",
              }}
              disabled={loading || saved}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            />
          )}

          {/* Character count */}
          <div className="text-sm text-gray-500 dark:text-gray-400 text-center mt-4">
            {charCount} character{charCount !== 1 ? "s" : ""}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
