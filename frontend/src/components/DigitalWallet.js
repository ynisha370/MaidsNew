import React, { useState, useEffect } from 'react';
import {
  Wallet,
  CreditCard,
  ArrowUpRight,
  ArrowDownLeft,
  Banknote,
  Smartphone,
  Building2,
  CheckCircle,
  AlertCircle,
  Clock,
  DollarSign,
  TrendingUp,
  Calendar,
  Download,
  Settings,
  Plus,
  Minus
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { toast } from 'sonner';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
const API = `${BACKEND_URL}/api`;

const DigitalWallet = () => {
  const { user } = useAuth();
  const [walletBalance, setWalletBalance] = useState(0);
  const [pendingBalance, setPendingBalance] = useState(0);
  const [transactions, setTransactions] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showWithdrawModal, setShowWithdrawModal] = useState(false);
  const [showAddPaymentModal, setShowAddPaymentModal] = useState(false);
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [withdrawMethod, setWithdrawMethod] = useState('');
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState('');

  useEffect(() => {
    loadWalletData();
  }, []);

  const loadWalletData = async () => {
    try {
      setLoading(true);

      // Load wallet balance and pending amounts
      const balanceResponse = await axios.get(`${API}/cleaner/wallet-balance`);
      setWalletBalance(balanceResponse.data.available || 0);
      setPendingBalance(balanceResponse.data.pending || 0);

      // Load transaction history
      const transactionsResponse = await axios.get(`${API}/cleaner/wallet-transactions`);
      setTransactions(transactionsResponse.data || []);

      // Load payment methods
      const paymentsResponse = await axios.get(`${API}/cleaner/payment-methods`);
      setPaymentMethods(paymentsResponse.data || []);

    } catch (error) {
      console.error('Failed to load wallet data:', error);
      toast.error('Failed to load wallet data');
    } finally {
      setLoading(false);
    }
  };

  const handleWithdraw = async () => {
    if (!withdrawAmount || !withdrawMethod) {
      toast.error('Please enter amount and select payment method');
      return;
    }

    const amount = parseFloat(withdrawAmount);
    if (amount <= 0 || amount > walletBalance) {
      toast.error('Invalid withdrawal amount');
      return;
    }

    try {
      await axios.post(`${API}/cleaner/withdraw`, {
        amount: amount,
        method: withdrawMethod,
        payment_method_id: selectedPaymentMethod
      });

      toast.success('Withdrawal request submitted successfully!');
      setShowWithdrawModal(false);
      setWithdrawAmount('');
      setWithdrawMethod('');
      loadWalletData(); // Refresh data
    } catch (error) {
      toast.error('Failed to submit withdrawal request');
    }
  };

  const handleAddPaymentMethod = async () => {
    if (!selectedPaymentMethod) {
      toast.error('Please select a payment method');
      return;
    }

    try {
      await axios.post(`${API}/cleaner/payment-methods`, {
        method: selectedPaymentMethod,
        // Additional fields would be collected based on method type
      });

      toast.success('Payment method added successfully!');
      setShowAddPaymentModal(false);
      setSelectedPaymentMethod('');
      loadWalletData(); // Refresh data
    } catch (error) {
      toast.error('Failed to add payment method');
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTransactionIcon = (type) => {
    switch (type) {
      case 'earning':
      case 'job_payment':
        return <ArrowDownLeft className="h-4 w-4 text-green-600" />;
      case 'withdrawal':
      case 'transfer':
        return <ArrowUpRight className="h-4 w-4 text-red-600" />;
      case 'refund':
        return <ArrowUpRight className="h-4 w-4 text-blue-600" />;
      default:
        return <DollarSign className="h-4 w-4 text-gray-600" />;
    }
  };

  const getTransactionColor = (type) => {
    switch (type) {
      case 'earning':
      case 'job_payment':
        return 'text-green-600';
      case 'withdrawal':
      case 'transfer':
        return 'text-red-600';
      case 'refund':
        return 'text-blue-600';
      default:
        return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="loading-spinner" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Wallet Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Wallet className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Available Balance</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {formatCurrency(walletBalance)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Clock className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Pending Clearance</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {formatCurrency(pendingBalance)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Withdrawn</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {formatCurrency(1200.00)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Actions */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Settings className="mr-2" size={20} />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button
                className="w-full"
                onClick={() => setShowWithdrawModal(true)}
                disabled={walletBalance <= 0}
              >
                <ArrowUpRight className="mr-2" size={16} />
                Withdraw Funds
              </Button>

              <Button
                variant="outline"
                className="w-full"
                onClick={() => setShowAddPaymentModal(true)}
              >
                <Plus className="mr-2" size={16} />
                Add Payment Method
              </Button>

              <Button variant="outline" className="w-full">
                <Download className="mr-2" size={16} />
                Download Statement
              </Button>
            </CardContent>
          </Card>

          {/* Payment Methods */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <CreditCard className="mr-2" size={20} />
                Payment Methods
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {paymentMethods.length === 0 ? (
                  <p className="text-sm text-gray-500 text-center py-4">
                    No payment methods added yet
                  </p>
                ) : (
                  paymentMethods.map((method) => (
                    <div key={method.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center">
                        {method.type === 'bank' && <Building2 className="h-5 w-5 text-gray-600 mr-3" />}
                        {method.type === 'card' && <CreditCard className="h-5 w-5 text-gray-600 mr-3" />}
                        {method.type === 'digital' && <Smartphone className="h-5 w-5 text-gray-600 mr-3" />}
                        <div>
                          <p className="font-medium text-sm">{method.name}</p>
                          <p className="text-xs text-gray-500">
                            {method.type === 'bank' ? 'Bank Account' :
                             method.type === 'card' ? 'Credit/Debit Card' : 'Digital Wallet'}
                          </p>
                        </div>
                      </div>
                      <Badge variant={method.is_default ? 'default' : 'outline'}>
                        {method.is_default ? 'Default' : 'Secondary'}
                      </Badge>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Transaction History */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Banknote className="mr-2" size={20} />
                Transaction History
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {transactions.length === 0 ? (
                  <div className="text-center py-8">
                    <Banknote className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No transactions yet</h3>
                    <p className="text-gray-500">Your transaction history will appear here</p>
                  </div>
                ) : (
                  transactions.map((transaction) => (
                    <div key={transaction.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center">
                        {getTransactionIcon(transaction.type)}
                        <div className="ml-3">
                          <p className="font-medium text-sm">{transaction.description}</p>
                          <p className="text-xs text-gray-500">{formatDate(transaction.created_at)}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className={`font-medium ${getTransactionColor(transaction.type)}`}>
                          {transaction.type === 'earning' || transaction.type === 'job_payment' ? '+' : '-'}
                          {formatCurrency(transaction.amount)}
                        </p>
                        <Badge className={getStatusColor(transaction.status)}>
                          {transaction.status}
                        </Badge>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Withdraw Funds Modal */}
      <Dialog open={showWithdrawModal} onOpenChange={setShowWithdrawModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Withdraw Funds</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Amount to Withdraw
              </label>
              <Input
                type="number"
                placeholder="0.00"
                value={withdrawAmount}
                onChange={(e) => setWithdrawAmount(e.target.value)}
                min="0"
                max={walletBalance}
                step="0.01"
              />
              <p className="text-sm text-gray-500 mt-1">
                Available: {formatCurrency(walletBalance)}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Payment Method
              </label>
              <Select value={withdrawMethod} onValueChange={setWithdrawMethod}>
                <SelectTrigger>
                  <SelectValue placeholder="Select payment method" />
                </SelectTrigger>
                <SelectContent>
                  {paymentMethods.map((method) => (
                    <SelectItem key={method.id} value={method.id}>
                      {method.name} ({method.type})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> Withdrawals are processed within 1-3 business days.
                A $2.50 processing fee applies to withdrawals under $100.
              </p>
            </div>

            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowWithdrawModal(false)}>
                Cancel
              </Button>
              <Button onClick={handleWithdraw} disabled={!withdrawAmount || !withdrawMethod}>
                Submit Withdrawal
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Add Payment Method Modal */}
      <Dialog open={showAddPaymentModal} onOpenChange={setShowAddPaymentModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Payment Method</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Payment Method Type
              </label>
              <Select value={selectedPaymentMethod} onValueChange={setSelectedPaymentMethod}>
                <SelectTrigger>
                  <SelectValue placeholder="Select payment method type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="bank">Bank Account</SelectItem>
                  <SelectItem value="card">Credit/Debit Card</SelectItem>
                  <SelectItem value="digital">Digital Wallet</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <p className="text-sm text-yellow-800">
                <strong>Security Note:</strong> Payment method information is encrypted and secure.
                We never store sensitive banking details.
              </p>
            </div>

            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowAddPaymentModal(false)}>
                Cancel
              </Button>
              <Button onClick={handleAddPaymentMethod} disabled={!selectedPaymentMethod}>
                Add Payment Method
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DigitalWallet;
