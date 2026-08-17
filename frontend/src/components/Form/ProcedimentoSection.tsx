import type { Dispatch } from 'react';
import { Flag } from '../ui/Flag';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import type { Action } from '../../hooks/usePopForm';
import type { CampoProcedimento, PopData } from '../../types/pop';

interface ProcedimentoSectionProps {
  state: PopData;
  dispatch: Dispatch<Action>;
}

export function ProcedimentoSection({ state, dispatch }: ProcedimentoSectionProps) {
  const setTitulo = (secaoIndex: number, value: string) => {
    dispatch({
      type: 'SET_SECOES',
      secoes: state.secoes.map((secao, i) =>
        i === secaoIndex ? { ...secao, titulo: value } : secao,
      ),
    });
  };

  const setPasso = (secaoIndex: number, passoIndex: number, value: string) => {
    dispatch({
      type: 'SET_SECOES',
      secoes: state.secoes.map((secao, i) =>
        i === secaoIndex
          ? { ...secao, passos: secao.passos.map((p, pi) => (pi === passoIndex ? value : p)) }
          : secao,
      ),
    });
  };

  const setCampo = (
    secaoIndex: number,
    campoIndex: number,
    field: keyof CampoProcedimento,
    value: string,
  ) => {
    dispatch({
      type: 'SET_SECOES',
      secoes: state.secoes.map((secao, i) =>
        i === secaoIndex
          ? {
              ...secao,
              campos: secao.campos.map((campo, ci) =>
                ci === campoIndex ? { ...campo, [field]: value } : campo,
              ),
            }
          : secao,
      ),
    });
  };

  return (
    <section className="form-section">
      <h2 className="section-title">Procedimento</h2>
      {state.secoes.map((secao, secaoIndex) => (
        <div className="secao-block" key={secaoIndex}>
          <div className="secao-block-header">
            <span className="secao-block-title">Seção {secaoIndex + 1}</span>
            {state.secoes.length > 1 ? (
              <Button
                variant="danger"
                size="sm"
                onClick={() => dispatch({ type: 'REMOVE_SECAO', index: secaoIndex })}
              >
                Remover seção
              </Button>
            ) : null}
          </div>

          <Flag required hint="Título da etapa — ex: Preparação da manobra" />
          <Input
            placeholder="Ex: Procedimento – Atracação"
            aria-label="Título da seção"
            value={secao.titulo}
            onChange={(e) => setTitulo(secaoIndex, e.target.value)}
          />

          <Flag required hint="Ações na ordem em que acontecem — ex: Confirmar o horário de chegada (ETA)" />
          {secao.passos.map((passo, passoIndex) => (
            <div className="dynamic-item" key={passoIndex}>
              <div className="field-row">
                <Input
                  placeholder={`Passo ${passoIndex + 1}`}
                  aria-label={`Passo ${passoIndex + 1}`}
                  value={passo}
                  onChange={(e) => setPasso(secaoIndex, passoIndex, e.target.value)}
                />
              </div>
              <div className="dynamic-item-actions">
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={secao.passos.length <= 1}
                  onClick={() =>
                    dispatch({ type: 'REMOVE_PASSO', secaoIndex, passoIndex })
                  }
                >
                  Remover
                </Button>
              </div>
            </div>
          ))}
          <Button
            variant="ghost"
            className="add-btn"
            onClick={() => dispatch({ type: 'ADD_PASSO', secaoIndex })}
          >
            + Adicionar passo
          </Button>

          <div style={{ marginTop: '1rem' }}>
            <Flag hint="Campos de registro da etapa — ex: Berço → número do berço designado" />
            {secao.campos.map((campo, campoIndex) => (
              <div className="dynamic-item" key={campoIndex}>
                <div className="field-row">
                  <Input
                    placeholder="Campo"
                    aria-label="Campo"
                    value={campo.campo}
                    onChange={(e) => setCampo(secaoIndex, campoIndex, 'campo', e.target.value)}
                  />
                  <Input
                    placeholder="Descrição / Instruções"
                    aria-label="Descrição do campo"
                    value={campo.descricao}
                    onChange={(e) =>
                      setCampo(secaoIndex, campoIndex, 'descricao', e.target.value)
                    }
                  />
                </div>
                <div className="dynamic-item-actions">
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={secao.campos.length <= 1}
                    onClick={() =>
                      dispatch({ type: 'REMOVE_CAMPO', secaoIndex, campoIndex })
                    }
                  >
                    Remover
                  </Button>
                </div>
              </div>
            ))}
            <Button
              variant="ghost"
              className="add-btn"
              onClick={() => dispatch({ type: 'ADD_CAMPO', secaoIndex })}
            >
              + Adicionar campo
            </Button>
          </div>
        </div>
      ))}
      <Button
        variant="ghost"
        className="add-btn"
        onClick={() => dispatch({ type: 'ADD_SECAO' })}
      >
        + Adicionar seção
      </Button>
    </section>
  );
}
