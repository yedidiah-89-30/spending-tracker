'use client';

import { useState, useEffect } from 'react';
import { useDebounce } from '@/shared/hooks/useDebounce';
import { Input } from '@/shared/components/ui/Input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/components/ui/Select';
import { Button } from '@/shared/components/ui/Button';
import { INCOME_CATEGORIES } from '../types';
import { Search, X } from 'lucide-react';
import { cn } from '@/shared/lib/utils/format';

interface IncomeFiltersProps {
  onFilterChange: (filters: any) => void;
  className?: string;
}

export function IncomeFilters({ onFilterChange, className }: IncomeFiltersProps) {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const debouncedSearch = useDebounce(search, 500);

  useEffect(() => {
    const filters: any = {};
    if (debouncedSearch) filters.search = debouncedSearch;
    if (category && category !== 'all') filters.category = category;
    if (sortBy) filters.sortBy = sortBy;
    if (sortOrder) filters.sortOrder = sortOrder;
    onFilterChange(filters);
  }, [debouncedSearch, category, sortBy, sortOrder, onFilterChange]);

  const handleClear = () => {
    setSearch('');
    setCategory('all');
    setSortBy('date');
    setSortOrder('desc');
  };

  const hasFilters = search || (category && category !== 'all');

  return (
    <div className={cn('flex flex-col sm:flex-row gap-3', className)}>
      <div className="relative flex-1">
        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search income..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-8"
        />
      </div>

      <Select value={category} onValueChange={setCategory}>
        <SelectTrigger className="w-full sm:w-[180px]">
          <SelectValue placeholder="Category" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Categories</SelectItem>
          {INCOME_CATEGORIES.map((cat) => (
            <SelectItem key={cat} value={cat}>
              {cat}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select value={sortBy} onValueChange={setSortBy}>
        <SelectTrigger className="w-full sm:w-[140px]">
          <SelectValue placeholder="Sort by" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="date">Date</SelectItem>
          <SelectItem value="amount">Amount</SelectItem>
          <SelectItem value="source">Source</SelectItem>
        </SelectContent>
      </Select>

      <Select value={sortOrder} onValueChange={(value: 'asc' | 'desc') => setSortOrder(value)}>
        <SelectTrigger className="w-full sm:w-[120px]">
          <SelectValue placeholder="Order" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="desc">Descending</SelectItem>
          <SelectItem value="asc">Ascending</SelectItem>
        </SelectContent>
      </Select>

      {hasFilters && (
        <Button
          variant="ghost"
          size="icon"
          onClick={handleClear}
          className="shrink-0"
          aria-label="Clear filters"
        >
          <X className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
}
