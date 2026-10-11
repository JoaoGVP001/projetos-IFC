import { memo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeSanitize, { defaultSchema } from "rehype-sanitize";
import rehypeKatex from "rehype-katex";
import { api } from "./bridge";
export function normalizarMatematica(texto: string) {
  return texto
    .split(/(`{3,}[\s\S]*?`{3,}|~{3,}[\s\S]*?~{3,}|`+[^`\n]*`+)/g)
    .map((p, i) =>
      i % 2
        ? p
        : p
            .replace(/\\\[([\s\S]*?)\\\]/g, "\n\n$$$$\n$1\n$$$$\n\n")
            .replace(/\\\(([\s\S]*?)\\\)/g, "$$$1$"),
    )
    .join("");
}
const schema = {
  ...defaultSchema,
  attributes: {
    ...defaultSchema.attributes,
    code: [
      ...(defaultSchema.attributes?.code || []),
      ["className", /^language-./, "math-inline", "math-display"],
    ],
  },
};
export const Markdown = memo(function Markdown({
  texto,
  onError,
}: {
  texto: string;
  onError?: (m: string) => void;
}) {
  return (
    <div className="markdown">
      <ReactMarkdown
        skipHtml
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[
          [rehypeSanitize, schema],
          [
            rehypeKatex,
            { throwOnError: false, strict: "ignore", trust: false },
          ],
        ]}
        components={{
          a: ({ href, children }) => (
            <a
              href={href}
              onClick={(e) => {
                e.preventDefault();
                if (href)
                  api("abrir_link", { url: href }).catch((e) =>
                    onError?.(e.message),
                  );
              }}
            >
              {children}
            </a>
          ),
          table: ({ children }) => (
            <div className="table-scroll">
              <table>{children}</table>
            </div>
          ),
        }}
      >
        {normalizarMatematica(texto)}
      </ReactMarkdown>
    </div>
  );
});
