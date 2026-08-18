import { useEffect, useState } from 'react';
import type { Dispatch } from 'react';
import { Button } from '../ui/Button';
import { IconPlay, IconSquare, IconZap } from '../ui/Icons';
import type { Action } from '../../hooks/usePopForm';
import type { PopData } from '../../types/pop';

const SIM_EXEMPLO: PopData = {
  nome_pop: 'Manobra de Atracação de Navio',
  codigo: 'POP-MAN-001',
  versao: '02',
  data: '15/03/2026',
  area: 'Operações Portuárias',
  aviso:
    'Manobra de atracação somente com prático credenciado a bordo e rebocadores disponíveis.',
  objetivo:
    'Padronizar a manobra de atracação de navios no berço designado, garantindo segurança à tripulação, ao navio e à infraestrutura do terminal.',
  escopo:
    'Aplica-se à equipe de operações portuárias, práticos, rebocadores e conferentes envolvidos na manobra de atracação.',
  definicoes: [
    { termo: 'Prático', definicao: 'Profissional credenciado responsável por conduzir a manobra do navio.' },
    { termo: 'Rebocador', definicao: 'Embarcação de apoio usada para posicionar o navio durante a atracação.' },
    { termo: 'Berço', definicao: 'Local designado no cais onde o navio será atracado.' },
  ],
  secoes: [
    {
      titulo: 'Preparação da manobra',
      passos: [
        'Confirmar o horário de chegada (ETA) e a identificação do navio.',
        'Designar o berço de atracação conforme o plano de operação.',
        'Confirmar a disponibilidade de prático e rebocadores.',
      ],
      campos: [
        { campo: 'Data e Hora', descricao: 'Data e hora efetiva do início da manobra.' },
        { campo: 'Berço', descricao: 'Número do berço designado para a atracação.' },
        { campo: 'Prático', descricao: 'Nome do prático responsável pela manobra.' },
      ],
    },
    {
      titulo: 'Execução da atracação',
      passos: [
        'Conduzir o navio até o berço com apoio dos rebocadores.',
        'Posicionar o navio conforme o plano de manobra.',
        'Passar as amarras e fixar o navio ao cais.',
        'Confirmar a atracação e registrar o término da manobra.',
      ],
      campos: [{ campo: 'Rebocadores', descricao: 'Relação dos rebocadores utilizados na manobra.' }],
    },
  ],
  regras: [
    'Não iniciar a manobra sem prático credenciado a bordo.',
    'Manter comunicação de rádio contínua entre prático, rebocadores e coordenação.',
    'Parar a manobra imediatamente em caso de condição meteorológica adversa.',
  ],
  consulta: 'Menu > Operações > Manobras',
  revisoes: [
    { revisao: '02', data: '15/03/2026', descricao: 'Inclusão dos campos obrigatórios de registro da manobra.', responsavel: 'Operações Portuárias' },
    { revisao: '01', data: '10/01/2026', descricao: 'Emissão inicial.', responsavel: 'Operações Portuárias' },
  ],
};

const ROTULOS: (keyof PopData)[] = [
  'nome_pop',
  'codigo',
  'versao',
  'data',
  'area',
  'aviso',
  'objetivo',
  'escopo',
];

const ROTULO_LABEL: Record<keyof PopData, string> = {
  nome_pop: 'Nome do POP',
  codigo: 'Código',
  versao: 'Versão',
  data: 'Data de emissão',
  area: 'Área',
  aviso: 'Aviso / Atenção',
  objetivo: 'Objetivo',
  escopo: 'Escopo',
  consulta: 'Consulta',
  definicoes: 'Definições',
  secoes: 'Procedimento',
  regras: 'Regras',
  revisoes: 'Revisões',
};

export function Simulacao({ dispatch }: { dispatch: Dispatch<Action> }) {
  const [ativo, setAtivo] = useState(false);
  const [passo, setPasso] = useState(0);

  const passosTotais = ROTULOS.length + 4;

  useEffect(() => {
    if (!ativo) return;
    if (passo >= passosTotais) {
      setAtivo(false);
      setPasso(0);
      return;
    }
    if (passo < ROTULOS.length) {
      const campo = ROTULOS[passo];
      dispatch({ type: 'SET_FIELD', field: campo, value: SIM_EXEMPLO[campo] as string });
    } else if (passo === ROTULOS.length) {
      dispatch({ type: 'SET_DEFINICOES', definicoes: [...SIM_EXEMPLO.definicoes] });
    } else if (passo === ROTULOS.length + 1) {
      dispatch({ type: 'SET_SECOES', secoes: [...SIM_EXEMPLO.secoes] });
    } else if (passo === ROTULOS.length + 2) {
      dispatch({ type: 'SET_REGRAS', regras: [...SIM_EXEMPLO.regras] });
    } else if (passo === ROTULOS.length + 3) {
      dispatch({ type: 'SET_REVISOES', revisoes: [...SIM_EXEMPLO.revisoes] });
    }
    const timer = setTimeout(() => setPasso(passo + 1), 500);
    return () => clearTimeout(timer);
  }, [ativo, passo, dispatch, passosTotais]);

  const descricaoAtual = (idx: number): string => {
    if (idx < ROTULOS.length) {
      const campo = ROTULOS[idx];
      const valor = SIM_EXEMPLO[campo];
      return `${ROTULO_LABEL[campo]}: ${typeof valor === 'string' ? valor : ''}`;
    }
    if (idx === ROTULOS.length) return 'Definições: 3 itens';
    if (idx === ROTULOS.length + 1) return 'Procedimento: 2 seções';
    if (idx === ROTULOS.length + 2) return 'Regras: 3 itens';
    return 'Revisões: 2 itens';
  };

  const progresso = passosTotais ? Math.min(passo, passosTotais) / passosTotais : 0;

  return (
    <div className="sim-box">
      <div className="sim-title">
        <IconZap size={16} />
        Simulação de preenchimento (RPA)
      </div>
      {ativo ? (
        <>
          {passo < passosTotais ? (
            <div className="sim-caption">Preenchendo: {descricaoAtual(passo)}</div>
          ) : null}
          <div className="progress-track" role="progressbar" aria-valuenow={Math.round(progresso * 100)} aria-valuemin={0} aria-valuemax={100}>
            <div className="progress-fill" style={{ width: `${progresso * 100}%` }} />
          </div>
          <div className="progress-label">
            Campo {Math.min(passo + 1, passosTotais)} de {passosTotais}
          </div>
          <div style={{ marginTop: '0.6rem' }}>
            <Button variant="danger" size="sm" icon={<IconSquare size={12} />} onClick={() => { setAtivo(false); setPasso(0); }}>
              Parar simulação
            </Button>
          </div>
        </>
      ) : (
        <>
          <div className="sim-caption">
            Um robô preenche o formulário automaticamente, campo a campo, mostrando na prática
            como cada campo deve ser preenchido.
          </div>
          <Button variant="primary" icon={<IconPlay size={14} />} onClick={() => setAtivo(true)}>
            Iniciar simulação
          </Button>
        </>
      )}
    </div>
  );
}