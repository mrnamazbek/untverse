"use client";

import React from "react";
import { Question } from "@/types/learning";
import { Check, Circle } from "lucide-react";

interface QuestionRendererProps {
  question: Question;
  selectedOptionIds: number[];
  textAnswer: string;
  onOptionToggle: (optionId: number) => void;
  onTextAnswerChange: (text: string) => void;
  isReviewMode?: boolean;
  correctOptionIds?: number[];
}

export const QuestionRenderer: React.FC<QuestionRendererProps> = ({
  question,
  selectedOptionIds,
  textAnswer,
  onOptionToggle,
  onTextAnswerChange,
  isReviewMode = false,
  correctOptionIds = [],
}) => {
  const isMultiple = question.question_type === "multiple_choice";
  const isTextBased = question.question_type === "fill_gap" || question.question_type === "sql";

  return (
    <div className="space-y-6">
      {/* Question Header & Stem */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-blue-50 text-[#0075de] border border-blue-200/50">
            {question.question_type === "single_choice" && "Один верный ответ"}
            {question.question_type === "multiple_choice" && "Несколько верных ответов"}
            {question.question_type === "true_false" && "Истина / Ложь"}
            {question.question_type === "fill_gap" && "Ввод ответа"}
            {question.question_type === "sql" && "SQL запрос"}
            {question.question_type === "matching" && "Сопоставление"}
          </span>
          <span className="text-xs text-[#a39e98]">•</span>
          <span className="text-xs font-medium text-[#615d59]">
            {question.points} {question.points === 1 ? "балл" : "балла"}
          </span>
        </div>

        <h3 className="text-base sm:text-lg font-semibold text-[#000000] leading-relaxed whitespace-pre-wrap">
          {question.text}
        </h3>

        {/* Code Snippet block if present */}
        {question.code_snippet && (
          <div className="p-4 bg-[#213183] text-white rounded-xl font-mono text-xs sm:text-sm overflow-x-auto shadow-inner border border-blue-900">
            <pre>{question.code_snippet}</pre>
          </div>
        )}
      </div>

      {/* Options Rendering */}
      {!isTextBased && (
        <div className="space-y-2.5">
          {question.options.map((opt, idx) => {
            const isSelected = selectedOptionIds.includes(opt.id);
            const isCorrect = correctOptionIds.includes(opt.id);

            let borderClass = "border-[#e6e6e6]";
            let bgClass = "bg-white hover:bg-[#f6f5f4]";
            let textClass = "text-[#31302e]";

            if (isReviewMode) {
              if (isCorrect) {
                borderClass = "border-[#1aae39] bg-green-50";
                textClass = "text-green-900 font-semibold";
              } else if (isSelected && !isCorrect) {
                borderClass = "border-red-500 bg-red-50";
                textClass = "text-red-900";
              }
            } else if (isSelected) {
              borderClass = "border-[#0075de] bg-blue-50/60";
              textClass = "text-[#0075de] font-semibold";
            }

            return (
              <button
                key={opt.id}
                type="button"
                onClick={() => !isReviewMode && onOptionToggle(opt.id)}
                disabled={isReviewMode}
                className={`w-full p-3.5 sm:p-4 rounded-xl border text-left flex items-start gap-3 transition-all cursor-pointer ${borderClass} ${bgClass} ${textClass}`}
              >
                <div
                  className={`w-5 h-5 rounded-${isMultiple ? "md" : "full"} mt-0.5 flex items-center justify-center shrink-0 border transition-all ${
                    isSelected
                      ? "bg-[#0075de] border-[#0075de] text-white"
                      : "border-[#d8d5d1] bg-white"
                  } ${isReviewMode && isCorrect ? "bg-[#1aae39] border-[#1aae39] text-white" : ""}`}
                >
                  {isSelected && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                </div>

                <div className="flex-1 text-sm leading-snug">
                  <span className="font-semibold text-xs text-[#a39e98] mr-2">
                    {String.fromCharCode(65 + idx)}.
                  </span>
                  <span>{opt.text}</span>
                </div>
              </button>
            );
          })}
        </div>
      )}

      {/* Text Input for Fill-gap or SQL */}
      {isTextBased && (
        <div className="space-y-2">
          <label className="block text-xs font-semibold text-[#615d59]">
            Введите точный ответ или ключевое слово:
          </label>
          <input
            type="text"
            value={textAnswer}
            onChange={(e) => onTextAnswerChange(e.target.value)}
            disabled={isReviewMode}
            placeholder={question.question_type === "sql" ? "SELECT ..." : "Ваш ответ..."}
            className="w-full p-3.5 bg-white border border-[#d8d5d1] rounded-xl text-sm focus:outline-none focus:border-[#0075de] focus:ring-2 focus:ring-blue-100 transition-all font-mono"
          />
        </div>
      )}
    </div>
  );
};
