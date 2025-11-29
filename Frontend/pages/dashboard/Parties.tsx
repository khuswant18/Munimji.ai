import React, { useState, useEffect } from 'react';
import { Phone, MessageCircle, Search, FileText, Loader2 } from 'lucide-react';
import { dashboardAPI, CustomerData, SupplierData, LedgerEntryData } from '../../utils/api';
import LedgerTable from '../../components/LedgerTable';
import { Transaction, TransactionType, PaymentMethod } from '../../utils/types';

interface PartiesProps {
  type: 'CUSTOMER' | 'SUPPLIER';
  data?: any[]; // Legacy prop, not used anymore
}

const Parties: React.FC<PartiesProps> = ({ type }) => {
  const [parties, setParties] = useState<(CustomerData | SupplierData)[]>([]);
  const [selectedParty, setSelectedParty] = useState<(CustomerData | SupplierData) | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [ledgerData, setLedgerData] = useState<LedgerEntryData[]>([]);
  const [loadingLedger, setLoadingLedger] = useState(false);

  useEffect(() => {
    loadParties();
  }, [type]);

  useEffect(() => {
    if (selectedParty) {
      loadPartyLedger();
    }
  }, [selectedParty]);

  const loadParties = async () => {
    setLoading(true);
    const response = type === 'CUSTOMER' 
      ? await dashboardAPI.getCustomers()
      : await dashboardAPI.getSuppliers();
    
    setLoading(false);

    if (response.data) {
      setParties(response.data);
      if (response.data.length > 0) {
        setSelectedParty(response.data[0]);
      }
    }
  };

  const loadPartyLedger = async () => {
    if (!selectedParty) return;
    
    setLoadingLedger(true);
    const response = await dashboardAPI.getLedger(100);
    setLoadingLedger(false);

    if (response.data) {
      // Filter ledger entries for selected party
      const filtered = response.data.filter(
        entry => entry.counterparty_name === selectedParty.name
      );
      setLedgerData(filtered);
    }
  };

  const filteredData = parties.filter(p => 
    p.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Convert API ledger entries to Transaction format for LedgerTable
  const partyTransactions: Transaction[] = ledgerData.map(entry => ({
    id: entry.id.toString(),
    date: entry.date || 'N/A',
    partyName: entry.counterparty_name || 'Unknown',
    amount: entry.amount,
    type: entry.type.toUpperCase() as TransactionType,
    status: 'COMPLETED' as const,
    note: entry.description,
    paymentMethod: (entry.source?.toUpperCase() as PaymentMethod) || PaymentMethod.CASH,
    isReconciled: true,
  }));

  const handleReminder = (phone: string | undefined, name: string, balance: number) => {
    if (!phone) {
      alert('Phone number not available');
      return;
    }
    const cleanPhone = phone.replace(/\D/g, '');
    window.open(
      `https://wa.me/${cleanPhone}?text=Hi ${name}, gentle reminder regarding the pending payment of ₹${balance}`, 
      '_blank'
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="animate-spin text-[#006A4E]" size={40} />
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-140px)] font-manrope">
      {/* Left List */}
      <div className="lg:col-span-4 bg-white rounded-3xl shadow-soft border border-slate-100 flex flex-col overflow-hidden">
        <div className="p-6 border-b border-slate-50">
           <h2 className="text-xl font-bold text-slate-800 mb-4">{type === 'CUSTOMER' ? 'Customers' : 'Suppliers'}</h2>
           <div className="relative">
             <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
             <input 
               type="text" 
               placeholder="Search name..." 
               value={searchTerm}
               onChange={(e) => setSearchTerm(e.target.value)}
               className="w-full pl-10 pr-4 py-2 bg-slate-50 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-[#006A4E]/20"
             />
           </div>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1 custom-scrollbar">
          {filteredData.map(party => (
            <div 
              key={party.id}
              onClick={() => setSelectedParty(party)}
              className={`p-4 rounded-2xl cursor-pointer transition-all ${selectedParty?.id === party.id ? 'bg-[#006A4E]/5 border-[#006A4E]/20 shadow-sm' : 'hover:bg-slate-50 border border-transparent'}`}
            >
              <div className="flex justify-between items-start mb-1">
                <h4 className={`font-bold text-sm ${selectedParty?.id === party.id ? 'text-[#0F172A]' : 'text-slate-700'}`}>{party.name}</h4>
                <span className={`text-xs font-bold ${party.outstanding_balance > 0 ? 'text-green-600' : party.outstanding_balance < 0 ? 'text-red-500' : 'text-slate-400'}`}>
                  {party.outstanding_balance > 0 ? '+' : ''}₹{Math.abs(party.outstanding_balance).toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between items-center text-xs text-slate-400">
                <span>Last: {party.last_activity || 'N/A'}</span>
                <span className={`px-2 py-0.5 rounded-full text-[10px] ${party.outstanding_balance !== 0 ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                  {party.outstanding_balance !== 0 ? 'ACTIVE' : 'SETTLED'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right Details */}
      <div className="lg:col-span-8 flex flex-col h-full overflow-hidden">
         {selectedParty ? (
           <>
             {/* Header Card */}
             <div className="bg-white rounded-3xl p-6 shadow-soft border border-slate-100 mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 bg-gradient-to-br from-[#006A4E] to-[#004D38] rounded-2xl flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-[#006A4E]/30">
                    {selectedParty.name.charAt(0)}
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-slate-800">{selectedParty.name}</h2>
                    <p className="text-slate-500 text-sm flex items-center gap-2">
                      <Phone size={14} /> {selectedParty.phone_number || 'No phone'}
                    </p>
                  </div>
                </div>
                <div className="flex gap-3 w-full md:w-auto">
                   <button 
                    onClick={() => handleReminder(selectedParty.phone_number, selectedParty.name, selectedParty.outstanding_balance)}
                    className="flex-1 md:flex-none flex items-center justify-center gap-2 bg-green-50 text-green-700 hover:bg-green-100 px-4 py-2.5 rounded-xl font-bold text-sm transition-colors"
                   >
                     <MessageCircle size={18} /> {type === 'CUSTOMER' ? 'Remind' : 'Message'}
                   </button>
                   <button className="flex-1 md:flex-none flex items-center justify-center gap-2 bg-slate-50 text-slate-600 hover:bg-slate-100 px-4 py-2.5 rounded-xl font-bold text-sm transition-colors">
                     <FileText size={18} /> Statement
                   </button>
                </div>
             </div>
             
             {/* Transactions Table Wrapper */}
             <div className="flex-1 overflow-hidden flex flex-col">
                {loadingLedger ? (
                  <div className="flex items-center justify-center h-64">
                    <Loader2 className="animate-spin text-[#006A4E]" size={32} />
                  </div>
                ) : (
                  <LedgerTable transactions={partyTransactions} title={`Ledger with ${selectedParty.name}`} />
                )}
             </div>
           </>
         ) : (
           <div className="h-full flex items-center justify-center text-slate-400">Select a party to view details</div>
         )}
      </div>
    </div>
  );
};

export default Parties;
