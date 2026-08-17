import type { ReactNode } from 'react';

interface CardGridProps {
  children: ReactNode;
}

export function CardGrid({ children }: CardGridProps) {
  return <div className="dash-grid">{children}</div>;
}
