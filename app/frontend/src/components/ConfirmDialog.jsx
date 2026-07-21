function ConfirmDialog({ open, title, message, confirmLabel = "Confirm", danger = false, onConfirm, onCancel }) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4">
      <div className="w-full max-w-sm bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-base font-medium text-gray-100 mb-2">{title}</h2>
        <p className="text-sm text-gray-400 mb-6">{message}</p>
        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-3 py-1.5 text-sm text-gray-300 hover:bg-gray-800 rounded-md transition"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className={`px-3 py-1.5 text-sm font-medium rounded-md transition ${
              danger
                ? "bg-red-900/40 text-red-400 hover:bg-red-900/60"
                : "bg-white text-gray-900 hover:bg-gray-200"
            }`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmDialog;