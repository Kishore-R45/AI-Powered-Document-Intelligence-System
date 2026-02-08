import { FileText } from 'lucide-react';

/**
 * Displays document source references for AI responses.
 * Shows which documents the answer was retrieved from.
 *
 * @param {Array} sources - Array of { documentName, page? }
 */
export default function SourceReference({ sources = [] }) {
  if (sources.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2">
      <span className="text-xs text-neutral-400 font-medium self-center">Sources:</span>
      {sources.map((source, index) => (
        <span
          key={index}
          className="inline-flex items-center gap-1 px-2 py-1 bg-neutral-50 border border-neutral-200 rounded-md text-xs text-neutral-600"
        >
          <FileText size={12} />
          {source.documentName}
          {source.page && <span className="text-neutral-400">· p.{source.page}</span>}
        </span>
      ))}
    </div>
  );
}