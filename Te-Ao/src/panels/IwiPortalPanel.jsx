// frontend/src/panels/IwiPortalPanel.jsx
// Iwi Portal UI - OCR, Translation, Archive, Ingest
// Integrated with Te Puna public schema for archive structure awareness

import React, { useState, useEffect } from "react";
import { useIwiPortal } from "../hooks/useIwiPortal";
import publicSchema from "../data/public_schema_te_puna.json";

const IwiPortalPanel = () => {
    const [activeTab, setActiveTab] = useState("ocr");
    const [ocrText, setOcrText] = useState("");
    const [translateText, setTranslateText] = useState("");
    const [translateResult, setTranslateResult] = useState("");
    const [archiveRecords, setArchiveRecords] = useState([]);
    const [portalStatus, setPortalStatus] = useState(null);

    const {
        loading,
        error,
        uploadOCR,
        translateText: apiTranslate,
        fetchArchive,
        ingestRecord,
        checkStatus,
    } = useIwiPortal();

    // Check portal status on mount
    useEffect(() => {
        checkStatus().then(setPortalStatus);
    }, []);

    // Fetch archive on tab switch
    useEffect(() => {
        if (activeTab === "archive") {
            fetchArchive(20).then((data) => {
                setArchiveRecords(data.data || []);
            });
        }
    }, [activeTab]);

    // Handle OCR file upload
    const handleOCRUpload = async (e) => {
        const file = e.target.files?.[0];
        if (!file) return;

        try {
            const result = await uploadOCR(file);
            setOcrText(result.text);
        } catch (err) {
            console.error("OCR upload failed:", err);
        }
    };

    // Handle translation
    const handleTranslate = async () => {
        if (!translateText.trim()) {
            alert("Please enter text to translate");
            return;
        }

        try {
            const result = await apiTranslate(translateText, "auto", "en");
            setTranslateResult(result.translated_text);
        } catch (err) {
            console.error("Translation failed:", err);
        }
    };

    // Handle ingest
    const handleIngest = async () => {
        if (!translateResult.trim()) {
            alert("Translate text first, then ingest");
            return;
        }

        try {
            await ingestRecord(
                "Portal Ingest",
                translateResult,
                "iwi-portal",
                "text",
                { timestamp: new Date().toISOString() }
            );
            alert("✅ Ingest saved to Alpha-Den");
            setTranslateResult("");
        } catch (err) {
            console.error("Ingest failed:", err);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-green-900 p-6">
            {/* Header */}
            <div className="max-w-6xl mx-auto mb-8">
                <h1 className="text-4xl font-bold text-white mb-2">🪶 Iwi Portal</h1>
                <p className="text-gray-300">
                    OCR • Translation • Archive • Ingestion
                </p>
                {portalStatus && (
                    <div className="mt-2 text-sm text-green-300">
                        ✅ Portal Online | DEN: {portalStatus.den_status} | TE PUNA:{" "}
                        {portalStatus.tepuna_status}
                    </div>
                )}
            </div>

            {/* Tabs */}
            <div className="max-w-6xl mx-auto mb-6 flex gap-2 border-b border-gray-600">
                {["ocr", "translate", "archive", "ingest"].map((tab) => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`px-4 py-2 font-semibold uppercase text-sm transition ${activeTab === tab
                            ? "text-green-400 border-b-2 border-green-400"
                            : "text-gray-400 hover:text-gray-200"
                            }`}
                    >
                        {tab === "ocr" && "📷 OCR"}
                        {tab === "translate" && "🌐 Translate"}
                        {tab === "archive" && "📚 Archive"}
                        {tab === "ingest" && "💾 Ingest"}
                    </button>
                ))}
            </div>

            {/* OCR Tab */}
            {activeTab === "ocr" && (
                <div className="max-w-2xl mx-auto">
                    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                        <h2 className="text-xl font-bold text-white mb-4">
                            📷 Image to Text (OCR)
                        </h2>
                        <div className="border-2 border-dashed border-gray-500 rounded p-6 text-center hover:border-green-400 transition">
                            <input
                                type="file"
                                accept="image/*"
                                onChange={handleOCRUpload}
                                disabled={loading}
                                className="hidden"
                                id="ocr-input"
                            />
                            <label
                                htmlFor="ocr-input"
                                className="cursor-pointer text-gray-300 hover:text-white"
                            >
                                {loading ? "Processing..." : "📁 Click to upload image"}
                            </label>
                        </div>

                        {ocrText && (
                            <div className="mt-6 bg-gray-900 rounded p-4">
                                <p className="text-sm text-gray-400 mb-2">Extracted Text:</p>
                                <textarea
                                    value={ocrText}
                                    onChange={(e) => setOcrText(e.target.value)}
                                    className="w-full h-32 bg-gray-700 text-white p-3 rounded border border-gray-600 focus:border-green-400 outline-none"
                                    placeholder="OCR results will appear here"
                                />
                            </div>
                        )}

                        {error && <div className="mt-4 text-red-400 text-sm">❌ {error}</div>}
                    </div>
                </div>
            )}

            {/* Translate Tab */}
            {activeTab === "translate" && (
                <div className="max-w-2xl mx-auto">
                    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                        <h2 className="text-xl font-bold text-white mb-4">🌐 Translate</h2>
                        <div className="grid grid-cols-1 gap-4">
                            <div>
                                <label className="block text-gray-300 text-sm mb-2">
                                    Original Text
                                </label>
                                <textarea
                                    value={translateText}
                                    onChange={(e) => setTranslateText(e.target.value)}
                                    placeholder="Enter text to translate"
                                    className="w-full h-24 bg-gray-700 text-white p-3 rounded border border-gray-600 focus:border-green-400 outline-none"
                                />
                            </div>

                            <button
                                onClick={handleTranslate}
                                disabled={loading}
                                className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-bold py-2 px-4 rounded transition"
                            >
                                {loading ? "Translating..." : "✨ Translate"}
                            </button>

                            {translateResult && (
                                <div>
                                    <label className="block text-gray-300 text-sm mb-2">
                                        Translated Text
                                    </label>
                                    <textarea
                                        value={translateResult}
                                        readOnly
                                        className="w-full h-24 bg-gray-900 text-white p-3 rounded border border-gray-600"
                                    />
                                </div>
                            )}
                        </div>

                        {error && <div className="mt-4 text-red-400 text-sm">❌ {error}</div>}
                    </div>
                </div>
            )}

            {/* Archive Tab */}
            {activeTab === "archive" && (
                <div className="max-w-4xl mx-auto">
                    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                        <h2 className="text-xl font-bold text-white mb-4">
                            📚 Te Puna Archive (Read-Only)
                        </h2>

                        {/* Schema Info */}
                        <div className="mb-6 p-3 bg-gray-900 rounded border border-gray-600 text-xs text-gray-300">
                            <p className="font-bold text-green-300 mb-2">🪶 Archive Tables Available:</p>
                            <div className="grid grid-cols-2 gap-2">
                                {Object.entries(publicSchema.tables || {}).map(([tableName, tableInfo]) => (
                                    <div key={tableName} className="text-gray-400">
                                        <span className="text-green-400 font-mono">{tableName}</span>
                                        <span className="text-gray-500"> ({tableInfo.column_count} fields)</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {loading ? (
                            <p className="text-gray-400">Loading archive...</p>
                        ) : archiveRecords.length > 0 ? (
                            <div className="grid gap-4">
                                {archiveRecords.map((record) => (
                                    <div
                                        key={record.id}
                                        className="bg-gray-900 rounded p-4 border border-gray-600 hover:border-green-400 transition"
                                    >
                                        <h3 className="text-green-300 font-bold">{record.title}</h3>
                                        <p className="text-gray-400 text-sm mt-1">{record.content}</p>
                                        <div className="text-gray-500 text-xs mt-2">
                                            {record.source} • {record.created_at}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-gray-400">No archive records found</p>
                        )}

                        {error && <div className="mt-4 text-red-400 text-sm">❌ {error}</div>}
                    </div>
                </div>
            )}

            {/* Ingest Tab */}
            {activeTab === "ingest" && (
                <div className="max-w-2xl mx-auto">
                    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                        <h2 className="text-xl font-bold text-white mb-4">
                            💾 Ingest to Alpha-Den
                        </h2>

                        <div className="bg-blue-900 border border-blue-600 rounded p-4 mb-4 text-sm text-blue-200">
                            📝 Workflow: Upload Image → OCR → Translate → Ingest
                        </div>

                        {translateResult ? (
                            <div>
                                <div className="bg-gray-900 rounded p-4 mb-4 border border-gray-600">
                                    <p className="text-gray-300 text-sm">Content to Ingest:</p>
                                    <p className="text-white mt-2">{translateResult}</p>
                                </div>

                                <button
                                    onClick={handleIngest}
                                    disabled={loading}
                                    className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-bold py-3 px-4 rounded transition"
                                >
                                    {loading ? "Ingesting..." : "✅ Save to Alpha-Den"}
                                </button>
                            </div>
                        ) : (
                            <p className="text-gray-400">
                                Complete translation first to ingest
                            </p>
                        )}

                        {error && <div className="mt-4 text-red-400 text-sm">❌ {error}</div>}
                    </div>
                </div>
            )}
        </div>
    );
};

export default IwiPortalPanel;
