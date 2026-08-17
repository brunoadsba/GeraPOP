import type { Dispatch } from 'react';
import { Flag } from '../ui/Flag';
import { TextArea } from '../ui/TextArea';
import type { Action } from '../../hooks/usePopForm';
import type { PopData } from '../../types/pop';

interface ConsultaSectionProps {
  state: PopData;
  dispatch: Dispatch<Action>;
}

export function ConsultaSection({ state, dispatch }: ConsultaSectionProps) {
  return (
    <section className="form-section">
      <h2 className="section-title">Consulta e Relatórios</h2>
      <Flag hint="Onde o registro é consultado — ex: Menu > Operações > Manobras" />
      <TextArea
        label="Caminho / menu para consulta (opcional)"
        rows={3}
        value={state.consulta}
        onChange={(e) => dispatch({ type: 'SET_FIELD', field: 'consulta', value: e.target.value })}
      />
    </section>
  );
}
