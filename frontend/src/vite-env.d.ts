/// <reference types="vite/client" />

declare module 'node:path' {
  export function resolve(...paths: (string | undefined)[]): string;
  export function join(...paths: (string | undefined)[]): string;
  export function dirname(path: string): string;
  export function basename(path: string, ext?: string): string;
  const path: {
    resolve(...paths: (string | undefined)[]): string;
    join(...paths: (string | undefined)[]): string;
    dirname(path: string): string;
    basename(path: string, ext?: string): string;
  };
  export default path;
}

declare module 'node:fs' {
  export function rmSync(path: string, options?: { recursive?: boolean; force?: boolean }): void;
  export function existsSync(path: string): boolean;
  export function readFileSync(path: string, encoding?: string): string;
  export function writeFileSync(path: string, data: string | Uint8Array, encoding?: string): void;
  const fs: {
    rmSync(path: string, options?: { recursive?: boolean; force?: boolean }): void;
    existsSync(path: string): boolean;
    readFileSync(path: string, encoding?: string): string;
    writeFileSync(path: string, data: string | Uint8Array, encoding?: string): void;
  };
  export default fs;
}

declare namespace NodeJS {
  interface ProcessEnv {
    [key: string]: string | undefined;
  }
  interface Process {
    env: ProcessEnv;
  }
}

declare const process: NodeJS.Process;

interface ImportMeta {
  readonly dirname: string;
}