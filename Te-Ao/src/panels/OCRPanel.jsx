import { useState } from "react";
import { useApi } from "../hooks/useApi.js";

function OCRPanel() {
  const { request } = useApi();
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    if (!file) {
      setError("Select an image before uploading.");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    setIsLoading(true);
    try {
      const data = await request("/ocr", {
        method: "POST",
        body: formData,
      });
      setResult(data);
    } catch (err) {
      setError(err.message || "Upload failed.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="rounded-2xl border border-emerald-800/60 bg-slate-900/70 p-6 shadow-lg shadow-emerald-900/20">
      <h2 className="text-xl font-semibold text-emerald-200">OCR Upload</h2>
      <p className="mt-2 text-sm text-slate-300">
        Drop an image and Tiwhanawhana will lift the kupu using Tesseract and
        store the taonga in Supabase memory.
      </p>
      <form className="mt-5 flex flex-col gap-4" onSubmit={handleSubmit}>
        <label className="flex flex-col gap-2 text-sm text-slate-200">
          Image file
          <input
            type="file"
            accept="image/*"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            className="rounded-lg border border-slate-700 bg-slate-800/80 p-3 text-slate-100 file:mr-4 file:cursor-pointer file:rounded-md file:border-0 file:bg-emerald-700 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-slate-100 hover:bg-slate-800"
          />
        </label>
        <button
          type="submit"
          className="inline-flex items-center justify-center rounded-lg bg-emerald-700 px-4 py-2 font-medium text-slate-100 transition-colors hover:bg-emerald-600 disabled:cursor-not-allowed disabled:bg-emerald-900"
          disabled={isLoading}
        >
          {isLoading ? "Processing..." : "Extract Text"}
        </button>
      </form>
      {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
      {result && (
        <div className="mt-5 rounded-xl border border-slate-800 bg-slate-950/70 p-4">
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-sm font-semibold text-emerald-300">
              {result.filename}
            </h3>
            {typeof result.confidence === "number" && (
              <span className="rounded-full border border-emerald-700 bg-emerald-900/60 px-3 py-1 text-xs font-medium text-emerald-200">
                {(result.confidence * 100).toFixed(1)}% confidence
              </span>
            )}
          </div>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-slate-200">
            {result.text || "(No text detected)"}
          </p>
        </div>
      )}
    </div>
  );
}

export default OCRPanel;
