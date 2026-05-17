import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Upload,
  FileText,
  Activity,
  Pill,
  Lightbulb,
  ClipboardList
} from "lucide-react";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState("en");
  const [tab, setTab] = useState("summary");

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    const res = await axios.get("http://127.0.0.1:8000/history");
    setHistory(res.data.reverse());
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("language", language);

    try {
      setLoading(true);
      const res = await axios.post("http://127.0.0.1:8000/process-audio", formData);
      setResult(res.data);
      setTab("report");
      fetchHistory();
    } catch {
      alert("Error processing audio");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">

      {/* SIDEBAR */}
      <div className="w-64 bg-blue-700 text-white p-5">
        <h2 className="text-2xl font-bold mb-6">MedScript</h2>
      </div>

      {/* MAIN */}
      <div className="flex-1 flex flex-col">

        {/* TOPBAR */}
        <div className="bg-white shadow p-4 flex justify-between items-center">
          <h1 className="text-xl font-semibold">Medical Dashboard</h1>

          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="border p-1 rounded"
          >
            <option value="en">English</option>
            <option value="hi">Hindi</option>
          </select>
        </div>

        <div className="flex flex-1">

          {/* LEFT */}
          <div className="flex-1 p-6 overflow-y-auto">

            {/* Upload */}
            <div className="bg-white p-6 rounded-2xl shadow mb-6">
              <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <Upload size={18} /> Upload Consultation
              </h2>

              <input type="file" onChange={(e) => setFile(e.target.files[0])} />

              <button
                onClick={handleUpload}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg w-full mt-4 hover:bg-blue-700"
              >
                {loading ? (
                  <div className="flex justify-center items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Processing...
                  </div>
                ) : (
                  "Upload & Analyze"
                )}
              </button>
            </div>

            {/* EMPTY STATE */}
            {!result && !loading && (
              <div className="text-center text-gray-500 mt-20">
                <FileText size={40} className="mx-auto mb-3" />
                <p>Upload audio to generate medical report</p>
              </div>
            )}

            {/* RESULTS */}
            {result && (
              <>
                {/* TABS */}
                <div className="flex gap-4 mb-4">
                  {["summary", "report", "transcript"].map((t) => (
                    <button
                      key={t}
                      onClick={() => setTab(t)}
                      className={`px-4 py-2 rounded-lg ${
                        tab === t
                          ? "bg-blue-600 text-white"
                          : "bg-white border"
                      }`}
                    >
                      {t.toUpperCase()}
                    </button>
                  ))}
                </div>

                {/* SUMMARY TAB */}
                {tab === "summary" && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                    <Card title="Summary" icon={<FileText size={18} />}>
                      {result.summary}
                    </Card>

                    <Card title="Symptoms" icon={<Activity size={18} />}>
                      {result.entities?.symptoms?.map((s, i) => <li key={i}>{s}</li>)}
                    </Card>

                    <Card title="Medicines" icon={<Pill size={18} />}>
                      {result.entities?.medicines?.map((m, i) => <li key={i}>{m}</li>)}
                    </Card>

                    <Card title="Advice" icon={<Lightbulb size={18} />}>
                      {result.entities?.advice?.map((a, i) => <li key={i}>{a}</li>)}
                    </Card>

                  </div>
                )}

                {/* REPORT TAB (🔥 MAIN FEATURE) */}
                {tab === "report" && (
                  <div className="bg-white p-6 rounded-xl shadow space-y-6">

                    <Section title="Subjective (Complaints)">
                      {result.report?.subjective?.map((i, idx) => <li key={idx}>{i}</li>)}
                    </Section>

                    <Section title="Objective">
                      {result.report?.objective?.map((i, idx) => <li key={idx}>{i}</li>)}
                    </Section>

                    <Section title="Assessment">
                      <p>{result.report?.assessment}</p>
                    </Section>

                    <Section title="Plan">
                      <h4 className="font-semibold mt-2">Medicines</h4>
                      <ul className="list-disc pl-5">
                        {result.report?.plan?.medicines?.map((m, i) => <li key={i}>{m}</li>)}
                      </ul>

                      <h4 className="font-semibold mt-2">Advice</h4>
                      <ul className="list-disc pl-5">
                        {result.report?.plan?.advice?.map((a, i) => <li key={i}>{a}</li>)}
                      </ul>
                    </Section>

                    <div className="text-center">
                      <a
                        href={`http://127.0.0.1:8000/download-report/${result.id}`}
                        className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
                      >
                        Download Report
                      </a>
                    </div>
                  </div>
                )}

                {/* TRANSCRIPT TAB */}
                {tab === "transcript" && (
                  <div className="bg-white p-6 rounded-xl shadow space-y-4">
                    <Section title="Raw Transcript">
                      <p>{result.raw_transcript}</p>
                    </Section>

                    <Section title="Corrected Transcript">
                      <p>{result.corrected_transcript}</p>
                    </Section>
                  </div>
                )}
              </>
            )}
          </div>

          {/* RIGHT: HISTORY */}
          <div className="w-80 bg-white border-l p-4 overflow-y-auto">
            <h2 className="text-lg font-semibold mb-4">History</h2>

            {history.map((item) => (
              <div
                key={item.id}
                className="mb-3 p-3 border rounded cursor-pointer hover:bg-gray-100"
                onClick={() => {
                  setResult(item);
                  setTab("report");
                }}
              >
                <p className="text-sm line-clamp-2">{item.summary}</p>
                <p className="text-xs text-gray-500">ID: {item.id}</p>
              </div>
            ))}
          </div>

        </div>
      </div>
    </div>
  );
}

/* 🔹 Components */

const Card = ({ title, icon, children }) => (
  <div className="bg-white p-5 rounded-xl shadow">
    <h3 className="font-semibold mb-2 flex items-center gap-2">
      {icon} {title}
    </h3>
    <ul className="list-disc pl-5 text-gray-700">
      {typeof children === "string" ? <p>{children}</p> : children}
    </ul>
  </div>
);

const Section = ({ title, children }) => (
  <div>
    <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
      <ClipboardList size={18} /> {title}
    </h3>
    <div className="text-gray-700">{children}</div>
  </div>
);

export default App;