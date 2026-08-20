import type { Dispatch } from 'react';
import { Flag } from '../ui/Flag';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { IconHistory, IconPlus, IconTrash } from '../ui/Icons';
import type { Action } from '../../hooks/usePopForm';
import type { PopData, Revisao } from '../../types/pop';

interface IdentificacaoSectionProps {
  state: PopData;
  dispatch: Dispatch<Action>;
}

export function IdentificacaoSection({ state, dispatch }: IdentificacaoSectionProps) {
  const set = (field: keyof PopData) => (value: string) =>
    dispatch({ type: 'SET_FIELD', field, value });

  const updateRevisao = (index: number, field: keyof Revisao, value: string) => {
    dispatch({
      type: 'SET_REVISOES',
      revisoes: state.revisoes.map((revisao, i) =>
        i === index ? { ...revisao, [field]: value } : revisao,
      ),
    });
  };

  return (
    <section className="form-section identificacao-section">
      {/* Linha 1: Nome do POP e Aviso */}
      <div className="ident-row-top">
        <div className="ident-col-nome">
          <Flag required hint="Nome completo do procedimento — ex: Manobra de Atracação de Navio" />
          <Input
            label="Nome do POP"
            requiredFlag
            placeholder="Registro de Manobras no Sistema TOS – OpenPort"
            value={state.nome_pop}
            onChange={(e) => set('nome_pop')(e.target.value)}
          />
        </div>
        <div className="ident-col-aviso">
          <Flag hint="Alerta importante (opcional)" />
          <Input
            label="Aviso / Atenção (opcional)"
            placeholder="Ex: Somente com prático credenciado..."
            value={state.aviso}
            onChange={(e) => set('aviso')(e.target.value)}
          />
        </div>
      </div>

      {/* Linha 2: Metadados do POP (4 Colunas) */}
      <div className="ident-metadata-box">
        <div className="ident-meta-grid">
          <div>
            <Flag required hint="Código único" />
            <Input
              label="Código"
              requiredFlag
              placeholder="POP-OPE-XXX"
              value={state.codigo}
              onChange={(e) => set('codigo')(e.target.value)}
            />
          </div>
          <div>
            <Flag hint="Versão atual" />
            <Input
              label="Versão"
              placeholder="01"
              value={state.versao}
              onChange={(e) => set('versao')(e.target.value)}
            />
          </div>
          <div>
            <Flag hint="Data emissão" />
            <Input
              label="Data"
              placeholder="DD/MM/AAAA"
              value={state.data}
              onChange={(e) => set('data')(e.target.value)}
            />
          </div>
          <div>
            <Flag required hint="Setor" />
            <Input
              label="Área"
              requiredFlag
              placeholder="Operações Portuárias"
              value={state.area}
              onChange={(e) => set('area')(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Linha 3: Histórico de Revisões no Topo */}
      <div className="ident-revisoes-box">
        <div className="ident-revisoes-header">
          <span className="ident-revisoes-title">
            <IconHistory size={16} />
            Histórico de Revisões
          </span>
          <Button
            variant="ghost"
            size="sm"
            icon={<IconPlus size={13} />}
            onClick={() => dispatch({ type: 'ADD_REVISAO' })}
          >
            Adicionar revisão
          </Button>
        </div>

        <div className="ident-revisoes-list">
          {state.revisoes.length === 0 ? (
            <div className="revisoes-empty">
              <span>Nenhuma revisão cadastrada.</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => dispatch({ type: 'ADD_REVISAO' })}
              >
                + Adicionar revisão
              </Button>
            </div>
          ) : (
            state.revisoes.map((revisao, index) => (
              <div className="ident-revisao-row" key={index}>
                <div className="ident-rev-cell cell-rev">
                  <span className="ident-rev-label">Rev.</span>
                  <input
                    type="text"
                    className="input"
                    placeholder="01"
                    aria-label="Revisão"
                    value={revisao.revisao}
                    onChange={(e) => updateRevisao(index, 'revisao', e.target.value)}
                  />
                </div>
                <div className="ident-rev-cell cell-data">
                  <span className="ident-rev-label">Data</span>
                  <input
                    type="text"
                    className="input"
                    placeholder="DD/MM/AAAA"
                    aria-label="Data da revisão"
                    value={revisao.data}
                    onChange={(e) => updateRevisao(index, 'data', e.target.value)}
                  />
                </div>
                <div className="ident-rev-cell cell-desc">
                  <span className="ident-rev-label">Descrição</span>
                  <input
                    type="text"
                    className="input"
                    placeholder="Descrição da alteração (ex: Emissão inicial)"
                    aria-label="Descrição da revisão"
                    value={revisao.descricao}
                    onChange={(e) => updateRevisao(index, 'descricao', e.target.value)}
                  />
                </div>
                <div className="ident-rev-cell cell-resp">
                  <span className="ident-rev-label">Responsável</span>
                  <input
                    type="text"
                    className="input"
                    placeholder="Setor / Nome"
                    aria-label="Responsável pela revisão"
                    value={revisao.responsavel}
                    onChange={(e) => updateRevisao(index, 'responsavel', e.target.value)}
                  />
                </div>
                <div className="ident-rev-cell cell-del">
                  {state.revisoes.length > 1 ? (
                    <button
                      type="button"
                      className="btn-remove-rev-spacious"
                      title="Remover revisão"
                      onClick={() =>
                        dispatch({
                          type: 'SET_REVISOES',
                          revisoes: state.revisoes.filter((_, i) => i !== index),
                        })
                      }
                    >
                      <IconTrash size={15} />
                    </button>
                  ) : null}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </section>
  );
}
