import type {
  DraftPayload,
  Fluxo,
  GenerateResult,
  PopData,
  PopListItem,
} from '../types/pop';

const BASE = import.meta.env.VITE_API_URL || '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, init);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail =
      body?.detail ?? body?.errors ?? (body?.detail as string) ?? 'Erro desconhecido';
    const message = Array.isArray(detail) ? detail.join(' • ') : String(detail ?? '');
    throw new ApiError(response.status, message);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

function blobRequest(path: string, init?: RequestInit): Promise<Blob> {
  return fetch(`${BASE}${path}`, init).then((response) => {
    if (!response.ok) {
      throw new ApiError(response.status, 'Falha ao baixar o arquivo');
    }
    return response.blob();
  });
}

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export function listPops(): Promise<PopListItem[]> {
  return request<PopListItem[]>('/pops');
}

export function getPop(id: string): Promise<PopData> {
  return request<PopData>(`/pops/${id}`);
}

export function deletePop(id: string): Promise<void> {
  return request<void>(`/pops/${id}`, { method: 'DELETE' });
}

export function validatePop(data: PopData): Promise<string[]> {
  return request<{ errors: string[] }>('/pops/validate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }).then((body) => body.errors);
}

export function checkCode(
  codigo: string,
  allowedIds: string[] = [],
): Promise<PopListItem | null> {
  return request<PopListItem | null>('/pops/check-code', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ codigo, allowed_ids: allowedIds }),
  });
}

export function generatePop(data: PopData, allowedIds: string[] = []): Promise<GenerateResult> {
  const query = allowedIds.length
    ? `?allowed_ids=${allowedIds.map(encodeURIComponent).join(',')}`
    : '';
  return request<GenerateResult>(`/generate${query}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
}

export function downloadDocx(popId: string): Promise<Blob> {
  return blobRequest(`/generate/${popId}/docx`);
}

export function downloadPdf(popId: string): Promise<Blob> {
  return blobRequest(`/generate/${popId}/pdf`);
}

export function previewDocx(data: PopData): Promise<Blob> {
  return blobRequest('/generate/preview/docx', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
}

export function previewPdf(data: PopData): Promise<Blob> {
  return blobRequest('/generate/preview/pdf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
}

export function getDraft(): Promise<DraftPayload | null> {
  return request<DraftPayload | null>('/draft');
}

export function saveDraft(payload: DraftPayload): Promise<void> {
  return request<void>('/draft', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export function clearDraft(): Promise<void> {
  return request<void>('/draft', { method: 'DELETE' });
}

export function downloadBackup(): Promise<Blob> {
  return blobRequest('/backup');
}

export function getFluxo(): Promise<Fluxo | null> {
  return request<Fluxo | null>('/pops/fluxo');
}

export function getFluxoPop(ref: string): Promise<PopData | null> {
  return request<PopData | null>(`/pops/fluxo/${ref}`);
}

export function attachPop(codigo: string, nome: string, file: File): Promise<{ id: string; codigo: string; nome_pop: string }> {
  const form = new FormData();
  form.append('codigo', codigo);
  form.append('nome', nome);
  form.append('file', file);
  return request<{ id: string; codigo: string; nome_pop: string }>('/pops/attach', {
    method: 'POST',
    body: form,
  });
}

export function triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}
