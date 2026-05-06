import type { RiskLevel } from "@/types";

export const VIDEO_SRC =
  "https://res.cloudinary.com/dnemeq7mr/video/upload/v1777417613/p73tpyodp3k6acyfm5jm.mp4";

export const DAKAR_CENTER: [number, number] = [14.735, -17.395];

export const DAKAR_BOUNDS: [[number, number], [number, number]] = [
  [14.6, -17.6],
  [14.95, -17.1],
];

export const riskColors: Record<RiskLevel, string> = {
  Low: "#15803d",
  Moderate: "#b7791f",
  High: "#c2410c",
  Extreme: "#991b1b",
};
