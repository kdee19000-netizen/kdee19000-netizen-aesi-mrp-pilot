import React, { useState } from 'react';

export const AnonymousReportForm = ({ domain }) => {
  const [anonymous, setAnonymous] = useState(false);
  const [report, setReport] = useState('');
  const [trackingCode, setTrackingCode] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!report.trim()) return;
    setSubmitting(true);
    setError(null);

    try {
      const endpointMap = {
        workplace: '/api/enterprise/workplace',
        public_safety: '/api/enterprise/public-safety',
        commerce: '/api/enterprise/commerce',
      };
      const endpoint = endpointMap[domain] || '/api/enterprise/workplace';

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: report,
          anonymous: anonymous,
          user_id: anonymous ? null : (window.currentUser?.id ?? null)
        })
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      if (anonymous && data.tracking_code) {
        setTrackingCode(data.tracking_code);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="anonymous-report-form">
      <div className="anonymity-toggle">
        <label>
          <input
            type="checkbox"
            checked={anonymous}
            onChange={(e) => setAnonymous(e.target.checked)}
          />
          Submit anonymously (your identity will be protected)
        </label>
      </div>

      <textarea
        value={report}
        onChange={(e) => setReport(e.target.value)}
        placeholder="Describe what happened. Your report is confidential."
        rows={10}
      />

      <button
        onClick={handleSubmit}
        className="submit-report"
        disabled={submitting || !report.trim()}
      >
        {submitting ? 'Submitting...' : 'Submit Confidential Report'}
      </button>

      {error && (
        <div className="error-message" role="alert">
          <p>Error submitting report: {error}</p>
        </div>
      )}

      {trackingCode && (
        <div className="tracking-code-display">
          <h3>⚠️ Save This Tracking Code</h3>
          <code>{trackingCode}</code>
          <p>Use this code to check the status of your anonymous report.</p>
        </div>
      )}
    </div>
  );
};
