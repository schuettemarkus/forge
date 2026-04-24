import { Cpu } from "lucide-react";

export default function FarmPage() {
  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <Cpu className="h-6 w-6 text-primary" />
        <h1 className="text-2xl font-bold">Printer Farm</h1>
      </div>

      <div className="rounded-lg border border-border bg-card p-12 text-center">
        <Cpu className="mx-auto mb-4 h-12 w-12 text-muted-foreground/50" />
        <p className="text-lg font-medium text-muted-foreground">
          No printers connected
        </p>
        <p className="mt-1 text-sm text-muted-foreground/70">
          Printer controller will connect to your Bambu P1S via MQTT in M4.
        </p>
      </div>
    </div>
  );
}
