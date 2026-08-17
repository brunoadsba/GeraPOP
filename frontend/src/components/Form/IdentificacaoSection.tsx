import type { Dispatch } from 'react';
import { Flag } from '../ui/Flag';
import { Input } from '../ui/Input';
import type { Action } from '../../hooks/usePopForm';
import type { PopData } from '../../types/pop';

interface IdentificacaoSectionProps {
  state: PopData;
  dispatch: Dispatch<Action>;
}

export function IdentificacaoSection({ state, dispatch }: IdentificacaoSectionProps) {
  const set = (field: keyof PopData) => (value: string) =>
    dispatch({ type: 'SET_FIELD', field, value });

  return (
    <section className="form-section">
      <h2 className="section-title">Identificação</h2>
      <div className="field-row">
        <div>
          <Flag required hint="Nome completo do procedimento — ex: Manobra de Atracação de Navio" />
          <Input
            label="Nome do POP"
            requiredFlag
            placeholder="Registro de Manobras no Sistema TOS – OpenPort"
            value={state.nome_pop}
            onChange={(e) => set('nome_pop')(e.target.value)}
          />
        </div>
        <div>
          <Flag required hint="Código único do POP — ex: POP-MAN-001" />
          <Input
            label="Código"
            requiredFlag
            placeholder="POP-OPE-XXX"
            value={state.codigo}
            onChange={(e) => set('codigo')(e.target.value)}
          />
        </div>
      </div>
      <div className="field-row">
        <div>
          <Flag hint="Número da versão — ex: 01, 02" />
          <Input
            label="Versão"
            value={state.versao}
            onChange={(e) => set('versao')(e.target.value)}
          />
        </div>
        <div>
          <Flag hint="Setor responsável — ex: Operações Portuárias" />
          <Input
            label="Área"
            requiredFlag
            placeholder="Operações Portuárias"
            value={state.area}
            onChange={(e) => set('area')(e.target.value)}
          />
        </div>
        <div>
          <Flag hint="Data de emissão — usa a data de hoje" />
          <Input label="Data" value={state.data} onChange={(e) => set('data')(e.target.value)} />
        </div>
      </div>
      <Flag hint="Alerta importante — ex: Somente com prático credenciado a bordo" />
      <Input
        label="Aviso / Atenção (opcional)"
        placeholder="Ex: Este POP não contempla..."
        value={state.aviso}
        onChange={(e) => set('aviso')(e.target.value)}
      />
    </section>
  );
}
