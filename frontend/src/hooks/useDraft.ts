import { useCallback, useEffect, useRef, useState } from 'react';
import { clearDraft, getDraft, saveDraft } from '../api/client';
import type { DraftPayload, PopData } from '../types/pop';

const DEBOUNCE_MS = 2000;

export interface UseDraftOptions {
  state: PopData;
  loadedFromId?: string | null;
  enabled?: boolean;
}

export function useDraft({ state, loadedFromId, enabled = true }: UseDraftOptions) {
  const [isSaving, setIsSaving] = useState(false);
  const [lastSavedTime, setLastSavedTime] = useState<string | null>(null);

  const stateRef = useRef(state);
  const loadedFromIdRef = useRef(loadedFromId);
  const lastSavedStateStr = useRef<string>('');

  stateRef.current = state;
  loadedFromIdRef.current = loadedFromId;

  // On initial mount / enable, load existing draft
  useEffect(() => {
    if (!enabled) return;
    getDraft()
      .then((payload) => {
        if (payload?.form) {
          lastSavedStateStr.current = JSON.stringify(payload.form);
          document.dispatchEvent(
            new CustomEvent<DraftPayload>('gerapop:draft:loaded', { detail: payload }),
          );
        }
      })
      .catch(() => undefined);
  }, [enabled]);

  const saveNow = useCallback(async () => {
    if (!enabled) return;
    const currentStr = JSON.stringify(stateRef.current);
    setIsSaving(true);
    try {
      const payload: DraftPayload = {
        form: stateRef.current,
        loaded_from_id: loadedFromIdRef.current,
      };
      await saveDraft(payload);
      lastSavedStateStr.current = currentStr;
      setLastSavedTime(
        new Date().toLocaleTimeString('pt-BR', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        }),
      );
    } catch {
      // Ignore background save errors
    } finally {
      setIsSaving(false);
    }
  }, [enabled]);

  // Debounced auto-save ONLY when state actually changes
  useEffect(() => {
    if (!enabled) return;

    const currentStr = JSON.stringify(state);
    // Don't save if state hasn't changed since last save
    if (currentStr === lastSavedStateStr.current) return;

    const timer = setTimeout(() => {
      saveNow();
    }, DEBOUNCE_MS);

    return () => clearTimeout(timer);
  }, [state, loadedFromId, enabled, saveNow]);

  const discard = useCallback(() => {
    clearDraft().catch(() => undefined);
    lastSavedStateStr.current = '';
    setLastSavedTime(null);
  }, []);

  return { isSaving, lastSavedTime, saveNow, discard };
}
