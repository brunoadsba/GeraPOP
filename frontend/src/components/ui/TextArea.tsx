import type { TextareaHTMLAttributes } from 'react';

interface TextAreaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  requiredFlag?: boolean;
}

export function TextArea({ label, requiredFlag, className = '', ...rest }: TextAreaProps) {
  return (
    <label className="field">
      {label ? (
        <span className="field-label">
          {label} {requiredFlag ? ' *' : ''}
        </span>
      ) : null}
      <textarea className={`textarea ${className}`.trim()} {...rest} />
    </label>
  );
}
