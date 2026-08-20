export interface Definicao {
  termo: string;
  definicao: string;
}

export interface CampoProcedimento {
  campo: string;
  descricao: string;
}

export interface ItemMatriz {
  tela: string;
  nome_tela: string;
  etapa: string;
  responsavel: string;
  registro?: string;
  atividade?: string;
}

export interface RegistroObrigatorio {
  registro: string;
  conteudo: string;
  responsavel: string;
}

export interface Secao {
  titulo: string;
  responsavel?: string;
  responsaveis?: string[];
  passos: string[];
  campos: CampoProcedimento[];
}

export interface Revisao {
  revisao: string;
  data: string;
  descricao: string;
  responsavel: string;
}

export interface PopData {
  nome_pop: string;
  codigo: string;
  versao: string;
  data: string;
  area: string;
  aviso: string;
  objetivo: string;
  escopo: string;
  campo_aplicacao?: string;
  pre_condicoes?: string;
  elaborado_por?: string;
  elaborado_cargo?: string;
  aprovado_por?: string;
  aprovado_cargo?: string;
  definicoes: Definicao[];
  matriz_responsabilidades?: ItemMatriz[];
  secoes: Secao[];
  regras: string[];
  consulta: string;
  registros_obrigatorios?: RegistroObrigatorio[];
  criterios_encerramento?: string;
  indicadores?: string;
  aviso_final?: string;
  revisoes: Revisao[];
}

export interface PopListItem {
  id: string;
  created_at: string;
  status: string;
  codigo: string;
  nome_pop: string;
  filename: string;
}

export interface GenerateResult {
  pop_id: string;
  filename: string;
}

export interface DraftPayload {
  form: Partial<PopData>;
  loaded_from_id?: string | null;
}

export interface FluxoNo {
  id: string;
  etapa: number;
  rotulo: string;
  descricao: string;
  pop_ref?: string | null;
}

export interface FluxoLink {
  from: string;
  to: string;
}

export interface Fluxo {
  fluxo_id: string;
  titulo: string;
  descricao: string;
  nos: FluxoNo[];
  links: FluxoLink[];
}

export function defaultSecao(): Secao {
  return { titulo: '', passos: [''], campos: [] };
}

export function defaultDefinicao(): Definicao {
  return { termo: '', definicao: '' };
}

export function defaultCampo(): CampoProcedimento {
  return { campo: '', descricao: '' };
}

export function emptyRevisao(): Revisao {
  return { revisao: '', data: '', descricao: '', responsavel: '' };
}

export function todayBr(): string {
  return new Date().toLocaleDateString('pt-BR');
}

export function emptyPop(): PopData {
  return {
    nome_pop: '',
    codigo: '',
    versao: '01',
    data: todayBr(),
    area: '',
    aviso: '',
    objetivo: '',
    escopo: '',
    definicoes: [defaultDefinicao()],
    secoes: [defaultSecao()],
    regras: [''],
    consulta: '',
    revisoes: [
      {
        revisao: '01',
        data: todayBr(),
        descricao: 'Emissão inicial',
        responsavel: '',
      },
    ],
  };
}
