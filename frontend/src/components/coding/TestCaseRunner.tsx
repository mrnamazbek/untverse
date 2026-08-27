"use client";

import React, { useState } from "react";
import { CodeRunResult } from "@/types/learning";
import { CheckCircle2, XCircle, Clock, AlertOctagon, Terminal } from "lucide-react";

interface TestCaseRunnerProps {
  result: CodeRunResult | null;
  isRunning?: boolean;
}

export const TestCaseRunner: React.FC<TestCaseRunnerProps> = ({
  result,
  isRunning = false,
}) => {
  const [activeTab, setActiveTab] = useState(0);

  if (isRunning) {
    return (
      <div className="notion-card p-6 flex items-center justify-center gap-3 text-sm text-[#615d59]">
        <div className="w-5 h-5 border-2 border-[#0075de] border-t-transparent rounded-full animate-spin" />
        <span>Выполнение кода в изолированной песочнице и проверка тестов...</span>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="notion-card p-8 text-center text-[#615d59] border-dashed">
        <Terminal className="w-8 h-8 mx-auto mb-2 text-[#a39e98]" />
        <p className="text-xs font-medium">
          Нажмите <span className="font-bold text-[#0075de]">«Запустить»</span> для проверки решения на наборе тестов.
        </p>
      </div>
    );
  }

  const isAccepted = result.status === "accepted";

  return (
    <div className="notion-card overflow-hidden">
      {/* Top Banner Status */}
      <div
        className={`px-5 py-3.5 border-b flex items-center justify-between ${
          isAccepted
            ? "bg-green-50/80 border-green-200 text-green-900"
            : "bg-red-50/80 border-red-200 text-red-900"
        }`}
      >
        <div className="flex items-center gap-2.5">
          {isAccepted ? (
            <CheckCircle2 className="w-5 h-5 text-[#1aae39]" />
          ) : (
            <XCircle className="w-5 h-5 text-red-600" />
          )}
          <div>
            <h4 className="font-bold text-sm">
              {result.status === "accepted" && "Решение принято (Accepted)"}
              {result.status === "wrong_answer" && "Неверный ответ (Wrong Answer)"}
              {result.status === "runtime_error" && "Ошибка во время выполнения (Runtime Error)"}
              {result.status === "timeout" && "Превышен лимит времени (Time Limit Exceeded)"}
              {result.status === "forbidden_syntax" && "Запрещенная конструкция (Security Violation)"}
            </h4>
            <p className="text-[11px] opacity-80">
              Пройдено тестов: {result.passed_tests} из {result.total_tests} • Время: {result.execution_time_ms} мс
            </p>
          </div>
        </div>

        {isAccepted && result.xp_earned > 0 && (
          <span className="px-3 py-1 bg-[#1aae39] text-white text-xs font-bold rounded-full shadow-xs">
            +{result.xp_earned} XP
          </span>
        )}
      </div>

      {/* Error Output if any */}
      {result.error_output && (
        <div className="p-4 bg-stone-900 text-red-300 font-mono text-xs overflow-x-auto border-b border-stone-800">
          <div className="font-bold text-red-400 mb-1">Сообщение об ошибке:</div>
          <pre className="whitespace-pre-wrap">{result.error_output}</pre>
        </div>
      )}

      {/* Test Cases Tabs */}
      {result.test_results.length > 0 && (
        <div className="p-4 bg-[#f6f5f4]/40">
          <div className="flex items-center gap-1.5 overflow-x-auto pb-2 mb-3">
            {result.test_results.map((tc, idx) => (
              <button
                key={idx}
                onClick={() => setActiveTab(idx)}
                className={`px-3 py-1.5 text-xs font-medium rounded-lg flex items-center gap-1.5 transition-all shrink-0 cursor-pointer ${
                  activeTab === idx
                    ? "bg-white text-[#000000] shadow-xs border border-[#e6e6e6] font-semibold"
                    : "text-[#615d59] hover:bg-white/60"
                }`}
              >
                <span
                  className={`w-2 h-2 rounded-full ${
                    tc.passed ? "bg-[#1aae39]" : "bg-red-500"
                  }`}
                />
                <span>Тест {idx + 1}</span>
              </button>
            ))}
          </div>

          {/* Active Test Case Details */}
          {result.test_results[activeTab] && (
            <div className="bg-white border border-[#e6e6e6] rounded-xl p-4 space-y-3 text-xs font-mono">
              <div>
                <span className="text-[#a39e98] block text-[10px] font-sans uppercase font-bold tracking-wider mb-1">
                  Входные данные:
                </span>
                <div className="p-2.5 bg-[#f6f5f4] rounded-lg text-[#000000] whitespace-pre-wrap">
                  {result.test_results[activeTab].input_data || "<пустой ввод>"}
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <span className="text-[#a39e98] block text-[10px] font-sans uppercase font-bold tracking-wider mb-1">
                    Ожидаемый вывод:
                  </span>
                  <div className="p-2.5 bg-green-50/70 border border-green-200/50 rounded-lg text-green-950 whitespace-pre-wrap">
                    {result.test_results[activeTab].expected_output}
                  </div>
                </div>

                <div>
                  <span className="text-[#a39e98] block text-[10px] font-sans uppercase font-bold tracking-wider mb-1">
                    Вывод вашей программы:
                  </span>
                  <div
                    className={`p-2.5 rounded-lg whitespace-pre-wrap ${
                      result.test_results[activeTab].passed
                        ? "bg-green-50/70 border border-green-200/50 text-green-950"
                        : "bg-red-50/70 border border-red-200/50 text-red-950"
                    }`}
                  >
                    {result.test_results[activeTab].actual_output || "<нет вывода>"}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
