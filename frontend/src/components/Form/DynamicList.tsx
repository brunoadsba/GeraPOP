import type { ReactNode } from 'react';
import { Button } from '../ui/Button';

interface DynamicListProps {
  addLabel: string;
  onAdd: () => void;
  children: ReactNode;
}

export function DynamicList({ addLabel, onAdd, children }: DynamicListProps) {
  return (
    <div>
      <div>{children}</div>
      <Button variant="ghost" onClick={onAdd} className="add-btn">
        + {addLabel}
      </Button>
    </div>
  );
}
