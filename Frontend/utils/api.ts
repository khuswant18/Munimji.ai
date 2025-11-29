// Frontend/utils/api.ts
import { getAuthToken } from './auth';

// Use environment variable or default to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

// Log API URL in development
if (import.meta.env.DEV) {
  console.log('🔗 API Base URL:', API_BASE_URL);
}

interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

// Generic API request handler
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const token = getAuthToken();
  
  console.log('API Request:', endpoint, 'Token:', token ? `${token.substring(0, 10)}...` : 'none');
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add authorization header if token exists
  if (token && !endpoint.includes('/auth/')) {
    headers['Authorization'] = `Bearer ${token}`;
    console.log('✅ Authorization header added');
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        error: data.detail || 'Request failed',
        status: response.status,
      };
    }

    return {
      data,
      status: response.status,
    };
  } catch (error) {
    console.error('API request failed:', error);
    return {
      error: error instanceof Error ? error.message : 'Network error',
      status: 0,
    };
  }
}

// ========== Auth API ==========
export interface LoginRequest {
  phone_number: string;
}

export interface LoginResponse {
  success: boolean;
  token: string;
  user: {
    id: number;
    phone_number: string;
    name?: string;
    shop_name?: string;
  };
}

export const authAPI = {
  login: (phone_number: string) =>
    apiRequest<LoginResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ phone_number }),
    }),

  logout: () =>
    apiRequest<{ success: boolean }>('/api/auth/logout', {
      method: 'POST',
    }),
};

// ========== Dashboard API ==========
export interface OverviewData {
  total_sales: number;
  total_purchases: number;
  total_expenses: number;
  net_income: number;
  outstanding_udhaar: number;
  recent_activity: LedgerEntryData[];
}

export interface LedgerEntryData {
  id: number;
  date?: string;
  type: string;
  amount: number;
  description?: string;
  counterparty_name?: string;
  counterparty_type?: string;
  source?: string;
}

export interface CustomerData {
  id: number;
  name: string;
  phone_number?: string;
  outstanding_balance: number;
  last_activity?: string;
}

export interface SupplierData {
  id: number;
  name: string;
  phone_number?: string;
  outstanding_balance: number;
  last_activity?: string;
}

export interface AddEntryRequest {
  type: string;
  amount: number;
  description?: string;
  counterparty_name?: string;
  counterparty_type?: string;
}

export interface UserProfile {
  id: number;
  phone_number: string;
  name?: string;
  shop_name?: string;
}

export const dashboardAPI = {
  getOverview: () => apiRequest<OverviewData>('/api/dashboard/overview'),

  getLedger: (limit: number = 50) =>
    apiRequest<LedgerEntryData[]>(`/api/dashboard/ledger?limit=${limit}`),

  getTransaction: (id: number) =>
    apiRequest<LedgerEntryData>(`/api/dashboard/transactions/${id}`),

  getCustomers: () => apiRequest<CustomerData[]>('/api/dashboard/customers'),

  getSuppliers: () => apiRequest<SupplierData[]>('/api/dashboard/suppliers'),

  getUdhaar: () => apiRequest<LedgerEntryData[]>('/api/dashboard/udhaar'),

  getCashbook: () => apiRequest<LedgerEntryData[]>('/api/dashboard/cashbook'),

  getExpenses: () => apiRequest<LedgerEntryData[]>('/api/dashboard/expenses'),

  getReports: () => apiRequest<any>('/api/dashboard/reports'),

  addEntry: (entry: AddEntryRequest) =>
    apiRequest<{ success: boolean; id: number }>('/api/dashboard/add-entry', {
      method: 'POST',
      body: JSON.stringify(entry),
    }),

  getProfile: () => apiRequest<UserProfile>('/api/me'),

  updateProfile: (data: { name?: string; shop_name?: string; preferred_language?: string }) =>
    apiRequest<{ success: boolean; user: UserProfile }>('/api/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
};

export default {
  auth: authAPI,
  dashboard: dashboardAPI,
};
