"use client"

import { useState } from "react";
import { Bot, X, Sparkles, Send } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";

export function AIAssistant() {
  const [isOpen, setIsOpen] = useState(false);

  const prompts = [
    "Plan my day",
    "I have 6 hours free.",
    "Break this task into subtasks.",
    "Prioritize my tasks."
  ];

  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.9 }}
            className="fixed bottom-24 right-4 z-50 w-80 max-w-[calc(100vw-2rem)] glass-dark rounded-2xl overflow-hidden border border-primary/20 shadow-2xl shadow-primary/20"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-primary/20 to-secondary/20 p-4 border-b border-white/10 flex justify-between items-center">
              <div className="flex items-center gap-2">
                <div className="bg-primary/20 p-1.5 rounded-lg">
                  <Bot size={20} className="text-primary" />
                </div>
                <h3 className="font-heading font-semibold text-white">AI Assistant</h3>
              </div>
              <button onClick={() => setIsOpen(false)} className="text-muted-foreground hover:text-white transition-colors">
                <X size={20} />
              </button>
            </div>
            
            {/* Body */}
            <div className="p-4 h-64 overflow-y-auto flex flex-col justify-end">
              <div className="space-y-4">
                <div className="flex gap-3 items-start">
                  <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                    <Bot size={16} className="text-primary" />
                  </div>
                  <div className="bg-white/5 border border-white/10 rounded-2xl rounded-tl-sm p-3 text-sm text-white/90 shadow-sm">
                    Hi! I'm your AI task assistant. How can I help you be more productive today?
                  </div>
                </div>
              </div>
              
              <div className="mt-6">
                <p className="text-xs text-muted-foreground mb-2 px-1 font-medium">Suggested Prompts</p>
                <div className="flex flex-wrap gap-2">
                  {prompts.map((prompt, i) => (
                    <button
                      key={i}
                      className="text-xs bg-white/5 hover:bg-white/10 border border-white/10 rounded-full px-3 py-1.5 text-white/80 transition-colors text-left"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            
            {/* Input area */}
            <div className="p-3 bg-black/40 border-t border-white/10">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Type a message..."
                  className="w-full bg-white/5 border border-white/10 rounded-full pl-4 pr-10 py-2.5 text-sm text-white placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 transition-colors"
                />
                <button className="absolute right-2 top-1/2 -translate-y-1/2 w-7 h-7 bg-primary rounded-full flex items-center justify-center text-white hover:bg-primary/90 transition-colors">
                  <Send size={14} className="ml-0.5" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-24 right-4 z-50 w-14 h-14 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center shadow-lg shadow-primary/30 text-white glitch-hover"
      >
        <Sparkles size={24} />
      </button>
    </>
  );
}
