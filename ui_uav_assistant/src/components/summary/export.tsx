import React, { useCallback } from "react";
import { SERVER_URL } from "../../api/client/entity";

export function ExportZipButtonAsButton() {
  const onClick = useCallback(() => {
    window.location.href = `${SERVER_URL}/export/all_csv.zip`;
  }, []);

  return (
    <button
      className="rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200 hover:bg-slate-800"
      onClick={onClick}
      type="button"
    >
      Export CSV (ZIP)
    </button>
  );
}
