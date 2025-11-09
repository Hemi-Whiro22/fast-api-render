import { useCallback, useEffect, useState } from "react";
import { useApi } from "../hooks/useApi.js";

function MemoryPanel() {
  const { request } = useApi();
  const [entries, setEntries] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [minSimilarity, setMinSimilarity] = useState(0);
  const [searchResults, setSearchResults] = useState([]);
  const [searchError, setSearchError] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const loadMemories = useCallback(async () => {
    setIsLoading(true);
    setError("");
    try {
      const data = await request("/memory");
      setEntries(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Could not fetch memory records.");
    } finally {
      setIsLoading(false);
    }
  }, [request]);

  useEffect(() => {
    loadMemories();
  }, [loadMemories]);

  const handleSearch = useCallback(async (event) => {
    event.preventDefault();
    setSearchError("");
    if (!query.trim()) {
      setSearchError("Enter a prompt to retrieve related memories.");
      return;
    }
    setIsSearching(true);
    try {
      const payload = {
        query: query.trim(),
        top_k: 5,
      };
      const threshold = Number(minSimilarity);
      if (threshold > 0) {
        payload.min_similarity = Number(threshold.toFixed(2));
      }
      const data = await request("/memory/retrieve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const parsed = Array.isArray(data) ? data : [];
      setSearchResults(parsed);
      setHasSearched(true);
    } catch (err) {
      setSearchError(err.message || "Vector retrieval failed.");
    } finally {
      setIsSearching(false);
    }
  }, [minSimilarity, query, request]);

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-lg shadow-slate-900/30">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-slate-200">Memory Vault</h2>
        <button
          type="button"
          onClick={loadMemories}
          className="rounded-md border border-slate-700 px-3 py-1 text-sm text-slate-200 transition-colors hover:border-emerald-500 hover:text-emerald-300"
          disabled={isLoading}
        >
          Refresh
        </button>
      </div>
      <p className="mt-2 text-sm text-slate-300">
        Supabase-backed vector memories surfaced for the awa guardians.
      </p>

  <form className="mt-4 grid gap-3 md:grid-cols-[2fr_1fr_auto]" onSubmit={handleSearch}>
        <div className="flex flex-col gap-2">
          <label className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            Retrieve memories
          </label>
          <input
            type="text"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Ask about stored kupu..."
            className="rounded-lg border border-slate-700 bg-slate-800/80 px-3 py-2 text-sm text-slate-100 focus:border-emerald-500 focus:outline-none"
          />
        </div>
        <div className="flex flex-col gap-2">
          <label className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            Minimum similarity ({minSimilarity.toFixed(2)})
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={minSimilarity}
            onChange={(event) => setMinSimilarity(Number(event.target.value))}
            className="h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-700 accent-emerald-500"
          />
        </div>
        <button
          type="submit"
          className="rounded-lg border border-emerald-700 bg-emerald-800 px-4 py-2 text-sm font-semibold text-emerald-50 transition-colors hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-emerald-900"
          disabled={isSearching}
        >
          {isSearching ? "Searching..." : "Retrieve"}
        </button>
      </form>

      {searchError && <p className="mt-2 text-sm text-red-400">{searchError}</p>}

      {!!searchResults.length && (
        <div className="mt-4 space-y-3">
          <p className="text-xs uppercase tracking-wide text-emerald-300">
            Retrieved memories
          </p>
          <ul className="space-y-3">
            {searchResults.map((result) => (
              <li
                key={`search-${result.id ?? result.content}`}
                className="rounded-xl border border-emerald-800/70 bg-emerald-950/60 p-4"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold uppercase text-emerald-200">
                    {(Number(result.similarity || 0) * 100).toFixed(1)}% match
                  </span>
                  {result.created_at && (
                    <span className="text-xs text-emerald-300/80">
                      {new Date(result.created_at).toLocaleString()}
                    </span>
                  )}
                </div>
                <p className="mt-2 text-sm text-emerald-50">
                  {result.content || "(No content)"}
                </p>
              </li>
            ))}
          </ul>
        </div>
      )}

      {hasSearched && !searchResults.length && !isSearching && !searchError && (
        <p className="mt-3 text-sm text-slate-400">
          No stored memories cleared the similarity threshold.
        </p>
      )}

      {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
      {isLoading && <p className="mt-3 text-sm text-emerald-300">Loading memories...</p>}

      <ul className="mt-4 space-y-3">
        {entries.map((entry) => (
          <li
            key={entry.id ?? `${entry.content?.slice(0, 10)}-${entry.created_at}`}
            className="rounded-xl border border-slate-800 bg-slate-950/70 p-4"
          >
            <p className="text-sm text-slate-200">
              {entry.content || "(No content)"}
            </p>
            {entry.created_at && (
              <p className="mt-2 text-xs uppercase tracking-wide text-slate-500">
                {new Date(entry.created_at).toLocaleString()}
              </p>
            )}
          </li>
        ))}
        {!isLoading && !entries.length && !error && (
          <li className="rounded-xl border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-400">
            No memories stored yet.
          </li>
        )}
      </ul>
    </div>
  );
}

export default MemoryPanel;
