import { parseDecisions, type Decision } from './sample-decisions';

export type ImportedDecisions = { decisions: Decision[]; filename: string };
const decode = (bytes: Uint8Array) => new TextDecoder('utf-8').decode(bytes);

/** Read a ZIP central directory and extract the chosen JSONL file in-browser. */
async function extractZip(file: File): Promise<ImportedDecisions> {
  const bytes = new Uint8Array(await file.arrayBuffer());
  const view = new DataView(bytes.buffer);
  let eocd = -1;
  for (let i = bytes.length - 22; i >= Math.max(0, bytes.length - 65557); i--) {
    if (view.getUint32(i, true) === 0x06054b50) { eocd = i; break; }
  }
  if (eocd < 0) throw new Error('Invalid ZIP: end-of-directory record missing');
  const count = view.getUint16(eocd + 10, true);
  let pos = view.getUint32(eocd + 16, true);
  const entries: { name: string; method: number; offset: number; size: number }[] = [];
  for (let i = 0; i < count; i++) {
    if (view.getUint32(pos, true) !== 0x02014b50) throw new Error('Invalid ZIP directory');
    const method = view.getUint16(pos + 10, true);
    const size = view.getUint32(pos + 20, true);
    const nameLen = view.getUint16(pos + 28, true);
    const extraLen = view.getUint16(pos + 30, true);
    const commentLen = view.getUint16(pos + 32, true);
    const offset = view.getUint32(pos + 42, true);
    const name = decode(bytes.subarray(pos + 46, pos + 46 + nameLen));
    entries.push({ name, method, offset, size });
    pos += 46 + nameLen + extraLen + commentLen;
  }
  const candidates = entries.filter(e => /(^|\/)decisions(?:_holdout)?\.jsonl$/i.test(e.name));
  const selected = candidates.find(e => /(^|\/)decisions\.jsonl$/i.test(e.name)) ?? candidates[0];
  if (!selected) throw new Error('ZIP contains no decisions.jsonl or decisions_holdout.jsonl. Run the backend pipeline first.');
  const off = selected.offset;
  if (view.getUint32(off, true) !== 0x04034b50) throw new Error('Invalid ZIP entry');
  const start = off + 30 + view.getUint16(off + 26, true) + view.getUint16(off + 28, true);
  const compressed = bytes.slice(start, start + selected.size);
  let plain: Uint8Array;
  if (selected.method === 0) plain = compressed;
  else if (selected.method === 8) {
    try {
      const stream = new Blob([compressed]).stream().pipeThrough(new DecompressionStream('deflate-raw'));
      plain = new Uint8Array(await new Response(stream).arrayBuffer());
    } catch { throw new Error('Browser cannot decompress this ZIP. Extract decisions.jsonl and upload it directly.'); }
  } else throw new Error('Unsupported ZIP compression method. Extract decisions.jsonl and upload it directly.');
  return { decisions: parseDecisions(decode(plain)), filename: selected.name };
}
export async function importDecisions(file: File): Promise<ImportedDecisions> {
  if (/\.zip$/i.test(file.name)) return extractZip(file);
  return { decisions: parseDecisions((await file.text()).replace(/^\uFEFF/, '')), filename: file.name };
}
