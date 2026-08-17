export interface Definicao {
  termo: string;
  definicao: string;
}

export interface CampoProcedimento {
  campo: string;
  descricao: string;
}

export interface Secao {
  titulo: string;
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
  definicoes: Definicao[];
  secoes: Secao[];
  regras: string[];
  consulta: string;
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
