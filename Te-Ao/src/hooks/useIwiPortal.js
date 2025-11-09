// frontend/src/hooks/useIwiPortal.js
// Iwi Portal API integration hook

import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const useIwiPortal = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    /**
     * Upload image for OCR processing
     */
    const uploadOCR = async (file) => {
        setLoading(true);
        setError(null);
        try {
            const formData = new FormData();
            formData.append("file", file);

            const response = await fetch(`${API_BASE}/iwi/ocr`, {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`OCR failed: ${response.statusText}`);
            }

            const data = await response.json();
            console.log("✅ OCR result:", data);
            return data;
        } catch (err) {
            setError(err.message);
            console.error("❌ OCR error:", err);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    /**
     * Translate text via OpenAI
     */
    const translateText = async (text, sourceLang = "auto", targetLang = "en") => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE}/iwi/translate`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    text,
                    source_lang: sourceLang,
                    target_lang: targetLang,
                }),
            });

            if (!response.ok) {
                throw new Error(`Translation failed: ${response.statusText}`);
            }

            const data = await response.json();
            console.log("✅ Translation result:", data);
            return data;
        } catch (err) {
            setError(err.message);
            console.error("❌ Translation error:", err);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    /**
     * Fetch Te Puna archive records
     */
    const fetchArchive = async (limit = 20) => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE}/iwi/archive?limit=${limit}`);

            if (!response.ok) {
                throw new Error(`Archive fetch failed: ${response.statusText}`);
            }

            const data = await response.json();
            console.log(`✅ Archive fetch: ${data.count} records`);
            return data;
        } catch (err) {
            setError(err.message);
            console.error("❌ Archive fetch error:", err);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    /**
     * Ingest record metadata to Alpha-Den
     */
    const ingestRecord = async (title, content, source, fileType = "text", metadata = {}) => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE}/iwi/ingest`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    title,
                    content,
                    source,
                    file_type: fileType,
                    metadata,
                }),
            });

            if (!response.ok) {
                throw new Error(`Ingest failed: ${response.statusText}`);
            }

            const data = await response.json();
            console.log("✅ Ingest result:", data);
            return data;
        } catch (err) {
            setError(err.message);
            console.error("❌ Ingest error:", err);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    /**
     * Check portal status
     */
    const checkStatus = async () => {
        try {
            const response = await fetch(`${API_BASE}/iwi/status`);
            if (!response.ok) {
                throw new Error("Portal unavailable");
            }
            const data = await response.json();
            return data;
        } catch (err) {
            console.error("❌ Status check failed:", err);
            return null;
        }
    };

    return {
        loading,
        error,
        uploadOCR,
        translateText,
        fetchArchive,
        ingestRecord,
        checkStatus,
    };
};
