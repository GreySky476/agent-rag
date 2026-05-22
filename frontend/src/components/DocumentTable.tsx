import { useTranslation } from "react-i18next";
import type { DocumentResponse } from "../types";

interface Props {
  documents: DocumentResponse[];
  loading: boolean;
  onDelete: (doc: DocumentResponse) => void;
}

export default function DocumentTable({ documents, loading, onDelete }: Props) {
  const { t } = useTranslation();

  if (loading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-10 bg-gray-800 rounded animate-pulse" />
        ))}
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-sm">{t("doc.empty")}</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-gray-500 border-b border-border">
            <th className="py-2 px-3 font-medium">{t("doc.name")}</th>
            <th className="py-2 px-3 font-medium">{t("doc.domain")}</th>
            <th className="py-2 px-3 font-medium">{t("doc.level")}</th>
            <th className="py-2 px-3 font-medium">{t("doc.status")}</th>
            <th className="py-2 px-3 font-medium">{t("doc.actions")}</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr
              key={doc.id}
              className="border-b border-border/50 hover:bg-gray-800/50 transition-colors"
            >
              <td className="py-2 px-3 text-gray-300 max-w-[200px] truncate">
                {doc.title || doc.file_path}
              </td>
              <td className="py-2 px-3 text-gray-500">
                {doc.domain_id ? `#${doc.domain_id}` : "—"}
              </td>
              <td className="py-2 px-3">
                <span
                  className={`text-xs px-1.5 py-0.5 rounded ${
                    doc.importance === "L3"
                      ? "bg-purple-900/40 text-purple-300"
                      : doc.importance === "L2"
                        ? "bg-blue-900/40 text-blue-300"
                        : "bg-gray-700 text-gray-400"
                  }`}
                >
                  {doc.importance}
                </span>
              </td>
              <td className="py-2 px-3">
                {doc.processing_status === "completed" && (
                  <span className="text-green-400">✅</span>
                )}
                {doc.processing_status === "pending" && (
                  <span className="text-yellow-400" title="Processing...">⏳</span>
                )}
                {doc.processing_status === "processing" && (
                  <span className="text-blue-400 animate-pulse" title="Processing...">🔄</span>
                )}
                {doc.processing_status === "failed" && (
                  <span className="text-red-400" title="Failed">❌</span>
                )}
              </td>
              <td className="py-2 px-3 flex gap-2">
                <button
                  onClick={() => onDelete(doc)}
                  className="text-gray-500 hover:text-red-400 cursor-pointer text-xs"
                  title={t("doc.actions")}
                >
                  🗑️
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
