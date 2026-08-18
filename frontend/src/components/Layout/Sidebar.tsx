import { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { listPops } from '../../api/client';
import { useTheme } from '../../hooks/useTheme';
import {
  IconFolder,
  IconHome,
  IconMoon,
  IconPlus,
  IconSun,
  IconTarget,
} from '../ui/Icons';

export function Sidebar() {
  const { isDark, toggle } = useTheme();
  const [totalPops, setTotalPops] = useState<number | null>(null);
  const logo = isDark ? '/logo-codeba-branca.png' : '/logo-codeba.png';

  useEffect(() => {
    listPops()
      .then((records) => setTotalPops(records.length))
      .catch(() => undefined);
  }, []);

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <img src={logo} alt="CODEBA" />
      </div>
      <nav className="sidebar-nav" aria-label="Navegação principal">
        <div className="sidebar-section-title">Visão Geral</div>
        <NavLink to="/" end className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
          <span className="nav-link-icon" aria-hidden="true">
            <IconHome size={18} />
          </span>
          <span className="nav-link-label">Início</span>
        </NavLink>
        <NavLink
          to="/fluxo"
          className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
        >
          <span className="nav-link-icon" aria-hidden="true">
            <IconTarget size={18} />
          </span>
          <span className="nav-link-label">Fluxo SEV</span>
        </NavLink>
        <NavLink
          to="/pops"
          className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
        >
          <span className="nav-link-icon" aria-hidden="true">
            <IconFolder size={18} />
          </span>
          <span className="nav-link-label">Meus POPs</span>
          {totalPops !== null && totalPops > 0 ? (
            <span className="nav-link-badge">{totalPops}</span>
          ) : null}
        </NavLink>

        <div className="sidebar-section-title">Criação</div>
        <NavLink
          to="/formulario"
          className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
        >
          <span className="nav-link-icon" aria-hidden="true">
            <IconPlus size={18} />
          </span>
          <span className="nav-link-label">Novo POP</span>
        </NavLink>
      </nav>
      <div className="sidebar-footer">
        <button
          className="theme-toggle"
          onClick={toggle}
          aria-pressed={isDark}
          title="Alternar tema claro/escuro"
        >
          {isDark ? <IconSun size={15} /> : <IconMoon size={15} />}
          {isDark ? 'Tema claro' : 'Tema escuro'}
        </button>
        <span className="sidebar-version">GeraPOP v1.2</span>
      </div>
    </aside>
  );
}
