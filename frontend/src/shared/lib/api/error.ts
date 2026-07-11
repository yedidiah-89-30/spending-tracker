import { ERROR_MESSAGES, HTTP_STATUS } from '@/shared/lib/utils/constants';

export class APIError extends Error {
  public status: number;
  public code: string;
  public details?: any;

  constructor(message: string, status: number = HTTP_STATUS.INTERNAL_SERVER_ERROR, code: string = 'UNKNOWN_ERROR', details?: any) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export class NetworkError extends Error {
  constructor(message: string = ERROR_MESSAGES.NETWORK_ERROR) {
    super(message);
    this.name = 'NetworkError';
  }
}

export class ValidationError extends Error {
  public errors: Record<string, string[]>;

  constructor(errors: Record<string, string[]>, message: string = ERROR_MESSAGES.VALIDATION_ERROR) {
    super(message);
    this.name = 'ValidationError';
    this.errors = errors;
  }
}

export const handleAPIError = (error: any): APIError | NetworkError => {
  if (error.response) {
    const { status, data } = error.response;
    
    switch (status) {
      case HTTP_STATUS.BAD_REQUEST:
        return new APIError(
          data.message || ERROR_MESSAGES.VALIDATION_ERROR,
          status,
          data.code || 'VALIDATION_ERROR',
          data.details
        );
      case HTTP_STATUS.UNAUTHORIZED:
        return new APIError(
          ERROR_MESSAGES.UNAUTHORIZED,
          status,
          'UNAUTHORIZED'
        );
      case HTTP_STATUS.FORBIDDEN:
        return new APIError(
          ERROR_MESSAGES.FORBIDDEN,
          status,
          'FORBIDDEN'
        );
      case HTTP_STATUS.NOT_FOUND:
        return new APIError(
          ERROR_MESSAGES.NOT_FOUND,
          status,
          'NOT_FOUND'
        );
      case HTTP_STATUS.TOO_MANY_REQUESTS:
        return new APIError(
          'Too many requests. Please try again later.',
          status,
          'TOO_MANY_REQUESTS'
        );
      case HTTP_STATUS.INTERNAL_SERVER_ERROR:
        return new APIError(
          ERROR_MESSAGES.SERVER_ERROR,
          status,
          'SERVER_ERROR'
        );
      default:
        return new APIError(
          data.message || ERROR_MESSAGES.UNKNOWN_ERROR,
          status,
          data.code || 'UNKNOWN_ERROR',
          data.details
        );
    }
  }
  
  if (error.request) {
    return new NetworkError();
  }
  
  return new APIError(ERROR_MESSAGES.UNKNOWN_ERROR);
};

export const getErrorMessage = (error: unknown): string => {
  if (error instanceof APIError) {
    return error.message;
  }
  if (error instanceof NetworkError) {
    return error.message;
  }
  if (error instanceof ValidationError) {
    const firstError = Object.values(error.errors).flat()[0];
    return firstError || error.message;
  }
  return ERROR_MESSAGES.UNKNOWN_ERROR;
};