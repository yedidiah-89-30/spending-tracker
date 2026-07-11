export interface BaseEntity {
  id: string;
  createdAt: string;
  updatedAt: string;
}

export interface Option {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectOption {
  value: string;
  label: string;
}

export interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
  content?: React.ReactNode;
}

export interface Breadcrumb {
  label: string;
  href?: string;
  icon?: React.ReactNode;
}

export interface MenuItem {
  label: string;
  href?: string;
  icon?: React.ReactNode;
  onClick?: () => void;
  children?: MenuItem[];
  disabled?: boolean;
  divider?: boolean;
}

export type Status = 'idle' | 'loading' | 'success' | 'error';

export type Theme = 'light' | 'dark' | 'system';

export type Language = 'en' | 'es' | 'fr' | 'de' | 'ja' | 'zh';