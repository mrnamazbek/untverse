"use client";

import { type ComponentProps, useState } from "react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import rehypeSanitize from "rehype-sanitize";
import remarkGfm from "remark-gfm";
import { Check, Copy } from "lucide-react";
import type { Locale } from "@/lib/i18n";

interface ContentRendererProps {
  /** Markdown received from the content API. Raw HTML is deliberately not enabled. */
  content: string;
  className?: string;
  locale?: Locale;
}

function CodeBlock({
  className,
  children,
  node: _node,
  locale = "kk",
  ...props
}: ComponentProps<"code"> & { node?: unknown; locale?: Locale }) {
  const [copied, setCopied] = useState(false);
  const language = /language-([\w+-]+)/.exec(className || "")?.[1];
  const code = String(children).replace(/\n$/, "");
  const isBlock = Boolean(className?.includes("language-")) || code.includes("\n");
  const labels = locale === "kk"
    ? { copy: "Кодты көшіру", copied: "Көшірілді" }
    : locale === "ru"
      ? { copy: "Копировать код", copied: "Скопировано" }
      : { copy: "Copy code", copied: "Copied" };

  if (!isBlock) {
    return (
      <code
        className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[0.9em] text-slate-800"
        {...props}
      >
        {children}
      </code>
    );
  }

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      // Clipboard access can be unavailable in an insecure browser context.
    }
  };

  return (
    <div className="my-5 overflow-hidden rounded-xl border border-slate-700 bg-slate-950 text-slate-100 shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-800 px-3 py-2 text-[11px] font-medium text-slate-300">
        <span className="uppercase tracking-wider">{language || "code"}</span>
        <button
          type="button"
          onClick={copy}
          className="inline-flex items-center gap-1 rounded px-1.5 py-1 text-slate-300 transition-colors hover:bg-slate-800 hover:text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
          aria-label={labels.copy}
        >
          {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
          {copied ? labels.copied : labels.copy}
        </button>
      </div>
      <pre className="m-0 overflow-x-auto p-4 text-xs leading-6 sm:text-sm">
        <code className={className} {...props}>{children}</code>
      </pre>
    </div>
  );
}

/**
 * Shared, safe renderer for API-backed educational content.
 *
 * `react-markdown` does not parse raw HTML unless explicitly configured with
 * rehypeRaw; we intentionally do not add that plugin. `rehype-sanitize` is a
 * defense-in-depth pass for the generated Markdown AST and highlighted code.
 */
export function ContentRenderer({ content, className = "", locale = "kk" }: ContentRendererProps) {
  return (
    <div className={`content-renderer ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight, rehypeSanitize]}
        components={{
          h1: ({ children }) => <h1 className="mb-5 mt-8 text-2xl font-extrabold tracking-tight text-slate-950 sm:text-3xl">{children}</h1>,
          h2: ({ children }) => <h2 className="mb-4 mt-8 text-xl font-bold text-slate-950 sm:text-2xl">{children}</h2>,
          h3: ({ children }) => <h3 className="mb-3 mt-6 text-lg font-bold text-slate-900">{children}</h3>,
          p: ({ children }) => <p className="my-4 text-sm leading-7 text-slate-700 sm:text-base">{children}</p>,
          ul: ({ children }) => <ul className="my-4 list-disc space-y-2 pl-6 text-sm leading-7 text-slate-700 sm:text-base">{children}</ul>,
          ol: ({ children }) => <ol className="my-4 list-decimal space-y-2 pl-6 text-sm leading-7 text-slate-700 sm:text-base">{children}</ol>,
          li: ({ children }) => <li className="pl-1">{children}</li>,
          blockquote: ({ children }) => <blockquote className="my-5 border-l-4 border-blue-500 bg-blue-50 px-4 py-3 text-sm italic leading-7 text-slate-700">{children}</blockquote>,
          hr: () => <hr className="my-8 border-slate-200" />,
          a: ({ href, children }) => (
            <a
              href={href}
              target={href?.startsWith("http") ? "_blank" : undefined}
              rel={href?.startsWith("http") ? "noopener noreferrer" : undefined}
              className="font-medium text-blue-700 underline underline-offset-2 hover:text-blue-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700"
            >
              {children}
            </a>
          ),
          table: ({ children }) => <div className="my-5 overflow-x-auto"><table className="w-full border-collapse text-left text-sm">{children}</table></div>,
          th: ({ children }) => <th className="border border-slate-200 bg-slate-50 px-3 py-2 font-semibold text-slate-900">{children}</th>,
          td: ({ children }) => <td className="border border-slate-200 px-3 py-2 align-top text-slate-700">{children}</td>,
          // react-markdown normally wraps fenced code in <pre>. CodeBlock owns
          // that semantic container so it can add its toolbar without nesting
          // invalid <pre> elements.
          pre: ({ children }) => <>{children}</>,
          code: ({ node, ...props }) => <CodeBlock {...props} node={node} locale={locale} />,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
