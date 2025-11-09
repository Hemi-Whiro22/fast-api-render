import { useState } from "react";
import { useApi } from "../hooks/useApi.js";

function TranslatePanel() {
  const { request } = useApi();
  const [text, setText] = useState("");
  const [targetLanguage, setTargetLanguage] = useState("te reo Māori");
  const [translation, setTranslation] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setIsLoading(true);
    try {
      const data = await request("/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, target_language: targetLanguage }),
      });
      setTranslation(data.translation);
    } catch (err) {
      setError(err.message || "Translation failed.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="rounded-2xl border border-blue-900/60 bg-slate-900/70 p-6 shadow-lg shadow-blue-900/20">
      <h2 className="text-xl font-semibold text-blue-200">Translate Kupu</h2>
      <p className="mt-2 text-sm text-slate-300">
        Relay text to the OpenAI navigator and receive kōrero in the language you
        choose.
      </p>
      <form className="mt-5 flex flex-col gap-4" onSubmit={handleSubmit}>
        <label className="text-sm text-slate-200">
          Source text
          <textarea
            required
            rows={6}
            value={text}
            onChange={(event) => setText(event.target.value)}
            className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-800/80 p-3 text-slate-100 focus:border-blue-500 focus:outline-none"
          />
        </label>
        <label className="text-sm text-slate-200">
          Target language
          <input
            value={targetLanguage}
            onChange={(event) => setTargetLanguage(event.target.value)}
            className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-800/80 p-3 text-slate-100 focus:border-blue-500 focus:outline-none"
          />
        </label>
        <button
          type="submit"
          className="inline-flex items-center justify-center rounded-lg bg-blue-700 px-4 py-2 font-medium text-slate-100 transition-colors hover:bg-blue-600 disabled:cursor-not-allowed disabled:bg-blue-900"
          disabled={isLoading}
        >
          {isLoading ? "Translating..." : "Translate"}
        </button>
      </form>
      {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
      {translation && (
        <div className="mt-5 rounded-xl border border-slate-800 bg-slate-950/70 p-4">
          <h3 className="text-sm font-semibold text-blue-300">Translation</h3>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-slate-200">
            {translation}
          </p>
        </div>
      )}
    </div>
  );
}

export default TranslatePanel;
