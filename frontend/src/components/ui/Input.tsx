import type { InputHTMLAttributes } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  hint?: string;
  requiredFlag?: boolean;
}

export function Input({ label, hint, requiredFlag, className = '', ...rest }: InputProps) {
  return (
    <label className="field">
      {label ? (
        <span className="field-label">
          {label} {requiredFlag ? ' *' : ''}
        </span>
      ) : null}
      <input className={`input ${className}`.trim()} {...rest} />
      {hint ? <span className="field-error">{hint}</span> : null}
    </label>
  );
}
