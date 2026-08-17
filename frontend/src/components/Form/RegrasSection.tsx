import type { Dispatch } from 'react';
import { Flag } from '../ui/Flag';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { DynamicList } from './DynamicList';
import type { Action } from '../../hooks/usePopForm';
import type { PopData } from '../../types/pop';

interface RegrasSectionProps {
  state: PopData;
  dispatch: Dispatch<Action>;
}

export function RegrasSection({ state, dispatch }: RegrasSectionProps) {
  const update = (index: number, value: string) => {
    dispatch({
      type: 'SET_REGRAS',
      regras: state.regras.map((regra, i) => (i === index ? value : regra)),
    });
  };

  return (
    <section className="form-section">
      <h2 className="section-title">Regras e Restrições</h2>
      <Flag hint="Regras que não podem ser quebradas — ex: Não iniciar sem prático a bordo" />
      <DynamicList addLabel="Adicionar regra" onAdd={() => dispatch({ type: 'ADD_REGRA' })}>
        {state.regras.map((regra, index) => (
          <div className="dynamic-item" key={index}>
            <Input
              placeholder="Regra"
              aria-label={`Regra ${index + 1}`}
              value={regra}
              onChange={(e) => update(index, e.target.value)}
            />
            <div className="dynamic-item-actions">
              <Button
                variant="ghost"
                size="sm"
                disabled={state.regras.length <= 1}
                onClick={() => dispatch({ type: 'REMOVE_REGRA', index })}
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
