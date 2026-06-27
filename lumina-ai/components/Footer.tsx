"use client";

import Link from "next/link";
import { Zap, Globe, X, ExternalLink, Mail } from "lucide-react";
import { navLinks } from "@/data/content";

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="relative bg-surface border-t border-border overflow-hidden">
      {/* Top gradient accent line */}
      <div
        className="absolute top-0 left-0 right-0 h-px"
        style={{
          background: "linear-gradient(90deg, transparent, #34D399 30%, #60A5FA 70%, transparent)",
        }}
      />

      {/* Ambient glow */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-32 bg-primary/3 blur-3xl pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_auto] gap-12">
          {/* Brand column */}
          <div className="flex flex-col gap-6">
            {/* Wordmark */}
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-control bg-primary/10 border border-primary/30 flex items-center justify-center">
                <Zap className="w-4.5 h-4.5 text-primary" strokeWidth={2.5} />
              </div>
              <div className="flex flex-col">
                <span className="font-display font-semibold text-lg tracking-tight text-textPrimary leading-none">
                  Lumina AI
                </span>
                <span className="font-mono text-[10px] text-textSecondary uppercase tracking-widest">
                  AI Hiring Challenge
                </span>
              </div>
            </div>

            <p className="font-body text-sm leading-relaxed text-textSecondary max-w-xs">
              Building the AI brain for modern hiring — one breakthrough at a time. Join us to shape the future of talent acquisition.
            </p>

            {/* Social icons */}
            <div className="flex items-center gap-3">
              {[
                { icon: X, label: "Twitter / X", href: "#" },
                { icon: Globe, label: "GitHub", href: "#" },
                { icon: ExternalLink, label: "LinkedIn", href: "#" },
                { icon: Mail, label: "Email", href: "mailto:hello@lumina.ai" },
              ].map(({ icon: Icon, label, href }) => (
                <a
                  key={label}
                  href={href}
                  aria-label={label}
                  className="w-9 h-9 rounded-control bg-background border border-border flex items-center justify-center text-textSecondary hover:text-primary hover:border-primary/40 transition-all duration-200 hover:-translate-y-0.5 focus-visible:outline-primary"
                >
                  <Icon size={16} />
                </a>
              ))}
            </div>

            {/* Partner logo placeholders */}
            <div className="flex items-center gap-3 pt-2">
              <span className="font-mono text-[10px] text-textSecondary uppercase tracking-widest">Partners</span>
              {[1, 2, 3].map((n) => (
                <div
                  key={n}
                  className="w-10 h-6 rounded-control bg-background border border-border flex items-center justify-center"
                  aria-label={`Partner ${n} logo`}
                >
                  <div className="w-4 h-2 bg-textSecondary/20 rounded-full" />
                </div>
              ))}
            </div>
          </div>

          {/* Nav links */}
          <div className="flex flex-col gap-4">
            <span className="font-mono text-xs font-semibold uppercase tracking-widest text-textSecondary">
              Navigate
            </span>
            <nav className="flex flex-col gap-2" aria-label="Footer navigation">
              {navLinks.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  onClick={(e) => {
                    e.preventDefault();
                    const id = link.href.replace("#", "");
                    const el = document.getElementById(id);
                    if (el) {
                      el.scrollIntoView({ behavior: "smooth", block: "start" });
                    }
                  }}
                  className="font-body text-sm text-textSecondary hover:text-textPrimary transition-colors duration-200 focus-visible:outline-primary rounded"
                >
                  {link.label}
                </a>
              ))}
            </nav>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-16 pt-8 border-t border-border flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="font-mono text-xs text-textSecondary text-center sm:text-left">
            © {year} Lumina AI. All rights reserved.
          </p>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            <span className="font-mono text-xs text-textSecondary">
              System Online — CPU Compute
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}
