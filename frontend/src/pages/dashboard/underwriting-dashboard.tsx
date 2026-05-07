import { ChangeEvent, useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { CircleMarker, MapContainer, Rectangle, TileLayer, Tooltip, useMap, useMapEvents } from "react-leaflet";
import type { LatLngBoundsExpression, LatLngExpression } from "leaflet";
import { Brain, ChevronDown, ChevronUp, Info, MapPin, PencilLine, X } from "lucide-react";
import dekkalLogo from "@/assets/officiel_dekkal_logo.png";
import { Button } from "@/components/ui/button";
import { downloadWordReport, normalizeUnknownError, scoreLocation } from "@/api";
import { DAKAR_BOUNDS, DAKAR_CENTER, riskColors } from "@/lib/constants";
import { t, type Lang } from "@/lib/i18n";
import { sampleScore } from "@/sample";
import type { ApiErrorState, PropertyType, RiskLevel, ScoreRequest, ScoreResponse } from "@/types";

type FinalDecision = "accepted" | "referred" | "inspection_requested" | "declined" | "priced_up";

interface CaseRecord {
  id: string;
  location: string;
  score: number;
  riskLevel: RiskLevel;
  finalDecision: FinalDecision;
}

interface BatchRow {
  id: string;
  label: string;
  request: ScoreRequest;
  status: "pending" | "scoring" | "complete" | "failed";
  result?: ScoreResponse;
  error?: string;
}

const finalDecisionLabels: Record<FinalDecision, string> = {
  accepted: "Accept",
  referred: "Refer",
  inspection_requested: "Request inspection",
  declined: "Decline",
  priced_up: "Price up",
};

function validateInput(address: string, lat: string, lon: string): ScoreRequest | ApiErrorState {
  const trimmedAddress = address.trim();
  const hasLatLon = lat.trim() !== "" || lon.trim() !== "";
  if (trimmedAddress && !hasLatLon) return { address: trimmedAddress };
  if (lat.trim() === "" || lon.trim() === "") {
    return { title: "Missing location", message: "Enter an address or both latitude and longitude." };
  }
  const parsedLat = Number(lat);
  const parsedLon = Number(lon);
  if (!Number.isFinite(parsedLat) || !Number.isFinite(parsedLon)) {
    return { title: "Invalid coordinates", message: "Latitude and longitude must be valid numbers." };
  }
  return { lat: parsedLat, lon: parsedLon };
}

function makeSampleResult(request?: ScoreRequest, index = 0): ScoreResponse {
  const levels: RiskLevel[] = ["Low", "Moderate", "High", "Extreme"];
  const level = levels[index % levels.length];
  const scoreByLevel: Record<RiskLevel, number> = { Low: 24, Moderate: 48, High: 68, Extreme: 86 };
  return {
    ...sampleScore,
    location: {
      lat: request?.lat ?? sampleScore.location.lat + index * 0.004,
      lon: request?.lon ?? sampleScore.location.lon + index * 0.004,
      address_normalized: request?.address ?? `Portfolio location ${index + 1}, Dakar`,
    },
    score: scoreByLevel[level],
    risk_level: level,
    decision_support: {
      action:
        level === "Low"
          ? "standard_underwriting"
          : level === "Moderate"
            ? "file_review"
            : level === "High"
              ? "field_verification_recommended"
              : "mandatory_human_decision",
      label:
        level === "Low"
          ? "Standard underwriting"
          : level === "Moderate"
            ? "File review recommended"
            : level === "High"
              ? "Field verification advised"
              : "Mandatory human decision required",
    },
  };
}

function parseCsvRows(text: string): BatchRow[] {
  const lines = text.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  if (lines.length < 2) return [];
  const headers = lines[0].split(",").map((header) => header.trim().toLowerCase());
  return lines.slice(1).map((line, index) => {
    const values = line.split(",").map((value) => value.trim());
    const row = Object.fromEntries(headers.map((header, headerIndex) => [header, values[headerIndex] ?? ""]));
    const address = row.address || row.location || row.site;
    const lat = Number(row.lat || row.latitude);
    const lon = Number(row.lon || row.lng || row.longitude);
    return {
      id: `${Date.now()}-${index}`,
      label: address || `${lat}, ${lon}`,
      request: address ? { address } : { lat, lon },
      status: "pending",
    };
  });
}

function escapeCsv(value: unknown) {
  return `"${String(value ?? "").replaceAll('"', '""')}"`;
}

function exportTextFile(filename: string, content: string, type = "text/plain;charset=utf-8") {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}


function riskPillClass(level: RiskLevel) {
  const classes: Record<RiskLevel, string> = {
    Low: "bg-emerald-100 text-emerald-800",
    Moderate: "bg-amber-100 text-amber-800",
    High: "bg-orange-100 text-orange-800",
    Extreme: "bg-red-100 text-red-800",
  };
  return classes[level];
}

function impactClass(impact: string) {
  if (impact.toLowerCase() === "high") return "bg-red-100 text-red-800";
  if (impact.toLowerCase() === "medium") return "bg-amber-100 text-amber-800";
  return "bg-emerald-100 text-emerald-800";
}

function scoreDegrees(score: number) {
  return Math.max(0, Math.min(100, score)) * 3.6;
}

interface NominatimSuggestion {
  display_name: string;
  lat: string;
  lon: string;
  boundingbox: [string, string, string, string]; // [south, north, west, east]
}

function FlyController({ target }: { target: LatLngBoundsExpression | null }) {
  const map = useMap();
  useEffect(() => {
    if (target) map.flyToBounds(target, { padding: [40, 40], maxZoom: 17, duration: 1.1 });
  }, [target, map]);
  return null;
}

function PositionTracker({
  latLon,
  onPositionChange,
}: {
  latLon: [number, number] | null;
  onPositionChange: (pos: { x: number; y: number } | null) => void;
}) {
  const map = useMap();
  useEffect(() => {
    if (!latLon) { onPositionChange(null); return; }
    const update = () => {
      const p = map.latLngToContainerPoint(latLon);
      onPositionChange({ x: p.x, y: p.y });
    };
    update();
    map.on("move zoom moveend zoomend", update);
    return () => { map.off("move zoom moveend zoomend", update); };
  }, [latLon, onPositionChange, map]);
  return null;
}

function MapClickHandler({ onPick }: { onPick: (lat: number, lon: number) => void }) {
  useMapEvents({
    click(event) {
      onPick(Number(event.latlng.lat.toFixed(6)), Number(event.latlng.lng.toFixed(6)));
    },
  });
  return null;
}


function getTooltips(lang: Lang): Record<string, string> {
  const tr = t[lang];
  return {
    [tr.historicalRisk] : tr.tooltipHistorical,
    [tr.structuralVuln] : tr.tooltipStructural,
    [tr.extremeRisk]    : tr.tooltipExtreme,
  };
}

function InfoTooltip({ text }: { text: string }) {
  const [pos, setPos] = useState<{ x: number; y: number } | null>(null);
  const btnRef = useRef<HTMLButtonElement>(null);

  function show() {
    if (btnRef.current) {
      const r = btnRef.current.getBoundingClientRect();
      setPos({ x: r.left + r.width / 2, y: r.top });
    }
  }

  return (
    <>
      <button
        ref={btnRef}
        type="button"
        className="text-slate-400 hover:text-slate-600 focus:outline-none"
        onMouseEnter={show}
        onMouseLeave={() => setPos(null)}
        aria-label="More information"
      >
        <Info size={13} />
      </button>
      {pos && (
        <div
          className="pointer-events-none w-64 rounded-2xl bg-slate-900 px-3 py-2 text-xs leading-5 text-white shadow-xl"
          style={{
            position: "fixed",
            top: pos.y - 8,
            left: pos.x,
            transform: "translate(-50%, -100%)",
            zIndex: 9999,
          }}
        >
          {text}
          <span
            className="absolute left-1/2 top-full -translate-x-1/2 border-4 border-transparent"
            style={{ borderTopColor: "#0f172a" }}
          />
        </div>
      )}
    </>
  );
}

const RISK_CYCLE = [
  { color: riskColors.Low,      deg: 72  },
  { color: riskColors.Moderate, deg: 144 },
  { color: riskColors.High,     deg: 216 },
  { color: riskColors.Extreme,  deg: 288 },
  { color: riskColors.Low,      deg: 360 },
];

function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-full bg-slate-100 ${className}`} />;
}

function ScoringProgress({ active }: { active: boolean }) {
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    if (!active) { setIdx(0); return; }
    const id = setInterval(() => setIdx(i => (i + 1) % RISK_CYCLE.length), 600);
    return () => clearInterval(id);
  }, [active]);

  if (!active) return null;

  const { color, deg } = RISK_CYCLE[idx];

  return (
    <>
      <section className="rounded-3xl border border-slate-200 bg-white p-4 sm:p-5">
        <div className="grid items-center justify-items-center gap-5 sm:grid-cols-[auto_1fr] sm:justify-items-start">
          <div
            className="relative grid h-36 w-36 shrink-0 place-items-center rounded-full shadow-[inset_0_0_0_1px_rgba(15,23,42,0.04)]"
            style={{
              background: `conic-gradient(${color} ${deg}deg, #e8ebf0 0deg)`,
              transition: "background 0.5s ease",
            }}
          >
            <div className="absolute inset-4 grid place-items-center rounded-full bg-white shadow-[inset_0_1px_8px_rgba(15,23,42,0.08)]">
              <div className="flex gap-1.5">
                {[0, 1, 2].map(i => (
                  <span
                    key={i}
                    className="h-2 w-2 rounded-full"
                    style={{
                      backgroundColor: color,
                      transition: "background-color 0.5s ease",
                      animation: `pulse 0.9s ease-in-out ${i * 0.2}s infinite`,
                    }}
                  />
                ))}
              </div>
            </div>
          </div>
          <div className="w-full min-w-0 space-y-3 text-center sm:text-left">
            <Skeleton className="h-5 w-20" />
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-64" />
          </div>
        </div>
      </section>

      <section className="rounded-3xl border border-slate-200 bg-white p-4 sm:p-5">
        <Skeleton className="mb-4 h-5 w-32" />
        <div className="grid gap-4">
          {["w-28", "w-36", "w-24"].map((w, i) => (
            <div key={i} className="grid gap-2">
              <div className="flex items-center justify-between">
                <Skeleton className={`h-4 ${w}`} />
                <Skeleton className="h-4 w-8" />
              </div>
              <Skeleton className="h-2 w-full rounded-full" />
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-3xl border border-slate-200 bg-white p-4 sm:p-5">
        <Skeleton className="mb-4 h-5 w-20" />
        <div className="grid gap-2">
          {[1, 2].map(i => (
            <div key={i} className="rounded-2xl border border-slate-100 p-3">
              <Skeleton className="mb-2 h-5 w-12" />
              <Skeleton className="h-4 w-full" />
            </div>
          ))}
        </div>
      </section>
    </>
  );
}

function Collapsible({ title, children, defaultOpen = false }: { title: string; children: ReactNode; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <article className="rounded-2xl border border-slate-100 bg-slate-50/60">
      <button
        type="button"
        className="flex w-full items-center justify-between px-3 py-3 text-left"
        onClick={() => setOpen((prev) => !prev)}
      >
        <strong className="text-sm text-ink">{title}</strong>
        {open ? <ChevronUp size={14} className="shrink-0 text-slate-400" /> : <ChevronDown size={14} className="shrink-0 text-slate-400" />}
      </button>
      {open && <div className="px-3 pb-3">{children}</div>}
    </article>
  );
}

function ComponentBar({ label, value, lang }: { label: string; value: number; lang: Lang }) {
  const tips = getTooltips(lang);
  const tip = tips[label];
  return (
    <div className="grid gap-2">
      <div className="flex items-center justify-between text-sm">
        <span className="flex items-center gap-1.5 text-slate-600">
          {label}
          {tip && <InfoTooltip text={tip} />}
        </span>
        <strong className="text-ink">{value.toFixed(1)}</strong>
      </div>
      <div className="h-2 rounded-full bg-slate-100">
        <div className="h-full rounded-full bg-mercury-blue" style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
      </div>
    </div>
  );
}

export function UnderwritingDashboardPage() {
  const [address, setAddress] = useState("Pikine Technopole, Dakar");
  const [lat, setLat] = useState("");
  const [lon, setLon] = useState("");
  const [result, setResult] = useState<ScoreResponse | null>(null);
  const [error, setError] = useState<ApiErrorState | null>(null);
  const [loading, setLoading] = useState(false);
  const [lang, setLang] = useState<Lang>("en");
  const tr = t[lang];
  const [propertyType, setPropertyType] = useState<PropertyType>("residential");
  const [sampleMode, setSampleMode] = useState(false);
  const [formOpen, setFormOpen] = useState(false);
  const [mapSelection, setMapSelection] = useState<{ lat: number; lon: number; address: string; fetching: boolean } | null>(null);
  const [finalDecision, setFinalDecision] = useState<FinalDecision>("referred");
  const [notes, setNotes] = useState("");
  const [mapMode, setMapMode] = useState<"street" | "satellite">("street");
  const [flyTarget, setFlyTarget] = useState<LatLngBoundsExpression | null>(null);
  const [markerPixelPos, setMarkerPixelPos] = useState<{ x: number; y: number } | null>(null);
  const [highlightActive, setHighlightActive] = useState(false);
  const onMarkerPositionChange = useCallback((pos: { x: number; y: number } | null) => setMarkerPixelPos(pos), []);
  const [suggestions, setSuggestions] = useState<NominatimSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const searchTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [exporting, setExporting] = useState(false);
  const [savedCases, setSavedCases] = useState<CaseRecord[]>([]);
  const [batchRows, setBatchRows] = useState<BatchRow[]>([]);
  const [batchRunning, setBatchRunning] = useState(false);
  const batchInputRef = useRef<HTMLInputElement | null>(null);


  const markerPosition = useMemo<LatLngExpression | null>(() => (
    result ? [result.location.lat, result.location.lon] : null
  ), [result]);

  async function handleMapClick(clickLat: number, clickLon: number) {
    setMapSelection({ lat: clickLat, lon: clickLon, address: "", fetching: true });
    setLat(String(clickLat));
    setLon(String(clickLon));
    setAddress("");
    try {
      const r = await fetch(
        `https://nominatim.openstreetmap.org/reverse?lat=${clickLat}&lon=${clickLon}&format=json&zoom=16&accept-language=${lang}`
      );
      const d = await r.json();
      const addr = d.display_name?.split(",").slice(0, 3).join(", ") || `${clickLat.toFixed(5)}, ${clickLon.toFixed(5)}`;
      setMapSelection({ lat: clickLat, lon: clickLon, address: addr, fetching: false });
    } catch {
      setMapSelection({ lat: clickLat, lon: clickLon, address: `${clickLat.toFixed(5)}, ${clickLon.toFixed(5)}`, fetching: false });
    }
  }

  async function submitScore(requestOverride?: ScoreRequest) {
    setError(null);
    setLoading(true);
    setMapSelection(null);
    try {
      if (sampleMode) {
        await new Promise((resolve) => window.setTimeout(resolve, 250));
        setResult(makeSampleResult(requestOverride, 2));
        return;
      }
      const request = requestOverride ?? validateInput(address, lat, lon);
      if ("title" in request) {
        setError(request);
        return;
      }
      const response = await scoreLocation({ ...request, property_type: propertyType }, { lang });
      setResult(response);
      setHighlightActive(true);
      setFinalDecision(response.decision_support.action === "standard_underwriting" ? "accepted" : response.decision_support.action === "field_verification_recommended" ? "inspection_requested" : "referred");
    } catch (caught) {
      setError(normalizeUnknownError(caught));
    } finally {
      setLoading(false);
    }
  }

  function saveCase() {
    if (!result) return;
    setSavedCases((current) => [
      {
        id: crypto.randomUUID(),
        location: result.location.address_normalized,
        score: result.score,
        riskLevel: result.risk_level,
        finalDecision,
      },
      ...current,
    ]);
  }

  const handleAddressChange = useCallback((value: string) => {
    setAddress(value);
    setLat("");
    setLon("");
    if (searchTimer.current) clearTimeout(searchTimer.current);
    if (value.trim().length < 2) { setSuggestions([]); setShowSuggestions(false); return; }
    searchTimer.current = setTimeout(async () => {
      try {
        const params = new URLSearchParams({
          q: value,
          format: "json",
          limit: "7",
          viewbox: "-17.6,14.95,-17.1,14.6",
          bounded: "1",
          "accept-language": lang,
          addressdetails: "0",
        });
        const r = await fetch(`https://nominatim.openstreetmap.org/search?${params}`, {
          headers: { "Accept-Language": lang }
        });
        const data: NominatimSuggestion[] = await r.json();
        setSuggestions(data);
        setShowSuggestions(data.length > 0);
        if (data[0]?.boundingbox) {
          const [s, n, w, e] = data[0].boundingbox.map(Number);
          setFlyTarget([[s, w], [n, e]]);
        }
      } catch { /* ignore network errors during typing */ }
    }, 320);
  }, [lang]);

  function selectSuggestion(s: NominatimSuggestion) {
    const shortName = s.display_name.split(",").slice(0, 3).join(",").trim();
    setAddress(shortName);
    setLat(s.lat);
    setLon(s.lon);
    setSuggestions([]);
    setShowSuggestions(false);
    const [south, north, west, east] = s.boundingbox.map(Number);
    setFlyTarget([[south, west], [north, east]]);
  }

  async function exportCurrentReport() {
    if (!result || exporting) return;
    setExporting(true);
    try {
      await downloadWordReport(result, { lang });
    } catch (caught) {
      setError(normalizeUnknownError(caught));
    } finally {
      setExporting(false);
    }
  }

  async function uploadBatch(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setBatchRows(parseCsvRows(await file.text()));
    if (batchInputRef.current) batchInputRef.current.value = "";
  }

  async function runBatch() {
    if (!batchRows.length) return;
    setBatchRunning(true);
    const nextRows = [...batchRows];
    for (let index = 0; index < nextRows.length; index += 1) {
      nextRows[index] = { ...nextRows[index], status: "scoring", error: undefined };
      setBatchRows([...nextRows]);
      try {
        const scored = sampleMode ? makeSampleResult(nextRows[index].request, index) : await scoreLocation(nextRows[index].request);
        nextRows[index] = { ...nextRows[index], status: "complete", result: scored };
      } catch (caught) {
        nextRows[index] = { ...nextRows[index], status: "failed", error: normalizeUnknownError(caught).message };
      }
      setBatchRows([...nextRows]);
    }
    setBatchRunning(false);
  }

  function exportBatchCsv() {
    const rows = [
      ["location", "score", "risk_level", "recommendation", "confidence", "model_version", "status", "error"].map(escapeCsv),
      ...batchRows.map((row) => [
        row.result?.location.address_normalized ?? row.label,
        row.result?.score ?? "",
        row.result?.risk_level ?? "",
        row.result?.decision_support.label ?? "",
        row.result?.confidence ?? "",
        row.result?.meta.model_version ?? "",
        row.status,
        row.error ?? "",
      ].map(escapeCsv)),
    ];
    exportTextFile(`dekkal-batch-screening-${Date.now()}.csv`, rows.map((row) => row.join(",")).join("\n"), "text/csv;charset=utf-8");
  }

  const finalDecisionLabels: Record<FinalDecision, string> = {
    accepted           : tr.accepted,
    referred           : tr.referred,
    inspection_requested: tr.inspection_requested,
    declined           : tr.declined,
    priced_up          : tr.priced_up,
  };

  return (
    <div className="flex flex-col overflow-y-auto sm:flex-row sm:overflow-hidden sm:h-[calc(100svh-73px)]">

      {/* ── MAP (hero) ───────────────────────────────────── */}
      <div className="relative h-[45vh] shrink-0 overflow-hidden sm:h-auto sm:flex-1">
        <MapContainer center={DAKAR_CENTER} zoom={11} minZoom={10} scrollWheelZoom className="h-full w-full">
          {mapMode === "street" ? (
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
          ) : (
            <>
              <TileLayer
                attribution='&copy; <a href="https://www.esri.com/">Esri</a> &mdash; Source: Esri, Maxar, GeoEye, Earthstar Geographics, CNES/Airbus DS, USDA, USGS, AeroGRID, IGN'
                url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                maxZoom={19}
              />
              <TileLayer
                url="https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
                maxZoom={19}
                attribution=""
              />
            </>
          )}
          <FlyController target={flyTarget} />
          <PositionTracker latLon={markerPosition as [number, number] | null} onPositionChange={onMarkerPositionChange} />
          <Rectangle bounds={DAKAR_BOUNDS} pathOptions={{ color: "#5266eb", weight: 2, fillOpacity: 0.04 }} />
          <MapClickHandler onPick={(lat, lon) => { setHighlightActive(false); handleMapClick(lat, lon); }} />
          {markerPosition ? (
            <CircleMarker center={markerPosition} radius={12} pathOptions={{ color: "#ffffff", weight: 3, fillColor: riskColors[result!.risk_level], fillOpacity: 0.95 }}>
              <Tooltip permanent direction="top" offset={[0, -14]}>{tr[result!.risk_level]} · {result!.score}</Tooltip>
            </CircleMarker>
          ) : null}
        </MapContainer>

        {/* Spotlight + pulse highlight after scoring */}
        {highlightActive && markerPixelPos && result && (
          <>
            {/* Dark vignette with spotlight hole */}
            <div
              className="pointer-events-none absolute inset-0 z-[998] transition-opacity duration-700"
              style={{
                background: `radial-gradient(circle at ${markerPixelPos.x}px ${markerPixelPos.y}px, transparent 72px, rgba(0,0,0,0.45) 170px)`,
              }}
            />
            {/* Pulsing ring */}
            <div
              className="pointer-events-none absolute z-[999]"
              style={{ left: markerPixelPos.x - 28, top: markerPixelPos.y - 28, width: 56, height: 56 }}
            >
              <div
                className="absolute inset-0 animate-ping rounded-full opacity-60"
                style={{ backgroundColor: riskColors[result.risk_level] }}
              />
            </div>
            {/* Dismiss button */}
            <button
              type="button"
              onClick={() => setHighlightActive(false)}
              className="absolute right-16 top-3 z-[1000] flex items-center gap-1.5 rounded-full border border-white/30 bg-black/40 px-3 py-1.5 text-xs text-white backdrop-blur-sm hover:bg-black/60"
            >
              <X size={11} /> Dismiss
            </button>
          </>
        )}

        {/* Map mode toggle */}
        <div className="absolute right-3 top-3 z-[1000] flex overflow-hidden rounded-full border border-slate-200 bg-white shadow-md">
          <button
            type="button"
            onClick={() => setMapMode("street")}
            className={`px-3 py-1.5 text-xs font-medium transition-colors ${mapMode === "street" ? "bg-mercury-blue text-white" : "text-slate-500 hover:bg-slate-50"}`}
          >
            Street
          </button>
          <button
            type="button"
            onClick={() => setMapMode("satellite")}
            className={`px-3 py-1.5 text-xs font-medium transition-colors ${mapMode === "satellite" ? "bg-mercury-blue text-white" : "text-slate-500 hover:bg-slate-50"}`}
          >
            Satellite
          </button>
        </div>

        {/* Location preview card — appears on map click */}
        {mapSelection && !loading && (
          <div className="absolute inset-x-4 bottom-6 z-[1000] flex justify-center">
            <div className="w-full max-w-sm rounded-3xl border border-slate-100 bg-white p-4 shadow-2xl shadow-slate-900/20">
              <div className="flex items-start gap-3">
                <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl bg-mercury-blue/10">
                  <MapPin size={16} className="text-mercury-blue" />
                </div>
                <div className="min-w-0 flex-1">
                  {mapSelection.fetching ? (
                    <div className="space-y-2">
                      <div className="h-4 w-40 animate-pulse rounded-full bg-slate-100" />
                      <div className="h-3 w-28 animate-pulse rounded-full bg-slate-100" />
                    </div>
                  ) : (
                    <>
                      <p className="line-clamp-2 text-sm font-medium leading-snug text-ink">{mapSelection.address}</p>
                      <p className="mt-0.5 text-xs text-slate-400">{mapSelection.lat.toFixed(5)}, {mapSelection.lon.toFixed(5)}</p>
                    </>
                  )}
                </div>
                <button type="button" onClick={() => setMapSelection(null)} className="shrink-0 rounded-full p-1 text-slate-300 hover:bg-slate-100 hover:text-slate-500">
                  <X size={14} />
                </button>
              </div>
              <div className="mt-3 flex items-center gap-2">
                <select
                  className="flex-1 rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-xs outline-none focus:border-mercury-blue"
                  value={propertyType}
                  onChange={(e) => setPropertyType(e.target.value as PropertyType)}
                >
                  <option value="residential">{tr.residential}</option>
                  <option value="commercial">{tr.commercial}</option>
                  <option value="hotel">{tr.hotel}</option>
                  <option value="school">{tr.school}</option>
                  <option value="hospital">{tr.hospital}</option>
                  <option value="warehouse">{tr.warehouse}</option>
                </select>
                <Button
                  className="shrink-0 rounded-full bg-mercury-blue px-5 py-2 text-sm text-white hover:bg-mercury-blue/90"
                  type="button"
                  disabled={loading || mapSelection.fetching}
                  onClick={() => void submitScore({ lat: mapSelection.lat, lon: mapSelection.lon })}
                >
                  {tr.runScore} →
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ── RIGHT PANEL ──────────────────────────────────── */}
      <div className="flex w-full flex-col overflow-hidden border-t border-slate-200 bg-white sm:w-[380px] sm:shrink-0 sm:border-l sm:border-t-0">

        {/* Panel header */}
        <div className="shrink-0 border-b border-slate-100 px-5 py-4">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <p className="text-xs uppercase tracking-[0.2em] text-lead">{tr.quoteReview}</p>
              <h2 className="mt-1 text-base font-medium text-ink">
                {loading ? tr.scoringInProcess : result ? tr.scoringTitle : "Dëkkal"}
              </h2>
              {loading && (
                <span className="mt-1.5 flex gap-1">
                  {[0,1,2].map(i => (
                    <span key={i} className="h-1 w-1 rounded-full bg-mercury-blue" style={{ animation: `pulse 1s ease-in-out ${i*0.2}s infinite` }} />
                  ))}
                </span>
              )}
            </div>
            <div className="flex shrink-0 items-center gap-1.5 pt-0.5">
              <button type="button" onClick={() => setLang((l) => l === "en" ? "fr" : "en")}
                className="flex items-center rounded-full border border-slate-200 px-2.5 py-1.5 text-xs font-medium hover:bg-slate-50">
                <span className={lang === "en" ? "text-mercury-blue font-semibold" : "text-slate-400"}>EN</span>
                <span className="mx-1 text-slate-200">|</span>
                <span className={lang === "fr" ? "text-mercury-blue font-semibold" : "text-slate-400"}>FR</span>
              </button>
              <button type="button" onClick={() => setFormOpen((o) => !o)} title={tr.scoreLocation}
                className={`flex h-8 w-8 items-center justify-center rounded-full border transition-colors ${formOpen ? "border-mercury-blue bg-mercury-blue/10 text-mercury-blue" : "border-slate-200 text-slate-400 hover:bg-slate-50"}`}>
                <PencilLine size={13} />
              </button>
            </div>
          </div>
        </div>

        {/* Collapsible form */}
        {formOpen && (
          <div className="shrink-0 border-b border-slate-100 bg-slate-50/50 p-4">
            <form className="grid gap-3" onSubmit={(event) => { event.preventDefault(); void submitScore(); }}>
              <div className="grid gap-1.5">
                <span className="text-xs font-medium text-slate-600">{tr.address}</span>
                <div className="relative">
                  <input
                    className="w-full rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm outline-none focus:border-mercury-blue"
                    value={address}
                    onChange={(e) => handleAddressChange(e.target.value)}
                    onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                    onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
                    placeholder="Pikine, Almadies, Guédiawaye…"
                    autoComplete="off"
                  />
                  {showSuggestions && suggestions.length > 0 && (
                    <ul className="absolute left-0 right-0 top-full z-[2000] mt-1 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
                      {suggestions.map((s, i) => (
                        <li key={i} className="border-b border-slate-50 last:border-0">
                          <button
                            type="button"
                            onMouseDown={() => selectSuggestion(s)}
                            className="flex w-full items-start gap-2 px-4 py-2.5 text-left hover:bg-slate-50"
                          >
                            <MapPin size={11} className="mt-0.5 shrink-0 text-mercury-blue" />
                            <span className="line-clamp-2 text-xs leading-4 text-slate-700">
                              {s.display_name.split(",").slice(0, 4).join(",")}
                            </span>
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <label className="grid gap-1.5 text-xs font-medium text-slate-600">
                  {tr.latitude}
                  <input className="rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm outline-none focus:border-mercury-blue" value={lat} onChange={(e) => setLat(e.target.value)} placeholder="14.734" inputMode="decimal" />
                </label>
                <label className="grid gap-1.5 text-xs font-medium text-slate-600">
                  {tr.longitude}
                  <input className="rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm outline-none focus:border-mercury-blue" value={lon} onChange={(e) => setLon(e.target.value)} placeholder="-17.510" inputMode="decimal" />
                </label>
              </div>
              <label className="grid gap-1.5 text-xs font-medium text-slate-600">
                {tr.propertyType}
                <select className="rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm outline-none focus:border-mercury-blue" value={propertyType} onChange={(e) => setPropertyType(e.target.value as PropertyType)}>
                  <option value="residential">{tr.residential}</option>
                  <option value="commercial">{tr.commercial}</option>
                  <option value="hotel">{tr.hotel}</option>
                  <option value="school">{tr.school}</option>
                  <option value="hospital">{tr.hospital}</option>
                  <option value="warehouse">{tr.warehouse}</option>
                </select>
              </label>
              <label className="flex items-center gap-2 text-xs text-slate-500">
                <input type="checkbox" checked={sampleMode} onChange={(e) => setSampleMode(e.target.checked)} className="h-3.5 w-3.5 accent-mercury-blue" />
                {tr.sampleMode}
              </label>
              <Button className="rounded-full bg-mercury-blue py-2.5 text-sm text-white hover:bg-mercury-blue/90" type="submit" disabled={loading}>
                {loading ? tr.scoring : tr.runScore}
              </Button>
            </form>
          </div>
        )}

        {/* Error banner */}
        {error && (
          <div className="shrink-0 border-b border-red-100 bg-red-50 px-5 py-3">
            <p className="text-sm font-medium text-red-900">{error.title}</p>
            <p className="text-xs leading-5 text-red-700">{error.message}</p>
          </div>
        )}

        {/* Results — scrollable */}
        <div className="min-h-0 flex-1 overflow-y-auto p-4 sm:max-h-none">
          {loading ? (
            <ScoringProgress active={loading} />
          ) : result ? (
            <div className="grid gap-3">
              {/* Score */}
              <div className="rounded-3xl border border-slate-200 bg-white p-4">
                <div className="flex items-center gap-4">
                  <div
                    className="relative grid h-24 w-24 shrink-0 place-items-center rounded-full"
                    style={{ background: `conic-gradient(${riskColors[result.risk_level]} ${scoreDegrees(result.score)}deg, #e8ebf0 0deg)` }}
                  >
                    <div className="absolute inset-3 grid place-items-center rounded-full bg-white shadow-[inset_0_1px_6px_rgba(15,23,42,0.08)]">
                      <div className="grid justify-items-center leading-none">
                        <strong className="text-2xl font-medium tabular-nums text-ink">{result.score}</strong>
                        <span className="text-[9px] uppercase tracking-widest text-slate-400">{tr.outOf100}</span>
                      </div>
                    </div>
                  </div>
                  <div className="min-w-0 flex-1">
                    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${riskPillClass(result.risk_level)}`}>{tr[result.risk_level]}</span>
                    <p className="mt-1.5 text-sm font-light leading-snug text-ink">{tr[result.decision_support.action]}</p>
                    <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-slate-500">{result.location.address_normalized}</p>
                  </div>
                </div>
              </div>

              {/* Risk components */}
              <div className="rounded-3xl border border-slate-200 bg-white p-4">
                <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">{tr.riskComponents}</h3>
                <div className="grid gap-3">
                  <ComponentBar label={tr.historicalRisk} value={result.components.historical_risk} lang={lang} />
                  <ComponentBar label={tr.structuralVuln} value={result.components.structural_vulnerability} lang={lang} />
                  <ComponentBar label={tr.extremeRisk} value={result.components.extreme_scenario_risk} lang={lang} />
                </div>
              </div>

              {/* AI Analysis */}
              {result.llm_explanation && (
                <div className="rounded-3xl border border-slate-200 bg-white p-4">
                  <div className="mb-3 flex items-center gap-2">
                    <Brain size={14} className="text-mercury-blue" />
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">{tr.riskAnalysis}</h3>
                  </div>
                  <p className="text-xs leading-6 text-slate-700">{result.llm_explanation.narrative}</p>
                  {result.llm_explanation.breakdown && (
                    <div className="mt-3 grid gap-1.5">
                      {[
                        [tr.historicalRisk, result.llm_explanation.breakdown.historical_risk],
                        [tr.structuralVuln, result.llm_explanation.breakdown.structural_vulnerability],
                        [tr.extremeRisk, result.llm_explanation.breakdown.extreme_scenario_risk],
                      ].map(([label, body]) => (
                        <Collapsible key={label} title={label}>
                          <p className="text-xs leading-5 text-slate-500">{body}</p>
                        </Collapsible>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Underwriting decision */}
              <div className="rounded-3xl border border-slate-200 bg-white p-4">
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">{tr.uwDecision}</h3>
                  <span className="text-[10px] uppercase tracking-widest text-slate-400">{tr.humanLed}</span>
                </div>
                <div className="grid grid-cols-2 gap-1.5">
                  {(Object.keys(finalDecisionLabels) as FinalDecision[]).map((d) => (
                    <Button key={d} type="button" variant={finalDecision === d ? "secondary" : "outline"} className="rounded-full py-1.5 text-xs" onClick={() => setFinalDecision(d)}>
                      {finalDecisionLabels[d]}
                    </Button>
                  ))}
                </div>
                <label className="mt-3 grid gap-1.5 text-xs text-slate-500">
                  {tr.caseNotes}
                  <textarea className="min-h-16 rounded-2xl border border-slate-200 p-3 text-xs outline-none focus:border-mercury-blue" value={notes} onChange={(e) => setNotes(e.target.value)} placeholder={tr.caseNotesPlaceholder} />
                </label>
                <div className="mt-2.5 flex gap-2">
                  <Button variant="outline" className="flex-1 rounded-full text-xs py-2" type="button" onClick={saveCase}>{tr.saveCase}</Button>
                  <Button variant="outline" className="flex-1 rounded-full text-xs py-2" type="button" onClick={() => void exportCurrentReport()} disabled={exporting}>{exporting ? tr.exportingReport : tr.exportReport}</Button>
                </div>
              </div>

              {/* Saved cases */}
              {savedCases.length > 0 && (
                <div className="rounded-3xl border border-slate-200 bg-white p-4">
                  <div className="mb-3 flex items-center justify-between">
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">{tr.savedReviews}</h3>
                    <span className="text-xs text-slate-400">{savedCases.length} {tr.cases}</span>
                  </div>
                  <div className="grid gap-1.5">
                    {savedCases.slice(0, 4).map((item) => (
                      <article key={item.id} className="rounded-2xl border border-slate-100 px-3 py-2">
                        <strong className="block truncate text-xs text-ink">{item.location}</strong>
                        <span className="text-[11px] text-slate-400">{item.riskLevel} · {item.score}/100</span>
                      </article>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex h-full flex-col items-center justify-center px-6 text-center">
              <div className="relative mb-6 flex items-center justify-center" style={{ width: 160, height: 160 }}>
                {[0, 1, 2].map((i) => (
                  <span
                    key={i}
                    className="absolute rounded-full bg-mercury-blue/15"
                    style={{
                      width: 80,
                      height: 80,
                      top: "50%",
                      left: "50%",
                      transform: "translate(-50%, -50%)",
                      animation: `sonar-ring 2.4s ease-out ${i * 0.8}s infinite`,
                    }}
                  />
                ))}
                <div
                  className="relative z-10 flex h-20 w-20 items-center justify-center rounded-full bg-white shadow-xl shadow-mercury-blue/20 ring-1 ring-mercury-blue/20"
                  style={{ animation: "float 3s ease-in-out infinite" }}
                >
                  <img src={dekkalLogo} alt="Dëkkal" className="h-14 w-14 object-contain" />
                </div>
              </div>
              <h3 className="text-lg font-light text-ink">{tr.noScoreYet}</h3>
              <p className="mt-2 text-xs leading-6 text-slate-500">{tr.noScoreDesc}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
