import { FAQ, Transaction, TransactionType, Party, PaymentMethod } from './types';

export const WHATSAPP_NUMBER = "919876543210"; // Mock number

export const FAQS: FAQ[] = [
  {
    id: '1',
    question: 'How do I get access?',
    answer: 'Simply click "Try Now" to start chatting with Munimji on WhatsApp. No app download required.'
  },
  {
    id: '2',
    question: 'Is Munimji free?',
    answer: 'We offer a free tier for small businesses. Premium features include advanced reporting and multi-user support.'
  },
  {
    id: '3',
    question: 'How do I record sales or purchases?',
    answer: 'Just send a photo of the bill or type the details (e.g., "Sold 50kg rice to Ravi ₹2500") to our WhatsApp number.'
  },
  {
    id: '4',
    question: 'Can I export my records?',
    answer: 'Yes, you can export your ledgers and reports to PDF or Excel directly from the dashboard or via WhatsApp command.'
  }
];

export const MOCK_CUSTOMERS: Party[] = [
  { id: 'c1', name: 'Ravi Kumar', phone: '+91 98765 11111', totalVolume: 45000, balance: 2500, lastActive: '2023-10-27', status: 'ACTIVE' },
  { id: 'c2', name: 'Anjali Trade', phone: '+91 98765 22222', totalVolume: 120000, balance: 0, lastActive: '2023-10-29', status: 'ACTIVE' },
  { id: 'c3', name: 'Metro Hotel', phone: '+91 98765 33333', totalVolume: 8500, balance: 8500, lastActive: '2023-10-25', status: 'ACTIVE' },
  { id: 'c4', name: 'Local Cafe', phone: '+91 98765 44444', totalVolume: 3200, balance: 1200, lastActive: '2023-10-20', status: 'INACTIVE' },
];

export const MOCK_SUPPLIERS: Party[] = [
  { id: 's1', name: 'Sharma Suppliers', phone: '+91 88888 11111', totalVolume: 250000, balance: -15000, lastActive: '2023-10-26', status: 'ACTIVE' },
  { id: 's2', name: 'Gupta Wholesale', phone: '+91 88888 22222', totalVolume: 80000, balance: -5000, lastActive: '2023-10-22', status: 'ACTIVE' },
];

export const MOCK_TRANSACTIONS: Transaction[] = [
  { id: '1', date: '2023-10-24', partyName: 'Ravi Kumar', amount: 1200, type: TransactionType.UDHAAR_GIVEN, status: 'PENDING', note: 'Rice bags', paymentMethod: PaymentMethod.CASH, isReconciled: false },
  { id: '2', date: '2023-10-25', partyName: 'General Sales', amount: 5000, type: TransactionType.SALE, status: 'COMPLETED', note: 'Cash sales', paymentMethod: PaymentMethod.CASH, isReconciled: true },
  { id: '3', date: '2023-10-26', partyName: 'Sharma Suppliers', amount: 8500, type: TransactionType.PURCHASE, status: 'COMPLETED', note: 'Inventory restock', paymentMethod: PaymentMethod.BANK, isReconciled: true },
  { id: '4', date: '2023-10-26', partyName: 'Office Rent', amount: 15000, type: TransactionType.EXPENSE, status: 'COMPLETED', category: 'Rent', paymentMethod: PaymentMethod.BANK, isReconciled: true },
  { id: '5', date: '2023-10-27', partyName: 'Ravi Kumar', amount: 2500, type: TransactionType.SALE, status: 'COMPLETED', note: '50kg Rice', paymentMethod: PaymentMethod.UPI, isReconciled: true },
  { id: '6', date: '2023-10-28', partyName: 'Tea & Snacks', amount: 150, type: TransactionType.EXPENSE, status: 'COMPLETED', category: 'Refreshments', paymentMethod: PaymentMethod.CASH, isReconciled: true },
  { id: '7', date: '2023-10-29', partyName: 'Anjali Trade', amount: 4200, type: TransactionType.UDHAAR_RECEIVED, status: 'COMPLETED', note: 'Payment received', paymentMethod: PaymentMethod.UPI, isReconciled: true },
  { id: '8', date: '2023-10-29', partyName: 'Gupta Wholesale', amount: 5000, type: TransactionType.PAYMENT_OUT, status: 'COMPLETED', note: 'Part payment', paymentMethod: PaymentMethod.BANK, isReconciled: false },
  { id: '9', date: '2023-10-30', partyName: 'Metro Hotel', amount: 8500, type: TransactionType.UDHAAR_GIVEN, status: 'PENDING', note: 'Catering supply', paymentMethod: PaymentMethod.CASH, isReconciled: false },
  { id: '10', date: '2023-10-30', partyName: 'Petrol Pump', amount: 2000, type: TransactionType.EXPENSE, status: 'COMPLETED', category: 'Transport', paymentMethod: PaymentMethod.UPI, isReconciled: true },
];

export const CHART_DATA_WEEKLY = [
  { name: 'Mon', income: 4000, expense: 2400 },
  { name: 'Tue', income: 3000, expense: 1398 },
  { name: 'Wed', income: 2000, expense: 9800 },
  { name: 'Thu', income: 2780, expense: 3908 },
  { name: 'Fri', income: 1890, expense: 4800 },
  { name: 'Sat', income: 2390, expense: 3800 },
  { name: 'Sun', income: 3490, expense: 4300 },
];

export const DASHBOARD_STATS = {
  totalSales: 125000,
  totalPurchases: 85000,
  netPosition: 40000,
  outstandingUdhaar: 15000,
};

export const MOCK_EXPENSES = [
  { id: 1, date: '2023-10-22', category: 'Utilities', description: 'Electricity Bill', amount: 1500, reimbursed: false, isReimbursed: false },
  { id: 2, date: '2023-10-20', category: 'Transport', description: 'Auto fare for delivery', amount: 200, reimbursed: true, isReimbursed: true },
  { id: 3, date: '2023-10-18', category: 'Food', description: 'Staff lunch', amount: 450, reimbursed: false, isReimbursed: false },
];
