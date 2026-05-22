import { useTranslation } from "react-i18next";

interface Props {
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmDialog({
  title,
  message,
  onConfirm,
  onCancel,
}: Props) {
  const { t } = useTranslation();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-gray-800 border border-border rounded-lg p-6 max-w-sm w-full mx-4 shadow-xl">
        <h3 className="text-lg font-semibold text-gray-200 mb-2">{title}</h3>
        <p className="text-sm text-gray-400 mb-6">{message}</p>
        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-1.5 text-sm text-gray-300 bg-gray-700 hover:bg-gray-600 rounded cursor-pointer transition-colors"
          >
            {t("dialog.cancel")}
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-1.5 text-sm text-white bg-red-600 hover:bg-red-700 rounded cursor-pointer transition-colors"
          >
            {t("dialog.delete")}
          </button>
        </div>
      </div>
    </div>
  );
}
