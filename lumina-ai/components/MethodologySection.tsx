"use client";

import { motion } from "framer-motion";
import { methodologyContent } from "@/data/content";

export default function MethodologySection() {
  return (
    <section id="methodology" className="py-24 bg-zinc-950 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-zinc-800/20 via-zinc-950 to-zinc-950" />
      
      <div className="max-w-7xl mx-auto px-6 lg:px-8 relative z-10">
        <div className="max-w-2xl">
          <motion.h2 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl font-bold tracking-tight text-zinc-100 sm:text-4xl"
          >
            {methodologyContent.heading}
          </motion.h2>
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="mt-6 text-lg leading-8 text-zinc-400"
          >
            {methodologyContent.body}
          </motion.p>
        </div>

        <div className="mt-16 grid gap-8 lg:grid-cols-2">
          <div className="flex flex-col space-y-6">
            {methodologyContent.rows.map((row, index) => (
              <motion.div
                key={row.label}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="group relative flex gap-x-6 rounded-2xl bg-zinc-900/50 p-6 ring-1 ring-inset ring-zinc-800/50 hover:bg-zinc-800/50 transition-colors"
              >
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-zinc-800 ring-1 ring-zinc-700/50 group-hover:bg-zinc-700/50 transition-colors">
                  <span className="text-zinc-300 font-mono text-sm">{row.weight}</span>
                </div>
                <div>
                  <h3 className="text-base font-semibold leading-7 text-zinc-200">
                    {row.label}
                  </h3>
                  <p className="mt-2 text-sm leading-6 text-zinc-400">
                    {row.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="lg:pl-8 flex flex-col justify-center">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              className="rounded-2xl bg-zinc-900 ring-1 ring-zinc-800 p-8 shadow-2xl relative overflow-hidden"
            >
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-500 to-emerald-400 opacity-50" />
              <div className="flex flex-col gap-6">
                <div>
                  <h4 className="text-sm font-medium text-emerald-400 font-mono mb-2">PERFORMANCE METRICS</h4>
                  <p className="text-xl font-medium text-zinc-200">{methodologyContent.noteArchitecture}</p>
                </div>
                <div className="h-px bg-zinc-800" />
                <div>
                  <h4 className="text-sm font-medium text-emerald-400 font-mono mb-2">CONSTRAINTS</h4>
                  <p className="text-xl font-medium text-zinc-200">{methodologyContent.noteDataset}</p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
