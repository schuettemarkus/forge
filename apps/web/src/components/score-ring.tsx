"use client";

import { cn } from "@/lib/utils";

interface ScoreRingProps {
  score: number;
  max?: number;
  size?: number;
  className?: string;
}

export function ScoreRing({ score, max = 100, size = 48, className }: ScoreRingProps) {
  const pct = Math.min(score / max, 1);
  const radius = (size - 6) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - pct);

  // Color based on score
  const color =
    pct > 0.6 ? "stroke-success" : pct > 0.3 ? "stroke-warning" : "stroke-destructive";

  return (
    <div className={cn("relative inline-flex items-center justify-center", className)}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={3}
          className="text-white/10"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          strokeWidth={3}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className={cn(color, "transition-all duration-700")}
          style={{ animation: "score-fill 1s ease-out" }}
        />
      </svg>
      <span className="absolute text-xs font-bold">
        {score.toFixed(0)}
      </span>
    </div>
  );
}
