# Lumina AI — AI Hiring Challenge Platform

A production-ready marketing website for the Lumina AI hackathon/challenge platform — the premier AI hiring competition.

## Tech Stack

- **Framework:** Next.js 16 (App Router), React 19, TypeScript
- **Styling:** Tailwind CSS v4 (CSS-first config via `@theme` in `globals.css`)
- **Animation:** Framer Motion
- **Icons:** lucide-react
- **Fonts:** Inter + JetBrains Mono (Google Fonts, free)
- **Hosting target:** Vercel free tier

## Getting Started

### Prerequisites

- Node.js 18+ installed
- npm 9+

### Run locally

```bash
# Navigate to the project directory
cd lumina-ai

# Install dependencies
npm install

# Start the development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for production

```bash
npm run build
npm start
```

## Project Structure

```
lumina-ai/
├── app/
│   ├── layout.tsx           # Root layout with font loading + SEO metadata
│   ├── page.tsx             # Landing page (composes all sections)
│   ├── globals.css          # Design system tokens (@theme) + global styles
│   ├── dashboard/
│   │   └── page.tsx         # "Coming Soon" dashboard placeholder
│   └── hiring-challenge/
│       └── page.tsx         # "Coming Soon" hiring challenge placeholder
├── components/
│   ├── Header.tsx           # Sticky nav with mobile hamburger drawer
│   ├── Hero.tsx             # Hero section with decorative inline SVG
│   ├── MissionSection.tsx   # Mission + requirement rows with accent bars
│   ├── ChallengeCard.tsx    # Reusable expand/collapse track card
│   ├── ChallengeSection.tsx # Challenge section (renders both track cards)
│   ├── PrizePoolSection.tsx # Prize pool stats with tier breakdown
│   ├── JourneySection.tsx   # Horizontal/vertical journey stepper
│   ├── TimelineSection.tsx  # Vertical timeline with key dates
│   ├── FAQSection.tsx       # Accordion FAQ with Framer Motion
│   └── Footer.tsx           # Footer with social links + nav recap
├── data/
│   └── content.ts           # ← Edit all page copy here (typed config)
└── public/                  # Static assets
```

## Editing Content

**All page copy lives in `data/content.ts`.** You can safely edit:

- `heroContent` — Hero headline, subheadline, audience tags
- `missionContent` — Mission heading, body, requirement rows
- `tracks` — Both track titles, overviews, requirements, submission checklists, prizes
- `prizePoolContent` — Prize amounts and tier breakdowns
- `journeySteps` — Journey step titles, descriptions, icons
- `timelineEvents` — Key dates and descriptions
- `faqItems` — FAQ questions and answers
- `navLinks` — Header and footer navigation

No code changes required — just edit the data file and the site updates automatically.

## Design System

The design system is defined in `app/globals.css` under `@theme`:

| Token | Value |
|-------|-------|
| `--color-primary` | `#34D399` (Emerald) |
| `--color-secondary` | `#60A5FA` (Blue) |
| `--color-background` | `#030303` (Near-black) |
| `--color-surface` | `#18181B` (Dark grey) |
| `--color-border` | `#27272A` |

## Deploying to Vercel (Free)

1. Push this project to a GitHub repository.
2. Go to [vercel.com](https://vercel.com) and sign in with GitHub.
3. Click **"Add New Project"** → import your repository.
4. Vercel auto-detects Next.js — click **Deploy**.
5. Your site is live on a free `.vercel.app` domain instantly.

No environment variables or backend configuration required for v1.

## Accessibility

- WCAG AA contrast ratios maintained throughout
- All interactive elements keyboard-navigable
- Semantic HTML (`<nav>`, `<section>`, `<main>`, proper heading hierarchy)
- `aria-expanded`, `aria-controls`, `aria-label` on all interactive components
- Visible focus rings using primary color

## License

MIT — built for the Lumina AI Challenge.
