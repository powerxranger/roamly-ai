import React, { useMemo } from 'react';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content, className = '' }) => {
  const renderedHtml = useMemo(() => {
    if (!content) return '';

    const lines = content.split('\n');
    const output: string[] = [];
    let inTable = false;
    let tableBuffer: string[] = [];
    let inList = false;
    let listType: 'ul' | 'ol' = 'ul';

    const flushTable = () => {
      if (!tableBuffer.length) return;
      const rows = tableBuffer.map(row => {
        const cells = row
          .split('|')
          .filter((_, idx, arr) => idx > 0 && idx < arr.length - 1)
          .map(c => c.trim());
        return cells;
      });

      if (rows.length >= 2) {
        const header = rows[0];
        // row 1 is separator |---|---|
        const bodyRows = rows.slice(2);

        let tableHtml = '<div class="overflow-x-auto my-3"><table class="w-full border-collapse border border-slate-800 text-sm"><thead><tr>';
        header.forEach(h => {
          tableHtml += `<th class="border border-slate-800 bg-slate-900/80 px-3 py-2 text-left text-xs font-semibold text-slate-200">${formatInline(h)}</th>`;
        });
        tableHtml += '</tr></thead><tbody>';
        bodyRows.forEach(r => {
          tableHtml += '<tr>';
          r.forEach(c => {
            tableHtml += `<td class="border border-slate-800/80 bg-slate-950/40 px-3 py-2 text-xs text-slate-300">${formatInline(c)}</td>`;
          });
          tableHtml += '</tr>';
        });
        tableHtml += '</tbody></table></div>';
        output.push(tableHtml);
      }
      tableBuffer = [];
      inTable = false;
    };

    const flushList = () => {
      if (inList) {
        output.push(listType === 'ul' ? '</ul>' : '</ol>');
        inList = false;
      }
    };

    const formatInline = (text: string): string => {
      return text
        // bold & italic
        .replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>')
        // bold
        .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-slate-100">$1</strong>')
        // italic
        .replace(/\*(.*?)\*/g, '<em class="text-slate-300">$1</em>')
        // inline code
        .replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-blue-300 text-xs font-mono">$1</code>')
        // links
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-blue-400 hover:text-blue-300 underline underline-offset-2">$1</a>');
    };

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();

      // Table lines
      if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
        flushList();
        inTable = true;
        tableBuffer.push(trimmed);
        continue;
      } else if (inTable) {
        flushTable();
      }

      // Empty line
      if (!trimmed) {
        flushList();
        continue;
      }

      // Headings
      if (trimmed.startsWith('#### ')) {
        flushList();
        output.push(`<h4 class="text-sm font-bold text-slate-200 mt-4 mb-2">${formatInline(trimmed.slice(5))}</h4>`);
        continue;
      }
      if (trimmed.startsWith('### ')) {
        flushList();
        output.push(`<h3 class="text-base font-bold text-blue-400 mt-5 mb-2">${formatInline(trimmed.slice(4))}</h3>`);
        continue;
      }
      if (trimmed.startsWith('## ')) {
        flushList();
        output.push(`<h2 class="text-lg font-bold text-slate-100 mt-6 mb-3 pb-1 border-b border-slate-800/80">${formatInline(trimmed.slice(3))}</h2>`);
        continue;
      }
      if (trimmed.startsWith('# ')) {
        flushList();
        output.push(`<h1 class="text-xl font-extrabold text-white mt-6 mb-3">${formatInline(trimmed.slice(2))}</h1>`);
        continue;
      }

      // Blockquotes
      if (trimmed.startsWith('> ')) {
        flushList();
        output.push(`<blockquote class="border-l-4 border-blue-500 bg-blue-500/5 px-4 py-2 my-2 rounded-r-lg text-slate-400 text-sm italic">${formatInline(trimmed.slice(2))}</blockquote>`);
        continue;
      }

      // Unordered lists
      if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
        if (!inList || listType !== 'ul') {
          flushList();
          output.push('<ul class="list-disc list-inside space-y-1 my-2 text-sm text-slate-300">');
          inList = true;
          listType = 'ul';
        }
        output.push(`<li class="leading-relaxed">${formatInline(trimmed.slice(2))}</li>`);
        continue;
      }

      // Numbered lists
      const orderedMatch = trimmed.match(/^(\d+)\.\s+(.*)/);
      if (orderedMatch) {
        if (!inList || listType !== 'ol') {
          flushList();
          output.push('<ol class="list-decimal list-inside space-y-1 my-2 text-sm text-slate-300">');
          inList = true;
          listType = 'ol';
        }
        output.push(`<li class="leading-relaxed">${formatInline(orderedMatch[2])}</li>`);
        continue;
      }

      // Regular paragraph
      flushList();
      output.push(`<p class="text-sm text-slate-300 leading-relaxed mb-3">${formatInline(trimmed)}</p>`);
    }

    if (inTable) flushTable();
    flushList();

    return output.join('\n');
  }, [content]);

  return (
    <div
      className={`markdown-content ${className}`}
      dangerouslySetInnerHTML={{ __html: renderedHtml }}
    />
  );
};
