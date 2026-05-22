import { useState, useEffect, useCallback } from "react";
import { useTranslation } from "react-i18next";
import toast from "react-hot-toast";
import UploadZone from "../components/UploadZone";
import DocumentTable from "../components/DocumentTable";
import StatsCard from "../components/StatsCard";
import ConfirmDialog from "../components/ConfirmDialog";
import {
  listDocuments,
  uploadDocument,
  deleteDocument,
  listKnowledgeDomains,
} from "../api/documents";
import { getStats } from "../api/chat";
import type { DocumentResponse, KnowledgeDomain, StatsResponse } from "../types";

export default function KnowledgePage() {
  const { t } = useTranslation();
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [domains, setDomains] = useState<KnowledgeDomain[]>([]);
  const [stats, setStats] = useState<StatsResponse>({
    total_documents: 0,
    total_domains: 0,
    last_processed_date: null,
  });
  const [loading, setLoading] = useState(true);
  const [domainFilter, setDomainFilter] = useState<string>("all");
  const [importanceFilter, setImportanceFilter] = useState<string>("all");
  const [search, setSearch] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<DocumentResponse | null>(null);
  const [uploading, setUploading] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const [docs, doms, st] = await Promise.all([
        listDocuments(),
        listKnowledgeDomains(),
        getStats(),
      ]);
      setDocuments(docs);
      setDomains(doms);
      setStats(st);
    } catch {
      toast.error(t("upload.loadFailed"));
    } finally {
      setLoading(false);
    }
  }, [t]);

  const pollStatuses = useCallback(async () => {
    try {
      const pending = await listDocuments("pending,processing");
      setDocuments((prev) =>
        prev.map((d) => {
          const updated = pending.find((p) => p.id === d.id);
          return updated
            ? { ...d, processing_status: updated.processing_status }
            : d;
        })
      );
      return pending.length;
    } catch {
      return 0;
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    const pendingCount = documents.filter(
      (d) => d.processing_status !== "completed" && d.processing_status !== "failed"
    ).length;
    if (pendingCount === 0) return;

    const timer = setInterval(() => {
      pollStatuses();
    }, 5000);

    return () => clearInterval(timer);
  }, [documents, pollStatuses]);

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      const result = await uploadDocument(file, "L2");
      toast.success(
        t("upload.success", { name: result.file_path, count: result.chunk_count })
      );
      await loadData();
    } catch {
      toast.error(t("upload.failed"));
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteDocument(deleteTarget.id);
      toast.success(t("upload.deleted"));
      setDeleteTarget(null);
      await loadData();
    } catch {
      toast.error(t("upload.deleteFailed"));
    }
  };

  const filtered = documents.filter((d) => {
    if (domainFilter !== "all" && d.domain_id !== Number(domainFilter)) return false;
    if (importanceFilter !== "all" && d.importance !== importanceFilter) return false;
    if (search && !d.title?.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-5xl mx-auto px-6 py-6">
        <h1 className="text-xl font-semibold text-gray-200 mb-6">
          📚 {t("kb.title")}
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="md:col-span-2">
            <UploadZone onUpload={handleUpload} uploading={uploading} />
          </div>
          <StatsCard stats={stats} loading={loading} />
        </div>

        <div className="flex flex-wrap gap-3 mb-4">
          <select
            value={domainFilter}
            onChange={(e) => setDomainFilter(e.target.value)}
            className="bg-gray-800 border border-border rounded px-3 py-1.5 text-sm text-gray-300 cursor-pointer"
          >
            <option value="all">{t("kb.allDomains")}</option>
            {domains.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>

          <select
            value={importanceFilter}
            onChange={(e) => setImportanceFilter(e.target.value)}
            className="bg-gray-800 border border-border rounded px-3 py-1.5 text-sm text-gray-300 cursor-pointer"
          >
            <option value="all">{t("kb.allLevels")}</option>
            <option value="L1">{t("kb.L1")}</option>
            <option value="L2">{t("kb.L2")}</option>
            <option value="L3">{t("kb.L3")}</option>
          </select>

          <input
            type="text"
            placeholder={t("kb.searchFiles")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-gray-800 border border-border rounded px-3 py-1.5 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500 flex-1 min-w-[200px]"
          />
        </div>

        <DocumentTable
          documents={filtered}
          loading={loading}
          onDelete={(doc) => setDeleteTarget(doc)}
        />

        {deleteTarget && (
          <ConfirmDialog
            title={t("dialog.deleteTitle")}
            message={t("dialog.deleteMsg", {
              name: deleteTarget.title || deleteTarget.file_path,
            })}
            onConfirm={handleDelete}
            onCancel={() => setDeleteTarget(null)}
          />
        )}
      </div>
    </div>
  );
}
