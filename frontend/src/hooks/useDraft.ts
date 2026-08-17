import { useEffect, useRef } from 'react';
import { clearDraft, getDraft, saveDraft } from '../api/client';
import type { DraftPayload, PopData } from '../types/pop';

const DEBOUNCE_MS = 2000;

export interface UseDraftOptions {
  state: PopData;
  loadedFromId?: string | null;
  enabled?: boolean;
}

export function useDraft({ state, loadedFromId, enabled = true }: UseDraftOptions) {
  const firstRender = useRef(true);

  useEffect(() => {
    if (!enabled) return;
    getDraft()
      .then((payload) => {
        if (payload?.form) {
          document.dispatchEvent(
            new CustomEvent<DraftPayload>('gerapop:draft:loaded', { detail: payload }),
          );
        }
      })
      .catch(() => undefined);
  }, [enabled]);

  useEffect(() => {
    if (!enabled) return;
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }
    const timer = setTimeout(() => {
      const payload: DraftPayload = { form: state, loaded_from_id: loadedFromId };
      saveDraft(payload).catch(() => undefined);
    }, DEBOUNCE_MS);
    return () => clearTimeout(timer);
  }, [state, loadedFromId, enabled]);

  const discard = () => clearDraft().catch(() => undefined);

  return { discard };
}
