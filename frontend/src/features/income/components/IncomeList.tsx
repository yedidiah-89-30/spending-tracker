'use client';

import { useState } from 'react';
import { useIncome } from '../hooks/useIncome';
import { IncomeFilters } from './IncomeFilters';
import { IncomeForm } from './IncomeForm';
import { Button } from '@/shared/components/ui/Button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/shared/components/ui/Table';
import { Skeleton } from '@/shared/components/ui/Skeleton';
import { EmptyState } from '@/shared/components/feedback/EmptyState';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/shared/components/ui/Dialog';
import { Badge } from '@/shared/components/ui/Badge';
import { formatCurrency, formatDate } from '@/shared/lib/utils/format';
import { MoreHorizontal, Pencil, Trash2, Plus } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/shared/components/ui/DropdownMenu';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/shared/components/ui/AlertDialog';
import { INCOME_CATEGORIES } from '../types';

export function IncomeList() {
  const [filters, setFilters] = useState({});
  const [selectedIncome, setSelectedIncome] = useState<any>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [incomeToDelete, setIncomeToDelete] = useState<string | null>(null);

  const { data, total, isLoading, deleteIncome, isDeleting } = useIncome(filters);

  const handleDelete = async () => {
    if (incomeToDelete) {
      await deleteIncome(incomeToDelete);
      setIsDeleteDialogOpen(false);
      setIncomeToDelete(null);
    }
  };

  const handleEdit = (income: any) => {
    setSelectedIncome(income);
    setIsFormOpen(true);
  };

  const handleAdd = () => {
    setSelectedIncome(null);
    setIsFormOpen(true);
  };

  // Helper to get category label from value
  const getCategoryLabel = (value: string) => {
    const category = INCOME_CATEGORIES.find(c => c.value === value);
    return category ? category.label : value;
  };

  // Dialogs component to avoid duplication
  const Dialogs = () => (
    <>
      <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>
              {selectedIncome ? 'Edit Income' : 'Add Income'}
            </DialogTitle>
          </DialogHeader>
          <IncomeForm
            initialData={selectedIncome}
            onSuccess={() => {
              setIsFormOpen(false);
              setSelectedIncome(null);
            }}
            onCancel={() => {
              setIsFormOpen(false);
              setSelectedIncome(null);
            }}
          />
        </DialogContent>
      </Dialog>

      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the income record.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={isDeleting}
              className="bg-destructive hover:bg-destructive/90"
            >
              {isDeleting ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );

  // Render loading state
  if (isLoading) {
    return (
      <>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Skeleton className="h-8 w-40" />
            <Skeleton className="h-10 w-32" />
          </div>
          <div className="rounded-lg border border-border/50">
            <Table>
              <TableHeader>
                <TableRow>
                  {Array.from({ length: 6 }).map((_, i) => (
                    <TableHead key={i}>
                      <Skeleton className="h-4 w-20" />
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {Array.from({ length: 5 }).map((_, i) => (
                  <TableRow key={i}>
                    {Array.from({ length: 6 }).map((_, j) => (
                      <TableCell key={j}>
                        <Skeleton className="h-4 w-full" />
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
        <Dialogs />
      </>
    );
  }

  // Render empty state
  if (data.length === 0) {
    return (
      <>
        <EmptyState
          title="No income records"
          description="Start tracking your income by adding your first income record."
          action={
            <Button onClick={handleAdd}>
              <Plus className="h-4 w-4 mr-2" />
              Add Income
            </Button>
          }
        />
        <Dialogs />
      </>
    );
  }

  // Render main content with data
  return (
    <>
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold">Income</h2>
            <p className="text-sm text-muted-foreground">
              Total: {total} records
            </p>
          </div>
          <Button onClick={handleAdd}>
            <Plus className="h-4 w-4 mr-2" />
            Add Income
          </Button>
        </div>

        <IncomeFilters onFilterChange={setFilters} />

        <div className="rounded-lg border border-border/50 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Source</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((income) => (
                <TableRow key={income.id}>
                  <TableCell className="font-medium">{income.source}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">{getCategoryLabel(income.category)}</Badge>
                  </TableCell>
                  <TableCell className="font-semibold text-emerald-600 dark:text-emerald-400">
                    {formatCurrency(income.amount)}
                  </TableCell>
                  <TableCell>{formatDate(income.date)}</TableCell>
                  <TableCell>
                    {income.recurring ? (
                      <Badge variant="outline" className="border-primary text-primary">
                        Recurring
                      </Badge>
                    ) : (
                      <Badge variant="outline">One-time</Badge>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <MoreHorizontal className="h-4 w-4" />
                          <span className="sr-only">Open menu</span>
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleEdit(income)}>
                          <Pencil className="h-4 w-4 mr-2" />
                          Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => {
                            setIncomeToDelete(income.id);
                            setIsDeleteDialogOpen(true);
                          }}
                          className="text-destructive focus:text-destructive"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>
      <Dialogs />
    </>
  );
}