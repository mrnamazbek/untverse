"use client";

import React from "react";
import { Play, RotateCcw, Copy, Check } from "lucide-react";

interface CodeEditorProps {
  code: string;
  onChange: (newCode: string) => void;
  onRun: () => void;
  onReset: () => void;
  isRunning?: boolean;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  code,
  onChange,
  onRun,
  onReset,
  isRunning = false,
}) => {
  const [copied, setCopied] = React.useState(false);

  const lines = code.split("\n");

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      onRun();
    }
    // Handle Tab key
    if (e.key === "Tab") {
      e.preventDefault();
      const target = e.target as HTMLTextAreaElement;
      const start = target.selectionStart;
      const end = target.selectionEnd;
      const newCode = code.substring(0, start) + "    " + code.substring(end);
      onChange(newCode);
      setTimeout(() => {
        target.selectionStart = target.selectionEnd = start + 4;
      }, 0);
    }
  };

  return (
    <div className="notion-card overflow-hidden border-[#213183]/30 shadow-md">
      {/* Editor Header Bar */}
      <div className="bg-[#213183] px-4 py-2.5 flex items-center justify-between text-xs text-white/80 border-b border-blue-900">
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-red-400/80 inline-block" />
          <span className="w-3 h-3 rounded-full bg-yellow-400/80 inline-block" />
          <span className="w-3 h-3 rounded-full bg-green-400/80 inline-block" />
          <span className="font-mono text-[11px] text-white/90 font-medium ml-2">solution.py</span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="p-1.5 hover:bg-white/10 rounded text-white/80 hover:text-white transition-colors"
            title="Скопировать код"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={onReset}
            className="p-1.5 hover:bg-white/10 rounded text-white/80 hover:text-white transition-colors"
            title="Сбросить к шаблону"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={onRun}
            disabled={isRunning}
            className="btn-primary text-xs py-1.5 px-3 bg-[#0075de] hover:bg-[#005bab] text-white shadow-xs font-semibold"
          >
            <Play className="w-3 h-3 fill-white" />
            <span>{isRunning ? "Тестирование..." : "Запустить (Ctrl+Enter)"}</span>
          </button>
        </div>
      </div>

      {/* Code Textarea with Line Numbers */}
      <div className="relative flex bg-[#1e2337] text-[#e0e6ed] font-mono text-xs sm:text-sm min-h-[300px] max-h-[480px] overflow-auto">
        {/* Line Numbers */}
        <div className="py-4 pl-3 pr-2 text-right text-gray-500 select-none bg-[#171b2b] border-r border-gray-800 text-xs">
          {lines.map((_, i) => (
            <div key={i} className="leading-6">
              {i + 1}
            </div>
          ))}
        </div>

        {/* Real Editor Area */}
        <textarea
          value={code}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          spellCheck={false}
          className="flex-1 p-4 bg-transparent text-white font-mono resize-none focus:outline-none leading-6 w-full whitespace-pre"
        />
      </div>
    </div>
  );
};
