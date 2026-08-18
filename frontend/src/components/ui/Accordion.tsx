import { useState } from 'react';
import type { ReactNode } from 'react';
import { IconChevronDown } from './Icons';

interface AccordionProps {
  title: ReactNode;
  /** Extra content rendered to the right of the title (e.g. a badge) */
  badge?: ReactNode;
  defaultOpen?: boolean;
  children: ReactNode;
  className?: string;
}

export function Accordion({
  title,
  badge,
  defaultOpen = true,
  children,
  className = '',
}: AccordionProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className={`accordion ${open ? 'accordion-open' : ''} ${className}`.trim()}>
      <button
        type="button"
        className="accordion-trigger"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
      >
        <span className="accordion-chevron">
          <IconChevronDown size={16} />
        </span>
        <span className="accordion-label">{title}</span>
        {badge ? <span className="accordion-badge">{badge}</span> : null}
      </button>
      <div className="accordion-panel" aria-hidden={!open}>
        <div className="accordion-content">{children}</div>
      </div>
    </div>
  );
}
