import type { ReactNode } from 'react';

interface CardProps {
  title?: ReactNode;
  caption?: ReactNode;
  chip?: ReactNode;
  actions?: ReactNode;
  children?: ReactNode;
}

export function Card({ title, caption, chip, actions, children }: CardProps) {
  return (
    <div className="card">
      {title ? (
        <div className="card-head">
          <div>
            <div className="card-title">
              {title}
              {chip}
            </div>
            {caption ? <div className="card-caption">{caption}</div> : null}
          </div>
        </div>
      ) : null}
      {children}
      {actions ? <div className="card-actions">{actions}</div> : null}
    </div>
  );
}
