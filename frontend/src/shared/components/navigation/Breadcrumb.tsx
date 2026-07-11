'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/shared/lib/utils/format';
import { ChevronRight, Home } from 'lucide-react';

interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: React.ReactNode;
}

interface BreadcrumbProps {
  items?: BreadcrumbItem[];
  className?: string;
  homeLabel?: string;
}

export function Breadcrumb({ items, className, homeLabel = 'Home' }: BreadcrumbProps) {
  const pathname = usePathname();

  // Generate breadcrumb items from path if not provided
  const generatedItems = React.useMemo(() => {
    if (items) return items;

    const paths = pathname?.split('/').filter(Boolean) || [];
    const breadcrumbs: BreadcrumbItem[] = [];

    // Always include home
    breadcrumbs.push({
      label: homeLabel,
      href: '/',
      icon: <Home className="h-3 w-3" />,
    });

    // Build path segments
    let currentPath = '';
    paths.forEach((segment) => {
      currentPath += `/${segment}`;
      breadcrumbs.push({
        label: segment.charAt(0).toUpperCase() + segment.slice(1),
        href: currentPath,
      });
    });

    return breadcrumbs;
  }, [pathname, items, homeLabel]);

  return (
    <nav
      className={cn('flex items-center space-x-2 text-sm text-muted-foreground', className)}
      aria-label="Breadcrumb"
    >
      {generatedItems.map((item, index) => {
        const isLast = index === generatedItems.length - 1;

        return (
          <React.Fragment key={index}>
            {index > 0 && (
              <ChevronRight className="h-3 w-3 flex-shrink-0" aria-hidden="true" />
            )}
            {item.href && !isLast ? (
              <Link
                href={item.href}
                className="flex items-center gap-1 hover:text-foreground transition-colors"
              >
                {item.icon}
                <span>{item.label}</span>
              </Link>
            ) : (
              <span className="flex items-center gap-1 text-foreground font-medium">
                {item.icon}
                <span aria-current="page">{item.label}</span>
              </span>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
}