import Link from "next/link";
import { Brain, Upload, Zap, Shield } from "lucide-react";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-bg px-4">
      {/* Hero */}
      <div className="text-center max-w-2xl">
        <div className="mb-6 flex justify-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-accent shadow-lg shadow-accent/20">
            <Brain className="h-8 w-8 text-white" />
          </div>
        </div>
        <h1 className="mb-4 text-4xl font-bold tracking-tight text-foreground">
          MetaMemory Studio
        </h1>
        <p className="mb-8 text-lg text-muted-foreground max-w-md mx-auto">
          The memory control plane for agentic systems. Inspect, evolve, and
          govern what your agents remember.
        </p>

        <div className="flex flex-wrap justify-center gap-3 mb-16">
          <Link
            href="/workspaces/demo"
            className="inline-flex items-center gap-2 rounded-lg bg-accent px-5 py-2.5 text-sm font-medium text-white hover:bg-accent-hover transition-colors"
          >
            <Zap className="h-4 w-4" />
            Import demo trace
          </Link>
          <label className="inline-flex cursor-pointer items-center gap-2 rounded-lg border border-border bg-surface px-5 py-2.5 text-sm font-medium text-foreground hover:bg-surface-raised transition-colors">
            <Upload className="h-4 w-4" />
            Upload your trace
            <input type="file" accept=".jsonl" className="sr-only" />
          </label>
        </div>

        {/* Feature grid */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {features.map((f) => (
            <div
              key={f.title}
              className="rounded-lg border border-border bg-surface p-4 text-left"
            >
              <f.icon className="mb-2 h-5 w-5 text-accent" />
              <h3 className="text-sm font-semibold text-foreground">{f.title}</h3>
              <p className="mt-1 text-xs text-muted-foreground">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>

      <p className="mt-12 text-xs text-muted">Press / to open command palette</p>
    </div>
  );
}

const features = [
  {
    icon: Brain,
    title: "Memory Library",
    desc: "Browse, search, and filter every memory your agents have constructed.",
  },
  {
    icon: Zap,
    title: "Contribution Scoring",
    desc: "Measure how each memory affected run outcomes and update weights.",
  },
  {
    icon: Shield,
    title: "Tamper-Evident Audit",
    desc: "SHA-256 hash chain on every event. Verify integrity at any time.",
  },
];
