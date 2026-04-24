"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import {
  Cpu,
  Plus,
  Wifi,
  WifiOff,
  Trash2,
  MapPin,
  X,
} from "lucide-react";
import { usePrinters, useCreatePrinter, useDeletePrinter, type PrinterData } from "@/lib/hooks";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function FarmPage() {
  const searchParams = useSearchParams();
  const { data: printers = [], isLoading } = usePrinters();
  const createPrinter = useCreatePrinter();
  const deletePrinter = useDeletePrinter();
  const [showAdd, setShowAdd] = useState(false);

  // Auto-open form when linked from settings with ?add=1
  useEffect(() => {
    if (searchParams.get("add") === "1") {
      setShowAdd(true);
    }
  }, [searchParams]);

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-4 sm:mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-gradient-to-br from-primary/30 to-accent/30 p-2.5">
            <Cpu className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold">Printer Farm</h1>
            <p className="text-xs sm:text-sm text-muted-foreground">
              {printers.length} printer{printers.length !== 1 ? "s" : ""} configured
            </p>
          </div>
        </div>
        <Button
          onClick={() => setShowAdd(true)}
          size="sm"
          className="rounded-xl w-full sm:w-auto"
        >
          <Plus className="mr-2 h-3.5 w-3.5" />
          Add Printer
        </Button>
      </div>

      {showAdd && (
        <AddPrinterForm
          onSubmit={(data) => {
            createPrinter.mutate(data, { onSuccess: () => setShowAdd(false) });
          }}
          onCancel={() => setShowAdd(false)}
          isPending={createPrinter.isPending}
        />
      )}

      {isLoading ? (
        <div className="glass rounded-2xl p-8 sm:p-12 text-center">
          <Cpu className="mx-auto mb-3 h-8 w-8 animate-pulse text-muted-foreground/40" />
          <p className="text-sm text-muted-foreground">Loading printers...</p>
        </div>
      ) : printers.length === 0 && !showAdd ? (
        <button
          onClick={() => setShowAdd(true)}
          className="w-full glass rounded-2xl p-8 sm:p-12 text-center border border-dashed border-white/15 hover:border-primary/40 hover:bg-primary/5 transition-all duration-300 group cursor-pointer"
        >
          <Plus className="mx-auto mb-3 h-10 w-10 text-muted-foreground/30 group-hover:text-primary/60 transition-colors" />
          <p className="text-sm font-medium text-muted-foreground group-hover:text-foreground/80 transition-colors">
            Add your first printer
          </p>
          <p className="text-xs text-muted-foreground/50 mt-1">
            Bambu, Prusa, Creality, and more
          </p>
        </button>
      ) : (
        <div className="space-y-3">
          {printers.map((printer) => (
            <PrinterCard
              key={printer.id}
              printer={printer}
              onDelete={() => deletePrinter.mutate(printer.id)}
              isDeleting={deletePrinter.isPending}
            />
          ))}

          {/* Inline add button — smaller when printers exist */}
          {!showAdd && (
            <button
              onClick={() => setShowAdd(true)}
              className="w-full rounded-2xl border border-dashed border-white/10 hover:border-primary/30 hover:bg-primary/5 py-3 flex items-center justify-center gap-2 text-sm text-muted-foreground/50 hover:text-muted-foreground transition-all duration-200 group"
            >
              <Plus className="h-4 w-4 group-hover:text-primary/60 transition-colors" />
              Add another printer
            </button>
          )}
        </div>
      )}
    </div>
  );
}

function PrinterCard({
  printer,
  onDelete,
  isDeleting,
}: {
  printer: PrinterData;
  onDelete: () => void;
  isDeleting: boolean;
}) {
  const isOnline = printer.status === "online" || printer.status === "idle";

  return (
    <div className="glass rounded-2xl p-4 sm:p-5">
      <div className="flex items-start gap-3 sm:gap-4">
        <div className={`rounded-xl p-2.5 shrink-0 ${isOnline ? "bg-success/10" : "bg-muted"}`}>
          {isOnline ? (
            <Wifi className="h-5 w-5 text-success" />
          ) : (
            <WifiOff className="h-5 w-5 text-muted-foreground" />
          )}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <h3 className="font-semibold text-sm sm:text-base">{printer.model}</h3>
            <Badge variant={isOnline ? "success" : "default"}>
              {printer.status}
            </Badge>
            <Badge>{printer.connection_type.toUpperCase()}</Badge>
          </div>

          <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground mt-1">
            <span className="font-mono">{printer.ip}</span>
            <span>SN: {printer.serial}</span>
            {printer.location_label && (
              <span className="flex items-center gap-1">
                <MapPin className="h-3 w-3" />
                {printer.location_label}
              </span>
            )}
          </div>

          {printer.last_seen && (
            <p className="text-[11px] text-muted-foreground/50 mt-1">
              Last seen: {new Date(printer.last_seen).toLocaleString()}
            </p>
          )}
        </div>

        <Button
          variant="ghost"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          disabled={isDeleting}
          className="text-muted-foreground hover:text-destructive shrink-0"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}

function AddPrinterForm({
  onSubmit,
  onCancel,
  isPending,
}: {
  onSubmit: (data: Partial<PrinterData>) => void;
  onCancel: () => void;
  isPending: boolean;
}) {
  const [model, setModel] = useState("Bambu Lab P1S");
  const [serial, setSerial] = useState("");
  const [ip, setIp] = useState("");
  const [location, setLocation] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ model, serial, ip, location_label: location || null });
  };

  const inputClass =
    "w-full rounded-xl bg-white/5 border border-white/10 px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-1 focus:ring-primary/50";

  return (
    <div className="glass rounded-2xl p-4 sm:p-5 mb-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">Add Printer</h3>
        <button onClick={onCancel} className="text-muted-foreground hover:text-foreground">
          <X className="h-4 w-4" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-muted-foreground block mb-1">Model</label>
            <select value={model} onChange={(e) => setModel(e.target.value)} className={inputClass}>
              <option value="Bambu Lab P1S">Bambu Lab P1S</option>
              <option value="Bambu Lab X1C">Bambu Lab X1C</option>
              <option value="Bambu Lab A1">Bambu Lab A1</option>
              <option value="Bambu Lab A1 Mini">Bambu Lab A1 Mini</option>
              <option value="Prusa MK4S">Prusa MK4S</option>
              <option value="Prusa Mini+">Prusa Mini+</option>
              <option value="Creality K1 Max">Creality K1 Max</option>
              <option value="Creality Ender 3 V3">Creality Ender 3 V3</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-muted-foreground block mb-1">Serial Number</label>
            <input type="text" value={serial} onChange={(e) => setSerial(e.target.value)}
              placeholder="e.g. 01P00A000000" className={inputClass} required />
          </div>
          <div>
            <label className="text-xs text-muted-foreground block mb-1">IP Address</label>
            <input type="text" value={ip} onChange={(e) => setIp(e.target.value)}
              placeholder="e.g. 192.168.1.100" className={inputClass} required />
          </div>
          <div>
            <label className="text-xs text-muted-foreground block mb-1">Location (optional)</label>
            <input type="text" value={location} onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g. Office, Garage" className={inputClass} />
          </div>
        </div>

        <div className="flex gap-2 pt-2">
          <Button type="submit" disabled={isPending} size="sm" className="rounded-xl">
            {isPending ? "Adding..." : "Add Printer"}
          </Button>
          <Button type="button" variant="ghost" size="sm" onClick={onCancel} className="rounded-xl">
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
}
