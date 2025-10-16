import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  Users, 
  Mail, 
  Phone, 
  Calendar, 
  Home, 
  CheckCircle, 
  XCircle, 
  Edit, 
  Trash2,
  RefreshCw,
  Filter,
  Search
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Textarea } from './ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const WaitlistManagement = () => {
  const [waitlist, setWaitlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [editNotes, setEditNotes] = useState('');
  const [editStatus, setEditStatus] = useState('');

  useEffect(() => {
    loadWaitlist();
  }, []);

  const loadWaitlist = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/waitlist`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setWaitlist(response.data || []);
    } catch (error) {
      console.error('Failed to load waitlist:', error);
      toast.error('Failed to load waitlist');
    } finally {
      setLoading(false);
    }
  };

  const updateWaitlistEntry = async (entryId, status, notes) => {
    try {
      const token = localStorage.getItem('token');
      await axios.patch(`${API}/waitlist/${entryId}`, 
        { status, notes },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Waitlist entry updated successfully');
      loadWaitlist();
      setShowEditDialog(false);
    } catch (error) {
      console.error('Failed to update waitlist entry:', error);
      toast.error('Failed to update waitlist entry');
    }
  };

  const removeFromWaitlist = async (entryId) => {
    if (!window.confirm('Are you sure you want to remove this entry from the waitlist?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/waitlist/${entryId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Entry removed from waitlist');
      loadWaitlist();
    } catch (error) {
      console.error('Failed to remove from waitlist:', error);
      toast.error('Failed to remove from waitlist');
    }
  };

  const handleEdit = (entry) => {
    setSelectedEntry(entry);
    setEditStatus(entry.status);
    setEditNotes(entry.notes || '');
    setShowEditDialog(true);
  };

  const handleSaveEdit = () => {
    if (selectedEntry) {
      updateWaitlistEntry(selectedEntry.id, editStatus, editNotes);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      waiting: { color: 'bg-yellow-100 text-yellow-800', label: 'Waiting' },
      contacted: { color: 'bg-blue-100 text-blue-800', label: 'Contacted' },
      scheduled: { color: 'bg-green-100 text-green-800', label: 'Scheduled' },
      expired: { color: 'bg-gray-100 text-gray-800', label: 'Expired' }
    };
    
    const config = statusConfig[status] || statusConfig.waiting;
    return <Badge className={config.color}>{config.label}</Badge>;
  };

  const filteredWaitlist = waitlist.filter(entry => {
    const matchesStatus = filterStatus === 'all' || entry.status === filterStatus;
    const matchesSearch = searchTerm === '' || 
      entry.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.email.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading waitlist...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Waitlist Management</h2>
          <p className="text-gray-600">Manage customer waitlist entries and capacity</p>
        </div>
        <Button onClick={loadWaitlist} variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Entries</p>
                <p className="text-2xl font-bold">{waitlist.length}</p>
              </div>
              <Users className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Waiting</p>
                <p className="text-2xl font-bold">
                  {waitlist.filter(e => e.status === 'waiting').length}
                </p>
              </div>
              <Clock className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Contacted</p>
                <p className="text-2xl font-bold">
                  {waitlist.filter(e => e.status === 'contacted').length}
                </p>
              </div>
              <Mail className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Scheduled</p>
                <p className="text-2xl font-bold">
                  {waitlist.filter(e => e.status === 'scheduled').length}
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search by name or email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="w-full md:w-48">
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger>
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="waiting">Waiting</SelectItem>
                  <SelectItem value="contacted">Contacted</SelectItem>
                  <SelectItem value="scheduled">Scheduled</SelectItem>
                  <SelectItem value="expired">Expired</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Waitlist Entries */}
      <div className="space-y-4">
        {filteredWaitlist.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No waitlist entries</h3>
              <p className="text-gray-600">No entries match your current filters.</p>
            </CardContent>
          </Card>
        ) : (
          filteredWaitlist.map((entry) => (
            <Card key={entry.id}>
              <CardContent className="p-6">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-semibold">
                        {entry.first_name} {entry.last_name}
                      </h3>
                      {getStatusBadge(entry.status)}
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-gray-600">
                      <div className="flex items-center">
                        <Mail className="h-4 w-4 mr-2" />
                        {entry.email}
                      </div>
                      {entry.phone && (
                        <div className="flex items-center">
                          <Phone className="h-4 w-4 mr-2" />
                          {entry.phone}
                        </div>
                      )}
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 mr-2" />
                        {entry.address?.preferred_date ? new Date(entry.address.preferred_date).toLocaleDateString() : 'N/A'}
                      </div>
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-2" />
                        {entry.preferred_time_slot}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-3 text-sm">
                      <div>
                        <span className="font-medium">Frequency:</span> {entry.preferred_frequency}
                      </div>
                      <div>
                        <span className="font-medium">House Size:</span> {entry.house_size}
                      </div>
                      <div>
                        <span className="font-medium">Zip Code:</span> {entry.address?.zip_code || 'N/A'}
                      </div>
                    </div>
                    
                    {entry.notes && (
                      <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                        <p className="text-sm text-gray-700">
                          <span className="font-medium">Notes:</span> {entry.notes}
                        </p>
                      </div>
                    )}
                    
                    <div className="mt-3 text-xs text-gray-500">
                      Added: {new Date(entry.created_at).toLocaleString()}
                    </div>
                  </div>
                  
                  <div className="flex space-x-2 ml-4">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleEdit(entry)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => removeFromWaitlist(entry.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Edit Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Waitlist Entry</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <Select value={editStatus} onValueChange={setEditStatus}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="waiting">Waiting</SelectItem>
                  <SelectItem value="contacted">Contacted</SelectItem>
                  <SelectItem value="scheduled">Scheduled</SelectItem>
                  <SelectItem value="expired">Expired</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Notes
              </label>
              <Textarea
                value={editNotes}
                onChange={(e) => setEditNotes(e.target.value)}
                placeholder="Add notes about this waitlist entry..."
                rows={3}
              />
            </div>
            
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowEditDialog(false)}>
                Cancel
              </Button>
              <Button onClick={handleSaveEdit}>
                Save Changes
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default WaitlistManagement;
