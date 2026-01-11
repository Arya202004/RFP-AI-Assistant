import React from "react";

const Dashboard = ({ data, reportRef }) => {
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (data.eligibility_score / 100) * circumference;

  const getScoreColorClass = (score) => {
    if (score > 50) return "score-green shadow-[0_0_20px_var(--success)]";
    if (score === 50) return "score-orange shadow-[0_0_20px_var(--warning)]";
    return "score-red shadow-[0_0_20px_var(--primary)]";
  };

  const getStrokeColorClass = (score) => {
    if (score > 50) return "stroke-green animate-pulse-neon";
    if (score === 50) return "stroke-orange";
    return "stroke-red animate-pulse-neon";
  };

  const scoreColorClass = getScoreColorClass(data.eligibility_score);
  const strokeColorClass = getStrokeColorClass(data.eligibility_score);

  return (
    <div ref={reportRef} className="pt-8 pb-10 rounded-3xl" style={{ backgroundColor: 'transparent' }}>
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

        {/* Match Index - Infographic */}
        <div className="lg:col-span-4 glass-card p-10 text-center flex flex-col items-center justify-center relative overflow-hidden group min-h-[420px]">
          <div className="absolute top-0 right-0 w-32 h-32 bg-primary opacity-5 blur-3xl group-hover:opacity-20 transition-opacity"></div>
          <h2 className="text-3xl font-black mb-10 tracking-tighter opacity-90">
            Match <span className="text-primary italic">Index</span>
          </h2>
          <div className="gauge-container relative w-44 h-44 animate-float">
            <svg width="180" height="180" className="transform -rotate-90">
              <circle
                stroke="var(--glass-border)"
                strokeWidth="12"
                fill="transparent"
                r={radius}
                cx="90"
                cy="90"
              />
              <circle
                className={`progress-ring__circle ${strokeColorClass}`}
                strokeWidth="12"
                strokeDasharray={`${circumference} ${circumference}`}
                style={{ strokeDashoffset: offset }}
                fill="transparent"
                r={radius}
                cx="90"
                cy="90"
                strokeLinecap="round"
              />
            </svg>
            <div className={`percentage-text absolute inset-0 flex items-center justify-center text-5xl font-black tracking-tighter ${scoreColorClass}`}>
              {data.eligibility_score}%
            </div>
          </div>
          <ul className="mt-10 space-y-3 w-full max-w-[320px]">
            {data.summary.split('.').filter(s => s.trim()).map((sentence, idx) => (
              <li key={idx} className="flex items-start gap-3 text-[10px] font-black opacity-80 leading-relaxed uppercase tracking-widest bg-white/5 py-2.5 px-5 rounded-2xl border border-white/10 text-left">
                <span className="text-primary mt-0.5">•</span>
                <span>{sentence.trim()}.</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Neural Insights Section */}
        <div className="lg:col-span-8 glass-card p-12 relative group min-h-[420px]">
          <div className="absolute top-0 left-0 w-48 h-48 bg-secondary opacity-5 blur-3xl group-hover:opacity-20 transition-opacity"></div>
          <h2 className="text-4xl font-black mb-8 tracking-tighter opacity-90">
            <span className="text-primary italic">Insights</span>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            <div className="animate-slide-right" style={{ animationDelay: '0.1s' }}>
              <h1 className="text-xs uppercase tracking-[0.2em] font-black mb-6 flex items-center opacity-90">
                <div className="w-2.5 h-2.5 bg-success rounded-full mr-3 shadow-[0_0_15px_var(--success)] animate-pulse"></div>
                Winnable Factors
              </h1>
              <ul className="space-y-5">
                {data.matched_criteria.map((item, i) => (
                  <li key={i} className="flex items-start text-sm font-black hover:translate-x-1 transition-transform cursor-default score-green">
                    <span className="mr-3 font-black text-xl leading-none">✓</span> {item}
                  </li>
                ))}
              </ul>
            </div>
            <div className="animate-slide-right" style={{ animationDelay: '0.3s' }}>
              <h1 className="text-xs uppercase tracking-[0.2em] font-black mb-6 flex items-center opacity-90">
                <div className="w-2.5 h-2.5 bg-primary rounded-full mr-3 shadow-[0_0_15px_var(--primary)] animate-pulse"></div>
                Risk Vertices
              </h1>
              <ul className="space-y-5">
                {data.risks.map((item, i) => (
                  <li key={i} className="flex items-start text-sm font-black hover:translate-x-1 transition-transform cursor-default score-red">
                    <span className="mr-3 font-black text-xl leading-none">✕</span> {item}
                  </li>
                ))}
                {data.risks.length === 0 && <li className="text-muted-opacity italic text-xs">No anomalies detected in stream.</li>}
              </ul>
            </div>
          </div>
        </div>

        {/* Compliance Matrix - Expanded & Systematic Alignment */}
        <div className="lg:col-span-12 glass-card p-12 relative overflow-hidden group">
          <div className="absolute -bottom-10 -right-10 w-64 h-64 bg-accent opacity-[0.05] blur-3xl group-hover:opacity-20 transition-opacity"></div>
          <div className="flex justify-between items-center mb-10">
            <h2 className="text-4xl font-black tracking-tighter opacity-95">
              Compliance <span className="text-primary italic">Matrix</span>
            </h2>
            <div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
            {data.checklist.map((item, i) => (
              <div key={i}
                className={`flex items-center p-6 rounded-[2.5rem] border transition-all hover:scale-[1.03] active:scale-95 animate-slide-right ${item.status === "Available" ? "border-success/40 bg-success/5 shadow-[0_0_20px_rgba(34,197,94,0.05)]" : "border-glass-border bg-white/5"}`}
                style={{ animationDelay: `${0.1 * i}s` }}>
                <div className={`w-3.5 h-3.5 rounded-full mr-5 ${item.status === "Available" ? "bg-success shadow-[0_0_15px_var(--success)]" : "bg-white/10 shadow-[inner_0_0_10px_rgba(255,255,255,0.05)]"}`}></div>
                <div>
                  <div className="text-[12px] font-black uppercase tracking-widest leading-none mb-2 opacity-95">{item.item}</div>
                  <div className={`text-[10px] font-black uppercase tracking-widest ${item.status === "Available" ? "text-success" : "text-muted-opacity"}`}>
                    {item.status}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div>

          </div>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
