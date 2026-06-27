"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Menu, X, Zap } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { navLinks } from "@/data/content";

export default function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Close menu on resize to desktop
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) setMenuOpen(false);
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault();
    setMenuOpen(false);
    const id = href.replace("#", "");
    const el = document.getElementById(id);
    if (el) {
      const offset = 80;
      const top = el.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top, behavior: "smooth" });
    }
  };

  return (
    <>
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled
            ? "bg-surface/95 backdrop-blur-md border-b border-border shadow-lg"
            : "bg-transparent border-b border-transparent"
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Wordmark */}
            <div className="flex items-center gap-3 flex-shrink-0">
              <div className="w-8 h-8 rounded-control bg-primary/10 border border-primary/30 flex items-center justify-center">
                <Zap className="w-4 h-4 text-primary" strokeWidth={2.5} />
              </div>
              <span className="font-display font-semibold text-lg tracking-tight text-textPrimary">
                Lumina AI
              </span>
              {/* Partner logo placeholder */}
              <div className="hidden sm:flex items-center gap-1.5 ml-2 pl-3 border-l border-border">
                <div className="w-5 h-5 rounded-full bg-secondary/20 border border-secondary/30" />
                <span className="font-mono text-xs text-textSecondary uppercase tracking-wider">
                  Challenge
                </span>
              </div>
            </div>

            {/* Desktop Nav */}
            <nav className="hidden lg:flex items-center gap-1" aria-label="Main navigation">
              {navLinks.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  onClick={(e) => handleNavClick(e, link.href)}
                  className="px-3 py-2 text-sm font-body text-textSecondary hover:text-textPrimary transition-colors duration-200 rounded-control hover:bg-surface focus-visible:outline-primary"
                >
                  {link.label}
                </a>
              ))}
            </nav>

            {/* CTA Buttons */}
            <div className="hidden lg:flex items-center gap-3">
              <a
                href="https://github.com/lumina-ai/submission"
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 text-sm font-display font-medium text-textPrimary border border-border rounded-control hover:border-primary/50 hover:bg-surface transition-all duration-200 hover:-translate-y-0.5 focus-visible:outline-primary"
              >
                View Source
              </a>
              <a
                href="#sandbox"
                onClick={(e) => handleNavClick(e as any, "#sandbox")}
                className="px-4 py-2 text-sm font-display font-medium text-background bg-primary rounded-control hover:bg-primary/90 hover:shadow-lg hover:shadow-primary/20 transition-all duration-200 hover:-translate-y-0.5 focus-visible:outline-primary"
              >
                Run Ranker
              </a>
            </div>

            {/* Mobile menu toggle */}
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="lg:hidden w-10 h-10 flex items-center justify-center rounded-control border border-border text-textSecondary hover:text-textPrimary hover:bg-surface transition-all duration-200 focus-visible:outline-primary"
              aria-label={menuOpen ? "Close menu" : "Open menu"}
              aria-expanded={menuOpen}
            >
              {menuOpen ? <X size={18} /> : <Menu size={18} />}
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Menu Drawer */}
      <AnimatePresence>
        {menuOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
              onClick={() => setMenuOpen(false)}
            />
            {/* Drawer */}
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 30, stiffness: 300 }}
              className="fixed top-0 right-0 bottom-0 z-50 w-72 bg-surface border-l border-border flex flex-col pt-20 pb-8 px-6 lg:hidden"
            >
              <button
                onClick={() => setMenuOpen(false)}
                className="absolute top-4 right-4 w-10 h-10 flex items-center justify-center rounded-control border border-border text-textSecondary hover:text-textPrimary transition-all"
                aria-label="Close menu"
              >
                <X size={18} />
              </button>

              <nav className="flex flex-col gap-1 flex-1" aria-label="Mobile navigation">
                {navLinks.map((link, i) => (
                  <motion.a
                    key={link.href}
                    href={link.href}
                    onClick={(e) => handleNavClick(e, link.href)}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="px-4 py-3 text-base font-body text-textSecondary hover:text-textPrimary hover:bg-background/50 rounded-control transition-all duration-200 focus-visible:outline-primary"
                  >
                    {link.label}
                  </motion.a>
                ))}
              </nav>

              <div className="flex flex-col gap-3 pt-6 border-t border-border">
                <a
                  href="https://github.com/lumina-ai/submission"
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => setMenuOpen(false)}
                  className="px-4 py-2.5 text-sm font-display font-medium text-center text-textPrimary border border-border rounded-control hover:border-primary/50 transition-all duration-200"
                >
                  View Source
                </a>
                <a
                  href="#sandbox"
                  onClick={(e) => handleNavClick(e as any, "#sandbox")}
                  className="px-4 py-2.5 text-sm font-display font-medium text-center text-background bg-primary rounded-control hover:bg-primary/90 transition-all duration-200"
                >
                  Run Ranker
                </a>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
