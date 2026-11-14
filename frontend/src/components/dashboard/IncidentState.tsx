import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { parseDecisions, type Decision } from "@/lib/sample-decisions";
import { importDecisions } from "@/lib/import-decisions";

export type ExecutionRecord = { event_id: string; status: string; reason?: string; missing_requirements?: string[]; verification?: {status?:string; details?:string} };
export type VerificationRecord = {event_id:string;status:string;note?:string};
type IncidentState = {
 verificationById: Record<string,VerificationRecord>;
 executionById: Record<string, ExecutionRecord>;
 id: string; setId: (id: string) => void; d: Decision | undefined; decisions: Decision[];
 loading: boolean; error: string | null; source: string;
 loadFile: (file: File) => Promise<void>; reload: () => Promise<void>;
 approved: Record<string, boolean>; consent: Record<string, boolean>;
 setApproval: (id: string, value: boolean) => void; setConsent: (id: string, value: boolean) => void;
};
const IncidentContext = createContext<IncidentState | null>(null);
const STORAGE_KEY = "plato40-decisions-v3";
const DATA_URL = import.meta.env.VITE_DECISIONS_URL || "/decisions.jsonl";
/** Read-only replay viewer. Approvals and consent are local simulations, never sent to backend. */
export function IncidentProvider({children}: {children: ReactNode}) {
 const [decisions,setDecisions]=useState<Decision[]>([]);
 const [verificationById,setVerificationById]=useState<Record<string,VerificationRecord>>({});
 const [executionById,setExecutionById]=useState<Record<string,ExecutionRecord>>({});
 const [id,setId]=useState("");
 const [approved,setApproved]=useState<Record<string,boolean>>({});
 const [consent,setConsent]=useState<Record<string,boolean>>({});
 const [loading,setLoading]=useState(true);
 const [error,setError]=useState<string|null>(null);
 const [source,setSource]=useState("No data loaded");
 const apply=(rows: Decision[], name:string)=>{if(!rows.length)throw new Error("No decisions found in the file");setDecisions(rows);setId(rows[0]?.event_id??"");setApproved({});setConsent({});setSource(name);setError(null);};
 const reload=async()=>{setLoading(true);try{const response=await fetch(DATA_URL,{cache:"no-store"});if(!response.ok)throw new Error(`Could not fetch ${DATA_URL} (HTTP ${response.status})`);apply(parseDecisions(await response.text()),DATA_URL);try{const logResponse=await fetch("/execution_log.jsonl",{cache:"no-store"});if(logResponse.ok){const logs=(await logResponse.text()).split(/\r?\n/).filter(Boolean).map(line=>JSON.parse(line) as ExecutionRecord);setExecutionById(Object.fromEntries(logs.map(log=>[log.event_id,log])));}else setExecutionById({});}catch{setExecutionById({});}
 try{const v=await fetch("/verification.jsonl",{cache:"no-store"});if(v.ok){const records=(await v.text()).split(/\r?\n/).filter(Boolean).map(x=>JSON.parse(x) as VerificationRecord);setVerificationById(Object.fromEntries(records.map(x=>[x.event_id,x])));}else setVerificationById({});}catch{setVerificationById({});}
 }catch(e){setError(e instanceof Error?e.message:String(e));}finally{setLoading(false);}};
 const loadFile=async(file:File)=>{setLoading(true);try{const result=await importDecisions(file);apply(result.decisions, `${file.name} → ${result.filename}`);setExecutionById({});try{localStorage.setItem(STORAGE_KEY,JSON.stringify({rows:result.decisions,name:`${file.name} → ${result.filename}`}));}catch{setError("Loaded successfully, but too large to remember after refresh. Re-upload when needed.");}}catch(e){setError(e instanceof Error?e.message:String(e));}finally{setLoading(false);}};
 useEffect(()=>{try{const saved=localStorage.getItem(STORAGE_KEY);if(saved){const {rows,name}=JSON.parse(saved);apply(parseDecisions(JSON.stringify(rows)),name);setLoading(false);return;}}catch{localStorage.removeItem(STORAGE_KEY);}void reload();},[]);
 return <IncidentContext.Provider value={{verificationById,executionById,id,setId,d:decisions.find(x=>x.event_id===id),decisions,loading,error,source,loadFile,reload,approved,consent,setApproval:(k,v)=>setApproved(p=>({...p,[k]:v})),setConsent:(k,v)=>setConsent(p=>({...p,[k]:v}))}}>{children}</IncidentContext.Provider>;
}
export function useIncidentState(){const context=useContext(IncidentContext);if(!context)throw new Error("Incident state must be used within IncidentProvider");return context;}
