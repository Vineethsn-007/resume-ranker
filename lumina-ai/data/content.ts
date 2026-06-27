// ─────────────────────────────────────────────────────────────────────────────
// Lumina AI — Submission Content Config
// ─────────────────────────────────────────────────────────────────────────────

export interface MethodologyRow {
  label: string;
  weight: string;
  description: string;
}

// ─── HERO ────────────────────────────────────────────────────────────────────

export const heroContent = {
  eyebrowTrack: "Redrob Intelligent Candidate Ranking Challenge",
  eyebrowHighlight: "Stage 4 Submission",
  audienceTags: [
    "CPU-Optimized",
    "Evidence-Based",
    "Semantic NLP",
    "Zero External APIs",
  ],
  headline: "Intelligent Candidate Discovery by Team Lumina AI",
  subheadline:
    "Our submission avoids the 'keyword-stuffer trap' by scoring candidates on genuine evidence of production experience. We prioritize role fit, technical depth, and career trajectory over simple keyword counts.",
  body: "This sandbox UI presents the top candidates ranked by our 5-component scoring pipeline from the 100,000 candidate dataset. Explore our methodology and see the live ranking results below.",
};

// ─── METHODOLOGY ──────────────────────────────────────────────────────────────

export const methodologyContent = {
  heading: "The Lumina AI Scoring Pipeline",
  body: "Our system evaluates candidates using a weighted 5-component architecture. Instead of relying on raw presence of keywords, we parse career history and behavioral signals to determine true capability and availability.",
  rows: [
    {
      label: "Role Fit & Title Gating",
      weight: "35%",
      description:
        "The primary gate. We use a tiered title classification system to ensure candidates with unrelated roles (e.g., HR, Marketing) are heavily penalized, regardless of how many AI skills they list.",
    },
    {
      label: "Technical Depth",
      weight: "30%",
      description:
        "Skills are scored based on evidence (duration, endorsements, and career history corroboration). We specifically detect and penalize honeypot patterns (e.g., 'expert' proficiency with 0 months duration).",
    },
    {
      label: "Career Substance NLP",
      weight: "20%",
      description:
        "We parse career descriptions for production signals (e.g., shipping recommendation systems or vector databases). This catches 'hidden gems' who don't list specific tools but have built relevant architecture.",
    },
    {
      label: "Behavioral Multiplier",
      weight: "10%",
      description:
        "A 0.80x to 1.0x multiplier on the base score. Inactive candidates or those with low recruiter response rates are meaningfully penalized, prioritizing talent that is actually available.",
    },
    {
      label: "Education",
      weight: "5%",
      description:
        "A minor signal based on field relevance, degree level, and institution tier, serving as a tie-breaker for otherwise identical candidates.",
    },
  ] satisfies MethodologyRow[],
  noteArchitecture: "Compute Profile: < 5.5 mins on CPU for 100K candidates",
  noteDataset: "All scores generated without any network/API calls",
};

// ─── NAV LINKS ───────────────────────────────────────────────────────────────

export const navLinks = [
  { label: "Overview", href: "#overview" },
  { label: "Methodology", href: "#methodology" },
  { label: "Sandbox Results", href: "#sandbox" },
];
