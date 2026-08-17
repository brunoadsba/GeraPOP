import type { Dispatch } from 'react';
import { Flag } from '../ui/Flag';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { DynamicList } from './DynamicList';
import type { Action } from '../../hooks/usePopForm';
import type { PopData, Revisao } from '../../types/pop';

interface RevisoesSectionProps {
  state: PopData;
  dispatch: Dispatch<Action>;
}

export function RevisoesSection({ state, dispatch }: RevisoesSectionProps) {
  const update = (index: number, field: keyof Revisao, value: string) => {
    dispatch({
      type: 'SET_REVISOES',
      revisoes: state.revisoes.map((revisao, i) =>
        i === index ? { ...revisao, [field]: value } : revisao,
      ),
    });
  };

  return (
    <section className="form-section">
      <h2 className="section-title">Histórico de Revisões</h2>
      <Flag hint="Versões anteriores do POP — ex: 02 → 15/03/2026 → Inclusão dos campos obrigatórios" />
      <DynamicList addLabel="Adicionar revisão" onAdd={() => dispatch({ type: 'ADD_REVISAO' })}>
        {state.revisoes.map((revisao, index) => (
          <div className="dynamic-item" key={index}>
            <div className="field-row">
              <Input
                placeholder="Rev."
                aria-label="Revisão"
                value={revisao.revisao}
                onChange={(e) => update(index, 'revisao', e.target.value)}
              />
              <Input
                placeholder="Data"
                aria-label="Data"
                value={revisao.data}
                onChange={(e) => update(index, 'data', e.target.value)}
              />
            </div>
            <div className="field-row">
              <Input
                placeholder="Descrição"
                aria-label="Descrição"
                value={revisao.descricao}
                onChange={(e) => update(index, 'descricao', e.target.value)}
              />
              <Input
                placeholder="Responsável"
                aria-label="Responsável"
                value={revisao.responsavel}
                onChange={(e) => update(index, 'responsavel', e.target.value)}
              />
            </div>
            <div className="dynamic-item-actions">
              <Button
                variant="ghost"
                size="sm"
                disabled={state.revisoes.length <= 1}
                onClick={() => dispatch({ type: 'REMOVE_REVISAO', index })}
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