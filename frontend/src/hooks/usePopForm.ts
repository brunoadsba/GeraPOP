import { useReducer } from 'react';
import type {
  CampoProcedimento,
  Definicao,
  PopData,
  Revisao,
  Secao,
} from '../types/pop';
import { defaultCampo, defaultDefinicao, emptyPop, emptyRevisao, defaultSecao } from '../types/pop';

export type Action =
  | { type: 'SET_FIELD'; field: keyof PopData; value: string }
  | { type: 'SET_DEFINICOES'; definicoes: Definicao[] }
  | { type: 'ADD_DEFINICAO' }
  | { type: 'REMOVE_DEFINICAO'; index: number }
  | { type: 'SET_SECOES'; secoes: Secao[] }
  | { type: 'ADD_SECAO' }
  | { type: 'REMOVE_SECAO'; index: number }
  | { type: 'ADD_PASSO'; secaoIndex: number }
  | { type: 'REMOVE_PASSO'; secaoIndex: number; passoIndex: number }
  | { type: 'ADD_CAMPO'; secaoIndex: number }
  | { type: 'REMOVE_CAMPO'; secaoIndex: number; campoIndex: number }
  | { type: 'SET_REGRAS'; regras: string[] }
  | { type: 'ADD_REGRA' }
  | { type: 'REMOVE_REGRA'; index: number }
  | { type: 'SET_REVISOES'; revisoes: Revisao[] }
  | { type: 'ADD_REVISAO' }
  | { type: 'REMOVE_REVISAO'; index: number }
  | { type: 'LOAD_POP'; pop: PopData }
  | { type: 'RESET' };

function updateSecao(secao: Secao, field: string, value: string): Secao {
  if (field === 'titulo') return { ...secao, titulo: value };
  return secao;
}

export function reducer(state: PopData, action: Action): PopData {
  switch (action.type) {
    case 'SET_FIELD':
      return { ...state, [action.field]: action.value };

    case 'SET_DEFINICOES':
      return { ...state, definicoes: action.definicoes };
    case 'ADD_DEFINICAO':
      return { ...state, definicoes: [...state.definicoes, defaultDefinicao()] };
    case 'REMOVE_DEFINICAO':
      return {
        ...state,
        definicoes:
          state.definicoes.length > 1
            ? state.definicoes.filter((_, i) => i !== action.index)
            : state.definicoes,
      };

    case 'SET_SECOES':
      return { ...state, secoes: action.secoes };
    case 'ADD_SECAO':
      return { ...state, secoes: [...state.secoes, defaultSecao()] };
    case 'REMOVE_SECAO':
      return {
        ...state,
        secoes:
          state.secoes.length > 1
            ? state.secoes.filter((_, i) => i !== action.index)
            : state.secoes,
      };

    case 'ADD_PASSO':
      return {
        ...state,
        secoes: state.secoes.map((secao, i) =>
          i === action.secaoIndex ? { ...secao, passos: [...secao.passos, ''] } : secao,
        ),
      };
    case 'REMOVE_PASSO':
      return {
        ...state,
        secoes: state.secoes.map((secao, i) =>
          i === action.secaoIndex && secao.passos.length > 1
            ? { ...secao, passos: secao.passos.filter((_, p) => p !== action.passoIndex) }
            : secao,
        ),
      };

    case 'ADD_CAMPO':
      return {
        ...state,
        secoes: state.secoes.map((secao, i) =>
          i === action.secaoIndex
            ? { ...secao, campos: [...secao.campos, defaultCampo()] }
            : secao,
        ),
      };
    case 'REMOVE_CAMPO':
      return {
        ...state,
        secoes: state.secoes.map((secao, i) =>
          i === action.secaoIndex && secao.campos.length > 1
            ? { ...secao, campos: secao.campos.filter((_, c) => c !== action.campoIndex) }
            : secao,
        ),
      };

    case 'SET_REGRAS':
      return { ...state, regras: action.regras };
    case 'ADD_REGRA':
      return { ...state, regras: [...state.regras, ''] };
    case 'REMOVE_REGRA':
      return {
        ...state,
        regras: state.regras.length > 1 ? state.regras.filter((_, i) => i !== action.index) : state.regras,
      };

    case 'SET_REVISOES':
      return { ...state, revisoes: action.revisoes };
    case 'ADD_REVISAO':
      return { ...state, revisoes: [...state.revisoes, emptyRevisao()] };
    case 'REMOVE_REVISAO':
      return {
        ...state,
        revisoes:
          state.revisoes.length > 1
            ? state.revisoes.filter((_, i) => i !== action.index)
            : state.revisoes,
      };

    case 'LOAD_POP':
      return normalizePop(action.pop);
    case 'RESET':
      return emptyPop();

    default:
      return state;
  }
}

function normalizePop(pop: PopData): PopData {
  const secoes = pop.secoes.map((secao) => ({
    ...secao,
    campos: secao.campos ?? [],
    passos: secao.passos?.length ? secao.passos : [''],
  }));
  return {
    ...pop,
    definicoes: pop.definicoes?.length ? pop.definicoes : [defaultDefinicao()],
    secoes: secoes.length ? secoes : [defaultSecao()],
    regras: pop.regras?.length ? pop.regras : [''],
    revisoes: pop.revisoes?.length ? pop.revisoes : [emptyRevisao()],
  };
}

export function setCampoValue(
  state: PopData,
  secaoIndex: number,
  campoIndex: number,
  field: keyof CampoProcedimento,
  value: string,
): PopData {
  return {
    ...state,
    secoes: state.secoes.map((secao, i) =>
      i === secaoIndex
        ? {
            ...secao,
            campos: secao.campos.map((campo, c) =>
              c === campoIndex ? { ...campo, [field]: value } : campo,
            ),
          }
        : secao,
    ),
  };
}

export function usePopForm() {
  return useReducer(reducer, undefined, emptyPop);
}

export { updateSecao };
