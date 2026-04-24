"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Mail, ArrowRight, Key, CheckCircle, AlertCircle } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";

export default function LoginPage() {
  const router = useRouter();
  const { login, verify } = useAuth();
  const [step, setStep] = useState<"email" | "token">("email");
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const msg = await login(email);
      setMessage(msg);
      setStep("token");
      // In dev mode, auto-extract the token from the response
      const tokenMatch = msg.match(/token to verify: (.+)$/);
      if (tokenMatch) {
        setToken(tokenMatch[1]);
      }
    } catch {
      setError("Failed to send magic link. Is the API running?");
    } finally {
      setLoading(false);
    }
  };

  const handleTokenSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const success = await verify(token);
      if (success) {
        router.push("/opportunities");
      } else {
        setError("Invalid or expired token");
      }
    } catch {
      setError("Verification failed");
    } finally {
      setLoading(false);
    }
  };

  const inputClass =
    "w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all";

  return (
    <div className="flex min-h-screen items-center justify-center -mt-14 lg:-mt-8">
      <div className="w-full max-w-sm mx-auto">
        {/* Logo */}
        <div className="text-center mb-8">
          <img src="/logo.svg" alt="Forge" className="h-14 w-14 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-gradient">FORGE</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Sign in to your control panel
          </p>
        </div>

        {/* Card */}
        <div className="glass rounded-2xl p-6 sm:p-8">
          {step === "email" ? (
            <form onSubmit={handleEmailSubmit} className="space-y-4">
              <div>
                <label className="text-xs text-muted-foreground block mb-1.5">
                  Email address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground/50" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    className={`${inputClass} pl-10`}
                    required
                    autoFocus
                  />
                </div>
              </div>

              <Button
                type="submit"
                disabled={loading || !email}
                className="w-full rounded-xl h-11"
              >
                {loading ? (
                  "Sending..."
                ) : (
                  <>
                    Send Magic Link
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </form>
          ) : (
            <form onSubmit={handleTokenSubmit} className="space-y-4">
              {/* Success message */}
              <div className="rounded-xl bg-success/10 border border-success/20 p-3 flex items-start gap-2">
                <CheckCircle className="h-4 w-4 text-success shrink-0 mt-0.5" />
                <p className="text-xs text-success">{message}</p>
              </div>

              <div>
                <label className="text-xs text-muted-foreground block mb-1.5">
                  Verification token
                </label>
                <div className="relative">
                  <Key className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground/50" />
                  <input
                    type="text"
                    value={token}
                    onChange={(e) => setToken(e.target.value)}
                    placeholder="Paste your token"
                    className={`${inputClass} pl-10 font-mono text-xs`}
                    required
                    autoFocus
                  />
                </div>
              </div>

              <Button
                type="submit"
                disabled={loading || !token}
                className="w-full rounded-xl h-11"
              >
                {loading ? "Verifying..." : "Sign In"}
              </Button>

              <button
                type="button"
                onClick={() => { setStep("email"); setError(""); }}
                className="w-full text-xs text-muted-foreground/60 hover:text-muted-foreground transition-colors"
              >
                Use a different email
              </button>
            </form>
          )}

          {error && (
            <div className="mt-4 rounded-xl bg-destructive/10 border border-destructive/20 p-3 flex items-start gap-2">
              <AlertCircle className="h-4 w-4 text-destructive shrink-0 mt-0.5" />
              <p className="text-xs text-destructive">{error}</p>
            </div>
          )}
        </div>

        <p className="text-center text-[11px] text-muted-foreground/30 mt-6">
          Passwordless login via magic link
        </p>
      </div>
    </div>
  );
}
