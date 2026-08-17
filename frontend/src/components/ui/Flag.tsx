import type { ReactNode } from 'react';

interface FlagProps {
  required?: boolean;
  hint?: string;
  children?: ReactNode;
}

export function Flag({ required, hint }: FlagProps) {
  return (
    <div className="flag-row">
      <span className={`flag ${required ? 'flag-req' : 'flag-opt'}`}>
        {required ? 'OBRIGATÓRIO' : 'OPCIONAL'}
      </span>
      {hint ? <span className="flag-hint">{hint}</span> : null}
    </div>
  );
}
