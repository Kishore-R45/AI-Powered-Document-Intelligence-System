import { FileText, ExternalLink } from 'lucide-react';

/**
 * Displays clickable document source references for AI responses.
 * Shows which documents the answer was retrieved from.
 * Clicking a source opens the document directly from S3 in a new browser tab.
 *
 * @param {Array} sources - Array of { documentId, documentName, viewUrl, page? }
 */
export default function SourceReference({ sources = [] }) {
  if (sources.length === 0) return null;

  /**
   * Open document in new tab using the presigned S3 URL.
   */
  const handleSourceClick = (source) => {
    if (source.viewUrl) {
      window.open(source.viewUrl, '_blank', 'noopener,noreferrer');
    } else {
      console.warn('No viewUrl available for source:', source.documentName);
    }
  };

  return (
    <div className="flex flex-wrap gap-2">
      <span className="text-xs text-neutral-400 font-medium self-center">Sources:</span>
      {sources.map((source, index) => (
        <button
          key={index}
          onClick={() => handleSourceClick(source)}
          disabled={!source.viewUrl}
          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 bg-brand-50 border border-brand-200 rounded-md text-xs text-brand-700 hover:bg-brand-100 hover:border-brand-300 transition-colors cursor-pointer group disabled:opacity-50 disabled:cursor-not-allowed"
          title={source.viewUrl ? `Open ${source.documentName} in new tab` : 'Document not available'}
        >
          <FileText size={12} />
          <span className="max-w-[150px] truncate">{source.documentName}</span>
          <ExternalLink size={10} className="opacity-50 group-hover:opacity-100" />
          {source.page && <span className="text-brand-500">· p.{source.page}</span>}
        </button>
      ))}
    </div>
  );
}