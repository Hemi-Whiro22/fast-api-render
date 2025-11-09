import OCRPanel from "./panels/OCRPanel.jsx";
import TranslatePanel from "./panels/TranslatePanel.jsx";
import MemoryPanel from "./panels/MemoryPanel.jsx";
import IwiPortalPanel from "./panels/IwiPortalPanel.jsx";
import koruIcon from "./assets/koru_spiral.svg";

function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-gradient-to-r from-emerald-900/80 via-slate-900 to-blue-900/80">
        <div className="mx-auto flex max-w-6xl items-center gap-4 px-6 py-6">
          <img src={koruIcon} alt="Tiwhanawhana koru" className="h-12 w-12" />
          <div>
            <p className="text-xs uppercase tracking-wide text-emerald-300/80">
              Tiwhanawhana Orchestrator
            </p>
            <h1 className="text-3xl font-semibold text-slate-100">
              Weaving OCR, Translation, and Memory
            </h1>
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-6xl gap-6 px-6 py-10 md:grid-cols-2">
        <section className="md:col-span-2">
          <IwiPortalPanel />
        </section>
        <section className="md:col-span-2">
          <OCRPanel />
        </section>
        <TranslatePanel />
        <MemoryPanel />
      </main>
    </div>
  );
}

export default App;
