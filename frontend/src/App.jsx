import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import Dashboard from "./components/Dashboard";
import "./index.css";

const API_BASE = window.location.hostname === "localhost"
  ? "http://localhost:8000"
  : "/api";

function App() {
  const [rfpFile, setRfpFile] = useState(null);
  const [companyFile, setCompanyFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');
  const [view, setView] = useState('upload');
  const reportRef = useRef(null);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const handleFileUpload = async () => {
    if (!rfpFile) return;

    const formData = new FormData();
    formData.append("file", rfpFile);
    if (companyFile) {
      formData.append("company_file", companyFile);
    }

    setLoading(true);
    setResponse(null);

    try {
      const res = await axios.post(`${API_BASE}/analyze/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResponse(res.data);
      setView('analysis');
    } catch (err) {
      console.error("Error:", err);
      alert("Failed to analyze RFP. Ensure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const resetUpload = () => {
    setRfpFile(null);
    setCompanyFile(null);
    setResponse(null);
    setView('upload');
  };

  const downloadPDF = async () => {
    const element = reportRef.current;
    if (!element) return;

    element.classList.add('pdf-export-mode');

    try {
      const canvas = await html2canvas(element, {
        scale: 3,
        useCORS: true,
        logging: false,
        backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--bg').trim() || '#050508',
        windowWidth: 1200,
      });

      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF("p", "mm", "a4");
      const pageWidth = pdf.internal.pageSize.getWidth();
      const margin = 10;
      const contentWidth = pageWidth - (margin * 2);
      const imgProps = pdf.getImageProperties(imgData);
      const contentHeight = (imgProps.height * contentWidth) / imgProps.width;

      pdf.addImage(imgData, "PNG", margin, margin, contentWidth, contentHeight);
      pdf.save(`Agentic_Analysis_Report_${new Date().getTime()}.pdf`);
    } catch (error) {
      console.error("PDF Export Error:", error);
      alert("Failed to generate PDF.");
    } finally {
      element.classList.remove('pdf-export-mode');
    }
  };

  return (
    <div className="view-container">
      {/* Dynamic Background Glow */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary opacity-10 blur-[120px] rounded-full"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-secondary opacity-10 blur-[120px] rounded-full"></div>

      <button onClick={toggleTheme} className="theme-switch" title="Toggle Essence">
        {theme === 'dark' ? '⚡' : '✨'}
      </button>

      {view === 'upload' ? (
        <div className="flex-1 flex flex-col items-center justify-center animate-entrance z-10 px-4">
          <header className="text-center mb-10">
            <h1 className="text-7xl font-black mb-4 drop-shadow-2xl">
              RFP <span className="text-primary italic">AI</span>
            </h1>
            <p className="text-lg max-w-xl mx-auto font-medium text-muted-opacity leading-relaxed">
              Upload your RFP and optionally inject custom company context for real-time compliance mapping.
            </p>
          </header>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-4xl">
            {/* RFP Upload */}
            <div className={`glass-card p-8 text-center border-2 border-dashed ${rfpFile ? 'border-success' : 'border-glass-border'}`}>
              <div className="text-4xl mb-4">📜</div>
              <h3 className="text-xl font-bold mb-2">RFP Document</h3>
              <p className="text-xs text-muted-opacity mb-6">Target analysis file (PDF/DOCX)</p>
              <input
                type="file"
                id="rfp-input"
                className="hidden"
                accept=".pdf,.doc,.docx"
                onChange={(e) => setRfpFile(e.target.files[0])}
              />
              <label htmlFor="rfp-input" className="glow-btn block w-full text-center py-3 text-sm cursor-pointer">
                {rfpFile ? rfpFile.name.substring(0, 15) + '...' : 'Select RFP'}
              </label>
            </div>

            {/* Company Data Upload */}
            <div className={`glass-card p-8 text-center border-2 border-dashed ${companyFile ? 'border-secondary' : 'border-glass-border'}`}>
              <div className="text-4xl mb-4">🏢</div>
              <h3 className="text-xl font-bold mb-2">Company Context</h3>
              <p className="text-xs text-muted-opacity mb-6">Optional source data (PDF/DOCX)</p>
              <input
                type="file"
                id="company-input"
                className="hidden"
                accept=".pdf,.doc,.docx"
                onChange={(e) => setCompanyFile(e.target.files[0])}
              />
              <label htmlFor="company-input" className="glow-btn block w-full text-center py-3 text-sm cursor-pointer" style={{ background: 'linear-gradient(45deg, var(--secondary), var(--accent))' }}>
                {companyFile ? companyFile.name.substring(0, 15) + '...' : 'Add Context'}
              </label>
            </div>
          </div>

          <div className="mt-10 w-full max-w-4xl">
            <button
              onClick={handleFileUpload}
              disabled={!rfpFile || loading}
              className={`glow-btn w-full py-5 text-xl ${loading ? 'opacity-50' : ''}`}
            >
              {loading ? "Igniting Neural RAG..." : "Analyze Synergy"}
            </button>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex flex-col overflow-hidden animate-entrance z-10">
          <header className="flex justify-between items-start mb-6 pr-20">
            <div>
              <h1 className="text-5xl font-black tracking-tight">
                Analysis <span className="text-primary italic">Synergy</span>
              </h1>
              <p className="text-sm font-bold text-secondary uppercase tracking-widest mt-1">
                Matched against: {companyFile ? companyFile.name : 'Static Profile'}
              </p>
            </div>
            <div className="flex gap-4 items-center mt-2">
              <button
                onClick={downloadPDF}
                className="glow-btn px-6 py-2.5 text-[10px] font-black uppercase tracking-[0.2em]"
              >
                🚀 Export Neural Report
              </button>
              <button
                onClick={resetUpload}
                className="glow-btn px-6 py-2.5 text-[10px] font-black uppercase tracking-[0.2em]"
              >
                ← Restart Analysis
              </button>
            </div>
          </header>
          <div className="scroll-area">
            {response && <Dashboard data={response} reportRef={reportRef} />}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
