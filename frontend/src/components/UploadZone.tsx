import { useState, useRef, useCallback } from "react";
import { useTranslation } from "react-i18next";

interface Props {
  onUpload: (file: File) => void;
  uploading: boolean;
}

export default function UploadZone({ onUpload, uploading }: Props) {
  const { t } = useTranslation();
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(
    (file: File) => {
      onUpload(file);
    },
    [onUpload]
  );

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      className={`h-full border-2 border-dashed rounded-lg flex flex-col items-center justify-center p-8 cursor-pointer transition-colors ${
        dragOver
          ? "border-blue-400 bg-blue-400/10"
          : uploading
            ? "border-gray-600 bg-gray-800/50 opacity-60 pointer-events-none"
            : "border-gray-600 hover:border-gray-500 bg-gray-800/30"
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.txt,.md,.csv"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFile(file);
          e.target.value = "";
        }}
        className="hidden"
      />

      {uploading ? (
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          <p className="text-sm text-gray-400">{t("upload.uploading")}</p>
        </div>
      ) : (
        <div className="text-center">
          <div className="text-2xl mb-2">📎</div>
          <p className="text-sm text-gray-400">{t("upload.drop")}</p>
          <p className="text-xs text-gray-500 mt-1">{t("upload.formats")}</p>
        </div>
      )}
    </div>
  );
}
