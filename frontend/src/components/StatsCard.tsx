import { useTranslation } from "react-i18next";
import type { StatsResponse } from "../types";

interface Props {
  stats: StatsResponse;
  loading: boolean;
}

export default function StatsCard({ stats, loading }: Props) {
  const { t } = useTranslation();

  return (
    <div className="bg-gray-800/50 border border-border rounded-lg p-4 flex flex-col justify-center">
      {loading ? (
        <div className="space-y-3">
          <div className="h-5 bg-gray-700 rounded animate-pulse w-3/4" />
          <div className="h-5 bg-gray-700 rounded animate-pulse w-1/2" />
        </div>
      ) : (
        <>
          <div className="text-center mb-3">
            <span className="text-3xl font-bold text-gray-200">
              {stats.total_documents}
            </span>
            <p className="text-xs text-gray-500 mt-0.5">{t("stats.files")}</p>
          </div>
          <div className="text-center">
            <span className="text-3xl font-bold text-gray-200">
              {stats.total_domains}
            </span>
            <p className="text-xs text-gray-500 mt-0.5">{t("stats.domains")}</p>
          </div>
          {stats.last_processed_date && (
            <p className="text-xs text-gray-600 text-center mt-3">
              {t("stats.lastProcessed")}{" "}
              {new Date(stats.last_processed_date).toLocaleDateString()}
            </p>
          )}
        </>
      )}
    </div>
  );
}
