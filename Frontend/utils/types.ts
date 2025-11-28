export interface FAQ {
  id: string;
  question: string;
  answer: string;
}

export enum TransactionType {
  SALE = 'SALE',
  PURCHASE = 'PURCHASE',
  UDHAAR_GIVEN = 'UDHAAR_GIVEN',
  UDHAAR_RECEIVED = 'UDHAAR_RECEIVED',
  EXPENSE = 'EXPENSE',
  PAYMENT_OUT = 'PAYMENT_OUT',
  PAYMENT_IN = 'PAYMENT_IN'
}

export enum PaymentMethod {
  CASH = 'CASH',
  UPI = 'UPI',
  BANK = 'BANK'
}

export interface Transaction {
  id: string;
  date: string;
  partyName: string;
  amount: number;
  type: TransactionType;
  status: 'PENDING' | 'COMPLETED';
  note?: string;
  category?: string;
  paymentMethod: PaymentMethod;
  isReconciled: boolean;
}

export interface Party {
  id: string;
  name: string;
  phone: string;
  totalVolume: number;
  balance: number;
  lastActive: string;
  status: 'ACTIVE' | 'INACTIVE';
}
