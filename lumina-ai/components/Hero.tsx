"use client";

import { motion, type Variants } from "framer-motion";
import { heroContent } from "@/data/content";
import { ArrowRight, Sparkles } from "lucide-react";
import Link from "next/link";

// Decorative geometric SVG — inline, zero external deps
function HeroDecorativeSVG() {
  return (
    <svg
      viewBox="0 0 600 500"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="w-full h-full"
      aria-hidden="true"
      role="presentation"
    >
      <defs>
        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#34D399" stopOpacity="0.6" />
          <stop offset="100%" stopColor="#60A5FA" stopOpacity="0.1" />
        </linearGradient>
        <linearGradient id="grad2" x1="0%" y1="100%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#60A5FA" stopOpacity="0.5" />
          <stop offset="100%" stopColor="#34D399" stopOpacity="0.05" />
        </linearGradient>
        <linearGradient id="grad3" x1="50%" y1="0%" x2="50%" y2="100%">
          <stop offset="0%" stopColor="#34D399" stopOpacity="0.4" />
          <stop offset="100%" stopColor="#60A5FA" stopOpacity="0.2" />
        </linearGradient>
        <linearGradient id="grad4" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#34D399" stopOpacity="0.15" />
          <stop offset="100%" stopColor="#60A5FA" stopOpacity="0.05" />
        </linearGradient>
        <filter id="blur1">
          <feGaussianBlur stdDeviation="8" />
        </filter>
        <filter id="blur2">
          <feGaussianBlur stdDeviation="3" />
        </filter>
      </defs>

      {/* Large background shard */}
      <polygon
        points="80,40 380,10 460,200 300,480 20,420"
        fill="url(#grad4)"
        opacity="0.5"
      />

      {/* Main angular shard — bright */}
      <polygon
        points="120,80 320,20 400,160 260,300 60,280"
        fill="url(#grad1)"
        opacity="0.25"
        filter="url(#blur2)"
      />

      {/* Secondary shard — blue dominant */}
      <polygon
        points="280,60 520,120 500,280 340,340 200,200"
        fill="url(#grad2)"
        opacity="0.2"
        filter="url(#blur2)"
      />

      {/* Thin accent lines */}
      <line x1="60" y1="250" x2="480" y2="80" stroke="#34D399" strokeWidth="0.5" opacity="0.3" />
      <line x1="100" y1="350" x2="520" y2="180" stroke="#60A5FA" strokeWidth="0.5" opacity="0.25" />
      <line x1="200" y1="450" x2="560" y2="100" stroke="#34D399" strokeWidth="0.3" opacity="0.15" />

      {/* Glowing core shard */}
      <polygon
        points="180,120 340,60 400,200 300,300 140,260"
        fill="url(#grad3)"
        opacity="0.35"
        filter="url(#blur1)"
      />

      {/* Small accent diamond top-right */}
      <polygon
        points="460,40 500,80 460,120 420,80"
        fill="#34D399"
        opacity="0.2"
      />
      <polygon
        points="460,40 500,80 460,120 420,80"
        fill="none"
        stroke="#34D399"
        strokeWidth="0.8"
        opacity="0.4"
      />

      {/* Small accent diamond bottom-left */}
      <polygon
        points="60,380 100,360 130,400 90,420"
        fill="#60A5FA"
        opacity="0.15"
      />
      <polygon
        points="60,380 100,360 130,400 90,420"
        fill="none"
        stroke="#60A5FA"
        strokeWidth="0.8"
        opacity="0.3"
      />

      {/* Dot grid pattern */}
      {[0,1,2,3,4].map((row) =>
        [0,1,2,3,4,5].map((col) => (
          <circle
            key={`${row}-${col}`}
            cx={300 + col * 40}
            cy={160 + row * 40}
            r="1"
            fill="#34D399"
            opacity={0.12 - col * 0.015}
          />
        ))
      )}

      {/* Outer ring accent */}
      <circle cx="380" cy="200" r="120" stroke="#34D399" strokeWidth="0.5" opacity="0.1" fill="none" />
      <circle cx="380" cy="200" r="80" stroke="#60A5FA" strokeWidth="0.5" opacity="0.08" fill="none" />
    </svg>
  );
}

const containerVariants: Variants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
};

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.25, 0, 0, 1] as const } },
};

const chipVariants: Variants = {
  hidden: { opacity: 0, scale: 0.85 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.35, ease: [0.25, 0, 0, 1] as const } },
};

export default function Hero() {
  return (
    <section
      id="overview"
      className="relative min-h-screen flex items-center overflow-hidden bg-background hero-bg pt-16"
    >
      {/* Grid overlay */}
      <div className="absolute inset-0 grid-overlay opacity-50" />

      {/* Ambient glow blobs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-secondary/5 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32 w-full">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Text Column */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="flex flex-col gap-8"
          >
            {/* Eyebrow dual-pill */}
            <motion.div variants={itemVariants} className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-pill bg-surface border border-border font-mono text-xs text-textSecondary uppercase tracking-widest">
                <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                {heroContent.eyebrowTrack}
              </span>
              <span
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-pill font-mono text-xs uppercase tracking-widest text-background font-semibold"
                style={{
                  background: "linear-gradient(135deg, #34D399 0%, #60A5FA 100%)",
                }}
              >
                <Sparkles size={10} />
                {heroContent.eyebrowHighlight}
              </span>
            </motion.div>

            {/* Audience chips */}
            <motion.div variants={containerVariants} className="flex flex-wrap gap-2">
              {heroContent.audienceTags.map((tag, i) => (
                <motion.span
                  key={tag}
                  variants={chipVariants}
                  transition={{ delay: 0.3 + i * 0.07 }}
                  className="px-3 py-1 rounded-pill bg-surface/80 border border-border font-mono text-xs text-textSecondary uppercase tracking-wide hover:border-primary/40 hover:text-primary transition-all duration-200"
                >
                  {tag}
                </motion.span>
              ))}
            </motion.div>

            {/* H1 Headline */}
            <motion.h1
              variants={itemVariants}
              className="font-display font-medium text-textPrimary leading-[1.04] tracking-[-0.02em]"
              style={{ fontSize: "clamp(2.2rem, 4.5vw + 0.5rem, 4rem)" }}
            >
              {heroContent.headline}
            </motion.h1>

            {/* Subheadline */}
            <motion.p
              variants={itemVariants}
              className="font-body text-base leading-relaxed text-textSecondary max-w-lg"
            >
              {heroContent.subheadline}
            </motion.p>

            {/* Body */}
            <motion.p
              variants={itemVariants}
              className="font-body text-base leading-relaxed text-textSecondary/80 max-w-lg"
            >
              {heroContent.body}
            </motion.p>

            {/* CTAs */}
            <motion.div variants={itemVariants} className="flex flex-wrap gap-3 pt-2">
              <Link
                href="#methodology"
                onClick={(e) => {
                  e.preventDefault();
                  document.getElementById("methodology")?.scrollIntoView({ behavior: "smooth" });
                }}
                className="group inline-flex items-center gap-2 px-6 py-3 rounded-control text-sm font-display font-medium text-background transition-all duration-200 hover:-translate-y-1 hover:shadow-lg focus-visible:outline-primary"
                style={{ background: "linear-gradient(135deg, #34D399 0%, #60A5FA 100%)" }}
              >
                View Methodology
                <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform duration-200" />
              </Link>
              <Link
                href="#sandbox"
                onClick={(e) => {
                  e.preventDefault();
                  document.getElementById("sandbox")?.scrollIntoView({ behavior: "smooth" });
                }}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-control text-sm font-display font-medium text-textPrimary border border-border hover:border-primary/50 hover:bg-surface transition-all duration-200 hover:-translate-y-1 focus-visible:outline-primary"
              >
                Live Sandbox Results
              </Link>
            </motion.div>

            {/* Stat chips */}
            <motion.div variants={itemVariants} className="flex flex-wrap gap-4 pt-2">
              {[
                { label: "Candidates Ranked", value: "100K" },
                { label: "Execution Time", value: "< 6m" },
                { label: "Compute", value: "CPU Only" },
              ].map((stat) => (
                <div key={stat.label} className="flex items-center gap-2">
                  <span className="font-display font-semibold text-primary text-lg">{stat.value}</span>
                  <span className="font-mono text-xs text-textSecondary uppercase tracking-wider">{stat.label}</span>
                </div>
              ))}
            </motion.div>
          </motion.div>

          {/* Decorative SVG Column */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.2, ease: "easeOut" }}
            className="relative hidden lg:flex items-center justify-center"
          >
            <div className="relative w-full max-w-lg aspect-[6/5]">
              {/* Glow behind SVG */}
              <div className="absolute inset-0 bg-primary/5 rounded-full blur-3xl scale-110" />
              <HeroDecorativeSVG />
            </div>
          </motion.div>
        </div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5, duration: 0.5 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
      >
        <span className="font-mono text-xs text-textSecondary uppercase tracking-widest">Scroll</span>
        <motion.div
          animate={{ y: [0, 6, 0] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
          className="w-0.5 h-8 bg-gradient-to-b from-primary/60 to-transparent rounded-full"
        />
      </motion.div>
    </section>
  );
}
