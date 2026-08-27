import { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { listPops } from '../../api/client';
import { useTheme } from '../../hooks/useTheme';
import {
  IconChevronLeft,
  IconChevronRight,
  IconFolder,
  IconHome,
  IconMoon,
  IconPlus,
  IconSun,
  IconX,
} from '../ui/Icons';

export function Sidebar() {
  const { isDark, toggle } = useTheme();
  const [totalPops, setTotalPops] = useState<number | null>(null);
  const [collapsed, setCollapsed] = useState(() => {
    try {
      return localStorage.getItem('gerapop:sidebar:collapsed') === '1';
    } catch {
      return false;
    }
  });
  const [mobileOpen, setMobileOpen] = useState(false);
  const logo = isDark ? '/logo-codeba-branca.png' : '/logo-codeba.png';

  useEffect(() => {
    listPops()
      .then((records) => setTotalPops(records.length))
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem('gerapop:sidebar:collapsed', collapsed ? '1' : '0');
    } catch {
    }
  }, [collapsed]);

  useEffect(() => {
    const onResize = () => {
      if (window.innerWidth > 900) setMobileOpen(false);
    };
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  return (
    <>
      <button
        className="sidebar-mobile-toggle"
        aria-label={mobileOpen ? 'Fechar navegação' : 'Abrir navegação'}
        aria-expanded={mobileOpen}
        onClick={() => setMobileOpen((v) => !v)}
      >
        {mobileOpen ? <IconX size={18} /> : <IconFolder size={18} />}
      </button>
      <aside className={`sidebar ${collapsed ? 'collapsed' : ''} ${mobileOpen ? 'mobile-open' : ''}`}>
        <div className="sidebar-logo">
          <img src={logo} alt="CODEBA" className="sidebar-logo-wordmark" />
          <div className="sidebar-logo-mark" aria-hidden="true">
            <span className="sidebar-logo-mark-inner">C</span>
          </div>
          <button
            className="sidebar-collapse-btn"
            aria-label={collapsed ? 'Expandir sidebar' : 'Recolher sidebar'}
            aria-expanded={!collapsed}
            onClick={() => setCollapsed((v) => !v)}
            title={collapsed ? 'Expandir' : 'Recolher'}
          >
            {collapsed ? <IconChevronRight size={16} /> : <IconChevronLeft size={16} />}
          </button>
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
          state={{ novo_pop: { nome: '', objetivo: '' } }}
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
      {mobileOpen && <div className="sidebar-overlay" onClick={() => setMobileOpen(false)} aria-hidden="true" />}
    </>
  );
}
