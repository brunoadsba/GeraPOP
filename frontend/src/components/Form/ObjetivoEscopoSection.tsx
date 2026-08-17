import type { Dispatch } from 'react';
import { Flag } from '../ui/Flag';
import { TextArea } from '../ui/TextArea';
import type { Action } from '../../hooks/usePopForm';
import type { PopData } from '../../types/pop';

interface ObjetivoEscopoSectionProps {
  state: PopData;
  dispatch: Dispatch<Action>;
}

export function ObjetivoEscopoSection({ state, dispatch }: ObjetivoEscopoSectionProps) {
  const set = (field: keyof PopData) => (value: string) =>
    dispatch({ type: 'SET_FIELD', field, value });

  return (
    <section className="form-section">
      <h2 className="section-title">Objetivo</h2>
      <Flag
        required
        hint="O que o procedimento padroniza — ex: Padronizar a manobra de atracação de navios"
      />
      <TextArea
        label="Descreva o objetivo do procedimento"
        requiredFlag
        rows={4}
        value={state.objetivo}
        onChange={(e) => set('objetivo')(e.target.value)}
      />

      <h2 className="section-title" style={{ marginTop: '1.4rem' }}>
        Escopo e Pré-condições
      </h2>
      <Flag hint="A quem se aplica e condições prévias — ex: Equipe de operações, práticos, rebocadores" />
      <TextArea
        label="A quem se aplica / condições prévias"
        rows={4}
        value={state.escopo}
        onChange={(e) => set('escopo')(e.target.value)}
      />
    </section>
  );
}
