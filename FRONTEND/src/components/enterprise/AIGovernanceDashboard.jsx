import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import './AIGovernanceDashboard.css';

/* --------------------------------------------------------------------------
   Mock data — mirrors the AI risk types defined in
   BACKEND-FASTAPI/domains/ai_governance.py (AIRiskType enum)
   In production replace fetchMetrics / fetchIncidents with real API calls.
   -------------------------------------------------------------------------- */

const RISK_SEVERITY = {
  unsafe_output: 'critical',
  harmful_instruction: 'critical',
  privacy_leak: 'critical',
  jailbreak_attempt: 'high',
  bias_detected: 'high',
  manipulation: 'medium',
  misinformation: 'medium',
  hallucination: 'low',
};

const RISK_LABELS = {
  unsafe_output: 'Unsafe Output',
  harmful_instruction: 'Harmful Instruction',
  privacy_leak: 'Privacy Leak',
  jailbreak_attempt: 'Jailbreak Attempt',
  bias_detected: 'Bias Detected',
  manipulation: 'Manipulation',
  misinformation: 'Misinformation',
  hallucination: 'Hallucination',
};

const RISK_ACCENT_COLORS = {
  critical: 'var(--ag-risk-critical)',
  high: 'var(--ag-risk-high)',
  medium: 'var(--ag-risk-medium)',
  low: 'var(--ag-risk-low)',
  info: 'var(--ag-risk-info)',
};

function buildMockMetrics(seed = 0) {
  // Deterministic variation so "refresh" shows a plausible change.
  const jitter = (base, range) =>
    base + Math.round(((seed * 13 + base * 7) % range) - range / 2);
  return {
    total_incidents: jitter(142, 20),
    critical_open: jitter(7, 4),
    pending_review: jitter(23, 8),
    resolved_today: jitter(18, 6),
    blocked_outputs: jitter(34, 10),
    avg_response_min: jitter(12, 6),
  };
}

function buildMockRiskBreakdown(seed = 0) {
  const base = {
    unsafe_output: 28,
    bias_detected: 22,
    jailbreak_attempt: 19,
    harmful_instruction: 14,
    privacy_leak: 11,
    misinformation: 8,
    manipulation: 6,
    hallucination: 4,
  };
  return Object.entries(base).map(([key, count]) => ({
    key,
    label: RISK_LABELS[key],
    count: count + ((seed * 3 + count) % 5),
    severity: RISK_SEVERITY[key],
  }));
}

const BASE_INCIDENTS = [
  {
    id: 'inc-001',
    risk_type: 'unsafe_output',
    summary:
      'Model returned instructions referencing harmful content. Output was intercepted and replaced with safe fallback.',
    timestamp: new Date(Date.now() - 1000 * 60 * 4).toISOString(),
    model_version: 'llm-v3.2.1',
    actions_required: ['immediate_model_review', 'safety_filter_update'],
    output_blocked: true,
    mrp_case_created: true,
  },
  {
    id: 'inc-002',
    risk_type: 'jailbreak_attempt',
    summary:
      'User sent "ignore previous instructions" prompt. System prompt injection attempt blocked.',
    timestamp: new Date(Date.now() - 1000 * 60 * 17).toISOString(),
    model_version: 'llm-v3.2.1',
    actions_required: ['incident_report_to_compliance'],
    output_blocked: true,
    mrp_case_created: false,
  },
  {
    id: 'inc-003',
    risk_type: 'bias_detected',
    summary:
      'Response contained a generalized stereotype. Bias analysis and retraining evaluation scheduled.',
    timestamp: new Date(Date.now() - 1000 * 60 * 44).toISOString(),
    model_version: 'llm-v3.1.9',
    actions_required: ['bias_analysis', 'retraining_evaluation', 'fairness_audit'],
    output_blocked: false,
    mrp_case_created: true,
  },
  {
    id: 'inc-004',
    risk_type: 'privacy_leak',
    summary:
      'Output contained a pattern matching private PII structure. Compliance notified.',
    timestamp: new Date(Date.now() - 1000 * 60 * 92).toISOString(),
    model_version: 'llm-v3.2.0',
    actions_required: ['immediate_model_review', 'incident_report_to_compliance'],
    output_blocked: true,
    mrp_case_created: true,
  },
  {
    id: 'inc-005',
    risk_type: 'hallucination',
    summary:
      'Model cited a non-existent academic source as fact. Fact-checking layer enhancement queued.',
    timestamp: new Date(Date.now() - 1000 * 60 * 180).toISOString(),
    model_version: 'llm-v3.1.8',
    actions_required: ['fact_checking_layer_enhancement'],
    output_blocked: false,
    mrp_case_created: false,
  },
];

/** Simulates a backend call — resolves after a short delay */
async function fetchMetrics(seed) {
  await new Promise((r) => setTimeout(r, 420));
  return buildMockMetrics(seed);
}

async function fetchRiskBreakdown(seed) {
  await new Promise((r) => setTimeout(r, 320));
  return buildMockRiskBreakdown(seed);
}

async function fetchIncidents() {
  await new Promise((r) => setTimeout(r, 500));
  return BASE_INCIDENTS;
}

const BASE_POLICIES = [
  {
    id: 'pol-001',
    type: 'decision_constraint',
    title: 'Output Safety Gate',
    description:
      'All model outputs must pass the real-time safety intercept before delivery to end users.',
    applies_to: ['unsafe_output', 'harmful_instruction'],
    enforcement: 'automatic_block',
    review_interval_days: 30,
    status: 'active',
  },
  {
    id: 'pol-002',
    type: 'adjudication_policy',
    title: 'Bias Escalation Protocol',
    description:
      'Detected bias incidents are escalated to the AI Ethics Reviewer within 60 minutes. Human adjudication required before model retrain.',
    applies_to: ['bias_detected'],
    enforcement: 'human_review',
    review_interval_days: 7,
    status: 'active',
  },
  {
    id: 'pol-003',
    type: 'decision_constraint',
    title: 'PII Redaction Mandate',
    description:
      'Any output matching PII patterns is immediately redacted and the incident is logged to compliance.',
    applies_to: ['privacy_leak'],
    enforcement: 'automatic_block',
    review_interval_days: 90,
    status: 'active',
  },
  {
    id: 'pol-004',
    type: 'adjudication_policy',
    title: 'Jailbreak Adjudication',
    description:
      'Prompt injection and jailbreak attempts trigger a compliance report and require ai_safety_team sign-off within 15 minutes.',
    applies_to: ['jailbreak_attempt'],
    enforcement: 'human_review',
    review_interval_days: 14,
    status: 'under_review',
  },
  {
    id: 'pol-005',
    type: 'decision_constraint',
    title: 'Hallucination Disclosure',
    description:
      'Outputs flagged for hallucination must include a disclosure notice and be routed to fact-checking enhancement.',
    applies_to: ['hallucination', 'misinformation'],
    enforcement: 'disclosure_required',
    review_interval_days: 60,
    status: 'active',
  },
];

const BASE_AUDIT_HISTORY = [
  {
    id: 'aud-001',
    event_type: 'output_blocked',
    risk_type: 'unsafe_output',
    actor: 'ai_safety_team',
    outcome:
      'Output intercepted; safe fallback delivered to user. Incident escalated to compliance team.',
    timestamp: new Date(Date.now() - 1000 * 60 * 8).toISOString(),
    model_version: 'llm-v3.2.1',
  },
  {
    id: 'aud-002',
    event_type: 'policy_reviewed',
    risk_type: 'bias_detected',
    actor: 'ai_ethics_reviewer',
    outcome:
      'Bias analysis completed. Stereotype pattern confirmed. Retraining evaluation scheduled for next sprint.',
    timestamp: new Date(Date.now() - 1000 * 60 * 35).toISOString(),
    model_version: 'llm-v3.1.9',
  },
  {
    id: 'aud-003',
    event_type: 'jailbreak_blocked',
    risk_type: 'jailbreak_attempt',
    actor: 'ai_safety_team',
    outcome:
      'Prompt injection attempt detected and blocked. System prompt integrity verified. No data exposure.',
    timestamp: new Date(Date.now() - 1000 * 60 * 72).toISOString(),
    model_version: 'llm-v3.2.1',
  },
  {
    id: 'aud-004',
    event_type: 'pii_redacted',
    risk_type: 'privacy_leak',
    actor: 'compliance_officer',
    outcome:
      'PII pattern redacted from model output. User notified of partial response. Compliance report filed.',
    timestamp: new Date(Date.now() - 1000 * 60 * 125).toISOString(),
    model_version: 'llm-v3.2.0',
  },
  {
    id: 'aud-005',
    event_type: 'fact_check_queued',
    risk_type: 'hallucination',
    actor: 'ai_ethics_reviewer',
    outcome:
      'Hallucination flagged: non-existent source cited as fact. Disclosure notice added. Fact-checking enhancement queued.',
    timestamp: new Date(Date.now() - 1000 * 60 * 200).toISOString(),
    model_version: 'llm-v3.1.8',
  },
];

async function fetchPolicies() {
  await new Promise((r) => setTimeout(r, 280));
  return BASE_POLICIES;
}

async function fetchAuditHistory() {
  await new Promise((r) => setTimeout(r, 380));
  return BASE_AUDIT_HISTORY;
}

/* --------------------------------------------------------------------------
   Utility helpers
   -------------------------------------------------------------------------- */
function formatRelativeTime(isoString) {
  const diffMs = Date.now() - new Date(isoString).getTime();
  const diffMin = Math.round(diffMs / 60000);
  if (diffMin < 1) return 'just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffH = Math.round(diffMin / 60);
  if (diffH < 24) return `${diffH}h ago`;
  return `${Math.round(diffH / 24)}d ago`;
}

function maxRiskCount(breakdown) {
  return breakdown.reduce((m, r) => Math.max(m, r.count), 1);
}

/* --------------------------------------------------------------------------
   Sub-components
   -------------------------------------------------------------------------- */

const POLICY_TYPE_OPTIONS = [
  { value: 'all', label: 'All' },
  { value: 'decision_constraint', label: 'Decision Constraints' },
  { value: 'adjudication_policy', label: 'Adjudication Policies' },
];

const AUDIT_EVENT_LABELS = {
  output_blocked: 'Output Blocked',
  policy_reviewed: 'Policy Reviewed',
  jailbreak_blocked: 'Jailbreak Blocked',
  pii_redacted: 'PII Redacted',
  fact_check_queued: 'Fact-Check Queued',
};

function GovernancePolicies({ policies, loading }) {
  const [typeFilter, setTypeFilter] = useState('all');

  const filtered = useMemo(
    () =>
      typeFilter === 'all' ? policies : policies.filter((p) => p.type === typeFilter),
    [policies, typeFilter]
  );

  const badgeClass = (type) => {
    if (type === 'decision_constraint') return 'constraint';
    if (type === 'adjudication_policy') return 'adjudication';
    return 'disclosure';
  };

  const typeLabel = (type) => {
    if (type === 'decision_constraint') return 'Decision Constraint';
    if (type === 'adjudication_policy') return 'Adjudication Policy';
    return type.replace(/_/g, ' ');
  };

  return (
    <>
      <div className="ag-filter-bar" role="group" aria-label="Filter policies by type">
        {POLICY_TYPE_OPTIONS.map(({ value, label }) => (
          <button
            key={value}
            className={`ag-filter-btn${typeFilter === value ? ' ag-filter-btn--active' : ''}`}
            onClick={() => setTypeFilter(value)}
            aria-pressed={typeFilter === value}
          >
            {label}
          </button>
        ))}
      </div>

      {loading && (
        <div className="ag-empty" aria-live="polite" aria-label="Loading policies">
          <span className="ag-spinner" aria-hidden="true" /> Loading policies…
        </div>
      )}

      {!loading && filtered.length === 0 && (
        <p className="ag-empty">No policies match the current filter.</p>
      )}

      {!loading && filtered.length > 0 && (
        <ul className="ag-policy-list" role="list" aria-label="Governance policies">
          {filtered.map((policy) => (
            <li
              key={policy.id}
              className="ag-policy-item"
              role="listitem"
              aria-label={policy.title}
            >
              <div className="ag-policy-item__header">
                <span className={`ag-badge ag-badge--${badgeClass(policy.type)}`}>
                  {typeLabel(policy.type)}
                </span>
                <span
                  className={`ag-badge ag-badge--${policy.status === 'active' ? 'low' : 'medium'}`}
                  aria-label={`Status: ${policy.status === 'active' ? 'Active' : 'Under Review'}`}
                >
                  {policy.status === 'active' ? 'Active' : 'Under Review'}
                </span>
              </div>
              <h3 className="ag-policy-item__title">{policy.title}</h3>
              <p className="ag-policy-item__description">{policy.description}</p>
              <div className="ag-policy-item__meta">
                <span>
                  <strong>Enforcement:</strong> {policy.enforcement.replace(/_/g, ' ')}
                </span>
                <span>
                  <strong>Review interval:</strong> every {policy.review_interval_days} days
                </span>
              </div>
              <div className="ag-policy-item__applies" aria-label="Applies to risk types">
                {policy.applies_to.map((rt) => (
                  <span key={rt} className="ag-action-tag">
                    {RISK_LABELS[rt] || rt}
                  </span>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}

function AuditHistory({ history, loading }) {
  const [riskFilter, setRiskFilter] = useState('all');
  const [sortOrder, setSortOrder] = useState('newest');

  const sorted = useMemo(() => {
    const filtered =
      riskFilter === 'all' ? history : history.filter((h) => h.risk_type === riskFilter);
    return [...filtered].sort((a, b) => {
      const diff = new Date(b.timestamp) - new Date(a.timestamp);
      return sortOrder === 'newest' ? diff : -diff;
    });
  }, [history, riskFilter, sortOrder]);

  if (loading) {
    return (
      <div className="ag-empty" aria-live="polite" aria-label="Loading audit history">
        <span className="ag-spinner" aria-hidden="true" /> Loading audit history…
      </div>
    );
  }

  return (
    <>
      <div className="ag-filter-bar" role="group" aria-label="Filter and sort audit history">
        <label className="ag-filter-bar__label" htmlFor="audit-risk-filter">
          Risk type:
        </label>
        <select
          id="audit-risk-filter"
          className="ag-filter-select"
          value={riskFilter}
          onChange={(e) => setRiskFilter(e.target.value)}
          aria-label="Filter audit history by risk type"
        >
          <option value="all">All risk types</option>
          {Object.entries(RISK_LABELS).map(([key, label]) => (
            <option key={key} value={key}>
              {label}
            </option>
          ))}
        </select>

        <label className="ag-filter-bar__label" htmlFor="audit-sort-order">
          Sort:
        </label>
        <select
          id="audit-sort-order"
          className="ag-filter-select"
          value={sortOrder}
          onChange={(e) => setSortOrder(e.target.value)}
          aria-label="Sort audit history by time"
        >
          <option value="newest">Newest first</option>
          <option value="oldest">Oldest first</option>
        </select>
      </div>

      {sorted.length === 0 && (
        <p className="ag-empty">No audit records match the current filter.</p>
      )}

      {sorted.length > 0 && (
        <ol className="ag-timeline" aria-label="Audit history log">
          {sorted.map((entry) => {
            const severity = RISK_SEVERITY[entry.risk_type] || 'info';
            return (
              <li
                key={entry.id}
                className="ag-timeline-item"
                style={{ '--ag-dot-color': RISK_ACCENT_COLORS[severity] }}
                aria-label={`Audit: ${AUDIT_EVENT_LABELS[entry.event_type] || entry.event_type}`}
              >
                <header className="ag-timeline-item__header">
                  <span className="ag-timeline-item__risk">
                    <span
                      className={`ag-badge ag-badge--${severity}`}
                      role="img"
                      aria-label={`Severity: ${severity}`}
                    >
                      {severity}
                    </span>{' '}
                    {AUDIT_EVENT_LABELS[entry.event_type] || entry.event_type}
                  </span>
                  <time
                    className="ag-timeline-item__time"
                    dateTime={entry.timestamp}
                    title={new Date(entry.timestamp).toLocaleString()}
                  >
                    {formatRelativeTime(entry.timestamp)}
                  </time>
                </header>
                <p className="ag-timeline-item__summary">{entry.outcome}</p>
                <p className="ag-audit-item__actor">
                  <strong>Handled by:</strong> {entry.actor.replace(/_/g, ' ')}
                  {entry.model_version && (
                    <>
                      {' · '}
                      <strong>Model:</strong> {entry.model_version}
                    </>
                  )}
                </p>
              </li>
            );
          })}
        </ol>
      )}
    </>
  );
}

function MetricCard({ label, value, delta, deltaDir, accentColor }) {
  return (
    <article
      className="ag-metric-card"
      aria-label={`${label}: ${value}`}
      style={{ '--ag-card-accent': accentColor }}
    >
      <p className="ag-metric-card__label">{label}</p>
      <p className="ag-metric-card__value" aria-live="polite">
        {value}
      </p>
      {delta && (
        <p
          className={`ag-metric-card__delta ag-metric-card__delta--${deltaDir}`}
          aria-label={`Change: ${delta}`}
        >
          {deltaDir === 'up' ? '▲' : '▼'} {delta}
        </p>
      )}
    </article>
  );
}

function RiskBreakdown({ breakdown, loading }) {
  const maxCount = maxRiskCount(breakdown);
  return (
    <section
      className="ag-risk-breakdown"
      aria-label="Risk type breakdown"
      aria-busy={loading}
    >
      {breakdown.map((row) => (
        <div
          key={row.key}
          className="ag-risk-row"
          role="group"
          aria-label={`${row.label}: ${row.count} incidents`}
        >
          <span className="ag-risk-row__label">
            <span
              className={`ag-badge ag-badge--${row.severity}`}
              aria-hidden="true"
            >
              {row.severity}
            </span>{' '}
            {row.label}
          </span>
          <div className="ag-risk-row__track" role="presentation">
            <div
              className="ag-risk-row__fill"
              style={{
                width: `${Math.round((row.count / maxCount) * 100)}%`,
                backgroundColor:
                  RISK_ACCENT_COLORS[row.severity] || 'var(--ag-accent)',
              }}
            />
          </div>
          <span className="ag-risk-row__count" aria-hidden="true">
            {row.count}
          </span>
        </div>
      ))}
      {breakdown.length === 0 && !loading && (
        <p className="ag-empty">No risk data available.</p>
      )}
    </section>
  );
}

function IncidentTimeline({ incidents, loading }) {
  if (loading) {
    return (
      <div className="ag-empty" aria-live="polite" aria-label="Loading incidents">
        <span className="ag-spinner" aria-hidden="true" /> Loading incidents…
      </div>
    );
  }

  if (incidents.length === 0) {
    return (
      <div className="ag-empty" aria-live="polite">
        <p className="ag-empty__icon" aria-hidden="true">✅</p>
        <p>No incidents in the current period.</p>
      </div>
    );
  }

  return (
    <ol className="ag-timeline" aria-label="Incident timeline">
      {incidents.map((inc) => {
        const severity = RISK_SEVERITY[inc.risk_type] || 'info';
        return (
          <li
            key={inc.id}
            className="ag-timeline-item"
            style={{ '--ag-dot-color': RISK_ACCENT_COLORS[severity] }}
            aria-label={`Incident ${inc.id}: ${RISK_LABELS[inc.risk_type] || inc.risk_type}`}
          >
            <header className="ag-timeline-item__header">
              <span className="ag-timeline-item__risk">
                <span
                  className={`ag-badge ag-badge--${severity}`}
                  role="img"
                  aria-label={`Severity: ${severity}`}
                >
                  {severity}
                </span>{' '}
                {RISK_LABELS[inc.risk_type] || inc.risk_type}
              </span>
              <time
                className="ag-timeline-item__time"
                dateTime={inc.timestamp}
                title={new Date(inc.timestamp).toLocaleString()}
              >
                {formatRelativeTime(inc.timestamp)}
              </time>
            </header>
            <p className="ag-timeline-item__summary">{inc.summary}</p>
            {inc.actions_required && inc.actions_required.length > 0 && (
              <ul
                className="ag-timeline-item__actions"
                aria-label="Required actions"
                role="list"
              >
                {inc.actions_required.map((action) => (
                  <li key={action} className="ag-action-tag" role="listitem">
                    {action.replace(/_/g, ' ')}
                  </li>
                ))}
              </ul>
            )}
          </li>
        );
      })}
    </ol>
  );
}

/* --------------------------------------------------------------------------
   Main dashboard component
   -------------------------------------------------------------------------- */
export const AIGovernanceDashboard = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [navOpen, setNavOpen] = useState(false);
  const [metrics, setMetrics] = useState(null);
  const [breakdown, setBreakdown] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [policies, setPolicies] = useState([]);
  const [auditHistory, setAuditHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [refreshSeed, setRefreshSeed] = useState(0);
  const [incidentSeverityFilter, setIncidentSeverityFilter] = useState('all');
  const [incidentSortOrder, setIncidentSortOrder] = useState('newest');

  const mainRef = useRef(null);
  const liveRegionRef = useRef(null);

  /** Announce message to screen-reader live region */
  const announce = useCallback((msg) => {
    if (liveRegionRef.current) {
      liveRegionRef.current.textContent = '';
      // Timeout forces re-announcement for repeated messages
      setTimeout(() => {
        if (liveRegionRef.current) liveRegionRef.current.textContent = msg;
      }, 50);
    }
  }, []);

  /** Fetch all data from (mock) backend */
  const loadData = useCallback(
    async (seed) => {
      setLoading(true);
      announce('Refreshing dashboard data…');
      try {
        const [m, b, i, p, a] = await Promise.all([
          fetchMetrics(seed),
          fetchRiskBreakdown(seed),
          fetchIncidents(),
          fetchPolicies(),
          fetchAuditHistory(),
        ]);
        setMetrics(m);
        setBreakdown(b);
        setIncidents(i);
        setPolicies(p);
        setAuditHistory(a);
        setLastUpdated(new Date());
        announce('Dashboard updated.');
      } catch {
        announce('Error loading dashboard data.');
      } finally {
        setLoading(false);
      }
    },
    [announce]
  );

  // Initial load
  useEffect(() => {
    loadData(0);
  }, [loadData]);

  // Simulated real-time polling every 30 seconds
  useEffect(() => {
    const id = setInterval(() => {
      setRefreshSeed((s) => {
        const next = s + 1;
        loadData(next);
        return next;
      });
    }, 30000);
    return () => clearInterval(id);
  }, [loadData]);

  const handleManualRefresh = () => {
    const next = refreshSeed + 1;
    setRefreshSeed(next);
    loadData(next);
  };

  // Close mobile nav when clicking outside
  useEffect(() => {
    if (!navOpen) return;
    const handler = (e) => {
      if (!e.target.closest('.ag-nav')) setNavOpen(false);
    };
    document.addEventListener('click', handler);
    return () => document.removeEventListener('click', handler);
  }, [navOpen]);

  // Smooth-scroll helper for anchor nav
  const scrollToSection = (e, id) => {
    e.preventDefault();
    setNavOpen(false);
    const el = document.getElementById(id);
    if (el) el.focus({ preventScroll: false });
    el?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const filteredSortedIncidents = useMemo(() => {
    const filtered =
      incidentSeverityFilter === 'all'
        ? incidents
        : incidents.filter(
            (inc) => RISK_SEVERITY[inc.risk_type] === incidentSeverityFilter
          );
    return [...filtered].sort((a, b) => {
      const diff = new Date(b.timestamp) - new Date(a.timestamp);
      return incidentSortOrder === 'newest' ? diff : -diff;
    });
  }, [incidents, incidentSeverityFilter, incidentSortOrder]);

  const metricCards = metrics
    ? [
        {
          label: 'Total Incidents',
          value: metrics.total_incidents,
          delta: '+3 from yesterday',
          deltaDir: 'up',
          accentColor: 'var(--ag-risk-info)',
        },
        {
          label: 'Critical Open',
          value: metrics.critical_open,
          delta: '-1 from yesterday',
          deltaDir: 'down',
          accentColor: 'var(--ag-risk-critical)',
        },
        {
          label: 'Pending Review',
          value: metrics.pending_review,
          accentColor: 'var(--ag-risk-high)',
        },
        {
          label: 'Resolved Today',
          value: metrics.resolved_today,
          delta: '+4 from yesterday',
          deltaDir: 'up',
          accentColor: 'var(--ag-risk-low)',
        },
        {
          label: 'Blocked Outputs',
          value: metrics.blocked_outputs,
          accentColor: 'var(--ag-risk-medium)',
        },
        {
          label: 'Avg. Response (min)',
          value: metrics.avg_response_min,
          accentColor: 'var(--ag-accent)',
        },
      ]
    : [];

  return (
    <div
      className={`ag-dashboard ${darkMode ? 'dark' : 'light'}`}
      data-testid="ai-governance-dashboard"
    >
      {/* Screen-reader live region */}
      <div
        ref={liveRegionRef}
        role="status"
        aria-live="polite"
        aria-atomic="true"
        style={{ position: 'absolute', width: 1, height: 1, overflow: 'hidden', clip: 'rect(0,0,0,0)' }}
      />

      {/* Skip to main content — keyboard accessibility */}
      <a className="ag-skip-link" href="#ag-main" onClick={(e) => scrollToSection(e, 'ag-main')}>
        Skip to main content
      </a>

      {/* ---- Navigation ---- */}
      <nav
        className="ag-nav"
        role="navigation"
        aria-label="AI Governance Monitoring navigation"
      >
        <div className="ag-nav__inner">
          <a
            className="ag-nav__brand"
            href="#ag-main"
            onClick={(e) => scrollToSection(e, 'ag-main')}
            aria-label="AI Governance Dashboard home"
          >
            <span className="ag-nav__brand-icon" aria-hidden="true">⚛️</span>
            <span>AI Governance</span>
          </a>

          {/* Desktop links */}
          <ul
            id="ag-nav-links"
            className={`ag-nav__links${navOpen ? ' ag-nav__links--open' : ''}`}
            role="list"
          >
            {[
              { href: 'ag-metrics', label: 'Metrics' },
              { href: 'ag-risk-breakdown', label: 'Risk Breakdown' },
              { href: 'ag-timeline', label: 'Timeline' },
              { href: 'ag-policies', label: 'Policies' },
              { href: 'ag-audit', label: 'Audit' },
            ].map(({ href, label }) => (
              <li key={href} role="listitem">
                <a
                  href={`#${href}`}
                  onClick={(e) => scrollToSection(e, href)}
                  aria-current={undefined}
                >
                  {label}
                </a>
              </li>
            ))}
          </ul>

          <div className="ag-nav__controls">
            {/* Dark / light mode toggle */}
            <button
              className="ag-theme-toggle"
              onClick={() => setDarkMode((d) => !d)}
              aria-pressed={darkMode}
              aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
              title={darkMode ? 'Light mode' : 'Dark mode'}
            >
              {darkMode ? '☀️' : '🌙'}
            </button>

            {/* Hamburger menu (mobile) */}
            <button
              className="ag-nav__hamburger"
              aria-expanded={navOpen}
              aria-controls="ag-nav-links"
              aria-label={navOpen ? 'Close navigation menu' : 'Open navigation menu'}
              onClick={() => setNavOpen((o) => !o)}
            >
              <span className="ag-nav__hamburger-bar" aria-hidden="true" />
              <span className="ag-nav__hamburger-bar" aria-hidden="true" />
              <span className="ag-nav__hamburger-bar" aria-hidden="true" />
            </button>
          </div>
        </div>
      </nav>

      {/* ---- Main content ---- */}
      <main
        id="ag-main"
        className="ag-main"
        ref={mainRef}
        tabIndex={-1}
        aria-label="AI Governance Monitoring Dashboard"
      >
        {/* Hero status bar */}
        <div
          className="ag-status-bar"
          role="region"
          aria-label="System status overview"
        >
          <div>
            <h1 className="ag-status-bar__title">
              Quantum-Assisted AI Governance Monitoring
            </h1>
            <p className="ag-status-bar__subtitle">
              Real-time safety intercept &amp; compliance audit — powered by
              quantum-enhanced pattern detection
            </p>
          </div>
          <span className="ag-status-bar__badge ag-status-bar__badge--live" aria-label="System live">
            LIVE
          </span>
        </div>

        {/* ---- Metrics section ---- */}
        <section
          id="ag-metrics"
          className="ag-section"
          aria-labelledby="metrics-heading"
        >
          <header className="ag-section__header">
            <h2 className="ag-section__title" id="metrics-heading">
              Key Metrics
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
              {lastUpdated && (
                <p className="ag-last-updated" aria-live="polite">
                  Last updated:{' '}
                  <time dateTime={lastUpdated.toISOString()}>
                    {lastUpdated.toLocaleTimeString()}
                  </time>
                </p>
              )}
              <button
                className="ag-btn ag-btn--outline"
                onClick={handleManualRefresh}
                disabled={loading}
                aria-label="Refresh dashboard data"
              >
                {loading ? (
                  <>
                    <span className="ag-spinner" aria-hidden="true" />
                    Refreshing…
                  </>
                ) : (
                  <>↻ Refresh</>
                )}
              </button>
            </div>
          </header>

          {metrics ? (
            <div
              className="ag-metrics-grid"
              role="list"
              aria-label="Governance metrics"
            >
              {metricCards.map((card) => (
                <div key={card.label} role="listitem">
                  <MetricCard {...card} />
                </div>
              ))}
            </div>
          ) : (
            <div className="ag-empty" aria-live="polite">
              <span className="ag-spinner" aria-hidden="true" /> Loading metrics…
            </div>
          )}
        </section>

        {/* ---- Risk breakdown section ---- */}
        <section
          id="ag-risk-breakdown"
          className="ag-section"
          aria-labelledby="breakdown-heading"
        >
          <header className="ag-section__header">
            <h2 className="ag-section__title" id="breakdown-heading">
              Risk Type Breakdown
            </h2>
          </header>
          <RiskBreakdown breakdown={breakdown} loading={loading && breakdown.length === 0} />
        </section>

        {/* ---- Incident timeline section ---- */}
        <section
          id="ag-timeline"
          className="ag-section"
          aria-labelledby="timeline-heading"
        >
          <header className="ag-section__header">
            <h2 className="ag-section__title" id="timeline-heading">
              Recent Incidents
            </h2>
            <span className="ag-badge ag-badge--info" aria-label={`${incidents.length} incidents`}>
              {incidents.length} incidents
            </span>
          </header>
          <div className="ag-filter-bar" role="group" aria-label="Filter and sort incidents">
            <label className="ag-filter-bar__label" htmlFor="incident-severity-filter">
              Severity:
            </label>
            <select
              id="incident-severity-filter"
              className="ag-filter-select"
              value={incidentSeverityFilter}
              onChange={(e) => setIncidentSeverityFilter(e.target.value)}
              aria-label="Filter incidents by severity"
            >
              <option value="all">All</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
            <label className="ag-filter-bar__label" htmlFor="incident-sort-order">
              Sort:
            </label>
            <select
              id="incident-sort-order"
              className="ag-filter-select"
              value={incidentSortOrder}
              onChange={(e) => setIncidentSortOrder(e.target.value)}
              aria-label="Sort incidents by time"
            >
              <option value="newest">Newest first</option>
              <option value="oldest">Oldest first</option>
            </select>
          </div>
          <IncidentTimeline
            incidents={filteredSortedIncidents}
            loading={loading && incidents.length === 0}
          />
        </section>

        {/* ---- Governance policies section ---- */}
        <section
          id="ag-policies"
          className="ag-section"
          aria-labelledby="policies-heading"
          role="region"
        >
          <header className="ag-section__header">
            <h2 className="ag-section__title" id="policies-heading">
              Governance Policies
            </h2>
            <span className="ag-badge ag-badge--info" aria-label={`${policies.length} policies`}>
              {policies.length} policies
            </span>
          </header>
          <GovernancePolicies
            policies={policies}
            loading={loading && policies.length === 0}
          />
        </section>

        {/* ---- Audit history section ---- */}
        <section
          id="ag-audit"
          className="ag-section"
          aria-labelledby="audit-heading"
          role="region"
        >
          <header className="ag-section__header">
            <h2 className="ag-section__title" id="audit-heading">
              Audit History
            </h2>
            <span
              className="ag-badge ag-badge--info"
              aria-label={`${auditHistory.length} audit records`}
            >
              {auditHistory.length} records
            </span>
          </header>
          <AuditHistory
            history={auditHistory}
            loading={loading && auditHistory.length === 0}
          />
        </section>
      </main>
    </div>
  );
};

export default AIGovernanceDashboard;
