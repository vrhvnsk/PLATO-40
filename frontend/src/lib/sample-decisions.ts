/** PLATO-40 decision contract adapter. No fabricated operational records. */
export type Priority = "critical" | "high" | "medium" | "low";
export type Decision = {
 event_id: string; timestamp_utc: string; episode_id: string; issue_type: string;
 priority: Priority; action: string; requires_human_approval: boolean;
 requires_guest_consent?: boolean; reason: string; evidence: string[];
 confidence: number; verification_plan: string;
 affected_assets?: string[]; autonomy?: string; expected_outcome?: string;
 dependencies?: string[]; guest_request_ids?: string[]; resource_id?: string;
};
export const decisions: Decision[] = []; // Legacy export; UI reads provider records.
export const priorities: Priority[] = ["critical", "high", "medium", "low"];
export const issueTypes: string[] = [];
export const label = (s: string) => s.replace(/_/g, " ");
export function parseDecisions(text: string): Decision[] {
 const records = text.trim().startsWith("[") ? JSON.parse(text) : text.split(/\r?\n/).filter(Boolean).map((line, i) => {
   try { return JSON.parse(line); } catch { throw new Error(`Invalid JSON on line ${i+1}`); }
 });
 if (!Array.isArray(records)) throw new Error("Expected JSON array or JSONL records");
 const ids = new Set<string>();
 return records.map((r, i) => {
  if (!r || typeof r !== "object" || typeof r.event_id !== "string" || typeof r.timestamp_utc !== "string" || typeof r.action !== "string" || typeof r.issue_type !== "string" || typeof r.reason !== "string") throw new Error(`Invalid decision record ${i+1}`);
  if (ids.has(r.event_id)) throw new Error(`Duplicate event_id: ${r.event_id}`);
  ids.add(r.event_id);
  if (!["critical","high","medium","low"].includes(r.priority)) throw new Error(`Invalid priority for ${r.event_id}`);
  if (typeof r.requires_human_approval !== "boolean") throw new Error(`Missing approval flag for ${r.event_id}`);
  return {...r, episode_id: String(r.episode_id ?? r.event_id), evidence: Array.isArray(r.evidence) ? r.evidence.map(String) : [], confidence: typeof r.confidence === "number" ? r.confidence : 0, verification_plan: String(r.verification_plan ?? "Not specified"), requires_guest_consent: r.requires_guest_consent === true} as Decision;
 });
}
export function timeline(list: Decision[]) {
 const issues = [...new Set(list.map(d=>d.issue_type))];
 const m = new Map<string, Record<string, number|string>>();
 list.forEach(d=>{const day=d.timestamp_utc.slice(5,10); const r=m.get(day)??{day};r[d.issue_type]=((r[d.issue_type] as number)??0)+1;m.set(day,r);});
 return [...m.values()].sort((a,b)=>String(a.day).localeCompare(String(b.day))).map(r=>{issues.forEach(k=>r[k]??=0);return r;});
}
