import { Cpu } from "lucide-react";

export default function FarmPage() {
  return (
    <div>
      <div className="mb-4 sm:mb-6 flex items-center gap-3">
        <Cpu className="h-5 w-5 sm:h-6 sm:w-6 text-primary" />
        <h1 className="text-xl sm:text-2xl font-bold">Printer Farm</h1>
      </div>

      <div className="glass rounded-2xl p-8 sm:p-12 text-center">
        <Cpu className="mx-auto mb-4 h-8 w-8 sm:h-12 sm:w-12 text-muted-foreground/50" />
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
