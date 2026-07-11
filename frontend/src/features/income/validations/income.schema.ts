import { z } from 'zod';
import { INCOME_CATEGORIES } from '../types';

export const incomeSchema = z.object({
  amount: z.number({
    required_error: 'Amount is required',
    invalid_type_error: 'Amount must be a number',
  })
    .positive('Amount must be greater than 0')
    .min(0.01, 'Amount must be at least 0.01')
    .max(999999999.99, 'Amount is too large'),
  source: z.string()
    .min(2, 'Source must be at least 2 characters')
    .max(100, 'Source must be less than 100 characters')
    .trim(),
  category: z.enum(INCOME_CATEGORIES as [string, ...string[]], {
    required_error: 'Category is required',
  }),
  date: z.string({
    required_error: 'Date is required',
  }).regex(/^\d{4}-\d{2}-\d{2}$/, 'Invalid date format'),
  description: z.string()
    .max(500, 'Description must be less than 500 characters')
    .optional()
    .nullable()
    .transform(val => val?.trim() || undefined),
  recurring: z.boolean().default(false),
});

export type IncomeFormData = z.infer<typeof incomeSchema>;
