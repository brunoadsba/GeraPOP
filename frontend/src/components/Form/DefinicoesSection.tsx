import type { Dispatch } from 'react';
import { Flag } from '../ui/Flag';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { DynamicList } from './DynamicList';
import type { Action } from '../../hooks/usePopForm';
import type { Definicao, PopData } from '../../types/pop';

interface DefinicoesSectionProps {
  state: PopData;
  dispatch: Dispatch<Action>;
}

export function DefinicoesSection({ state, dispatch }: DefinicoesSectionProps) {
  const update = (index: number, field: keyof Definicao, value: string) => {
    dispatch({
      type: 'SET_DEFINICOES',
      definicoes: state.definicoes.map((item, i) =>
        i === index ? { ...item, [field]: value } : item,
      ),
    });
  };

  return (
    <section className="form-section">
      <h2 className="section-title">Definições</h2>
      <Flag required hint="Termos usados no POP e seus significados — ex: Prático → profissional que conduz a manobra" />
      <DynamicList addLabel="Adicionar termo" onAdd={() => dispatch({ type: 'ADD_DEFINICAO' })}>
        {state.definicoes.map((item, index) => (
          <div className="dynamic-item" key={index}>
            <div className="field-row">
              <Input
                placeholder="Termo"
                aria-label="Termo"
                value={item.termo}
                onChange={(e) => update(index, 'termo', e.target.value)}
              />
              <Input
                placeholder="Definição"
                aria-label="Definição"
                value={item.definicao}
                onChange={(e) => update(index, 'definicao', e.target.value)}
              />
            </div>
            <div className="dynamic-item-actions">
              <Button
                variant="ghost"
                size="sm"
                disabled={state.definicoes.length <= 1}
                onClick={() => dispatch({ type: 'REMOVE_DEFINICAO', index })}
              >
                Remover
              </Button>
            </div>
          </div>
        ))}
      </DynamicList>
    </section>
  );
}
