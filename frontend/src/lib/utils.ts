export function cn(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(" ");
}

export function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
}

export function getRankBadgeColor(rankTitle: string): string {
  if (rankTitle.includes("Магистр")) return "bg-purple-100 text-purple-800 border-purple-300";
  if (rankTitle.includes("Сеньор")) return "bg-blue-100 text-blue-800 border-blue-300";
  if (rankTitle.includes("Продвинутый")) return "bg-teal-100 text-teal-800 border-teal-300";
  if (rankTitle.includes("Исследователь")) return "bg-amber-100 text-amber-800 border-amber-300";
  return "bg-stone-100 text-stone-700 border-stone-300";
}
