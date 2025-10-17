import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  Calendar, 
  Clock, 
  User, 
  Phone, 
  Mail, 
  MapPin, 
  AlertCircle, 
  CheckCircle,
  Users,
  Filter,
  Search,
  RefreshCw,
  Eye,
  UserCheck
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const JobAssignmentManager = () => {
  const [pendingBookings, setPendingBookings] = useState([]);
  const [cleaners, setCleaners] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  const [filters, setFilters] = useState({
    date: '',
    timeSlot: '',
    search: ''
  });

  useEffect(() => {
    loadData();
  }, [filters]);

  const loadData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadPendingBookings(),
        loadCleaners()
      ]);
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const loadPendingBookings = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.date) params.append('date', filters.date);
      if (filters.timeSlot) params.append('time_slot', filters.timeSlot);
      
      const response = await axios.get(`${API}/admin/bookings/pending-assignment?${params}`);
      setPendingBookings(response.data.pending_bookings || []);
    } catch (error) {
      console.error('Failed to load pending bookings:', error);
      toast.error('Failed to load pending bookings');
    }
  };

  const loadCleaners = async () => {
    try {
      const response = await axios.get(`${API}/admin/cleaners`);
      setCleaners(response.data || []);
    } catch (error) {
      console.error('Failed to load cleaners:', error);
      toast.error('Failed to load cleaners');
    }
  };

  const assignCleaner = async (bookingId, cleanerId) => {
    try {
      await axios.post(`${API}/admin/bookings/${bookingId}/assign-cleaner`, {
        cleaner_id: cleanerId
      });
      
      toast.success('Cleaner assigned successfully');
      loadPendingBookings(); // Refresh the list
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to assign cleaner';
      toast.error(message);
    }
  };

  const getStatusBadge = (status) => {
    const statusColors = {
      pending: 'bg-yellow-100 text-yellow-800',
      confirmed: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-purple-100 text-purple-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800'
    };
    
    return (
      <Badge className={`${statusColors[status] || 'bg-gray-100 text-gray-800'} border-0`}>
        {status?.charAt(0).toUpperCase() + status?.slice(1)}
      </Badge>
    );
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const filteredBookings = pendingBookings.filter(booking => {
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      return (
        booking.customer_name.toLowerCase().includes(searchTerm) ||
        booking.customer_email.toLowerCase().includes(searchTerm) ||
        booking.id.toLowerCase().includes(searchTerm)
      );
    }
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Job Assignment Manager</h1>
        <Button onClick={loadData} variant="outline" className="flex items-center gap-2">
          <RefreshCw className="h-4 w-4" />
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <Label htmlFor="date">Date</Label>
              <Input
                id="date"
                type="date"
                value={filters.date}
                onChange={(e) => setFilters({...filters, date: e.target.value})}
              />
            </div>
            <div>
              <Label htmlFor="timeSlot">Time Slot</Label>
              <Select value={filters.timeSlot} onValueChange={(value) => setFilters({...filters, timeSlot: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="All time slots" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All time slots</SelectItem>
                  <SelectItem value="8:00 AM - 10:00 AM">8:00 AM - 10:00 AM</SelectItem>
                  <SelectItem value="10:00 AM - 12:00 PM">10:00 AM - 12:00 PM</SelectItem>
                  <SelectItem value="12:00 PM - 2:00 PM">12:00 PM - 2:00 PM</SelectItem>
                  <SelectItem value="2:00 PM - 4:00 PM">2:00 PM - 4:00 PM</SelectItem>
                  <SelectItem value="4:00 PM - 6:00 PM">4:00 PM - 6:00 PM</SelectItem>
                  <SelectItem value="6:00 PM - 8:00 PM">6:00 PM - 8:00 PM</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="search">Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  id="search"
                  placeholder="Search bookings..."
                  value={filters.search}
                  onChange={(e) => setFilters({...filters, search: e.target.value})}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex items-end">
              <Button 
                variant="outline" 
                onClick={() => setFilters({date: '', timeSlot: '', search: ''})}
                className="w-full"
              >
                Clear Filters
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Pending Bookings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-yellow-500" />
            Pending Assignments ({filteredBookings.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-8">
              <RefreshCw className="h-8 w-8 animate-spin" />
            </div>
          ) : filteredBookings.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
              <p className="text-lg font-medium">No pending assignments</p>
              <p className="text-sm">All bookings have been assigned to cleaners</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredBookings.map((booking) => (
                <Card key={booking.id} className="border-l-4 border-l-yellow-500">
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-4 mb-2">
                          <h3 className="font-semibold text-lg">#{booking.id.slice(-8)}</h3>
                          {getStatusBadge('pending')}
                          <span className="text-sm text-gray-500">
                            {formatDate(booking.booking_date)} • {booking.time_slot}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                          <div className="flex items-center gap-2 text-sm">
                            <User className="h-4 w-4 text-gray-500" />
                            <span className="font-medium">{booking.customer_name}</span>
                          </div>
                          <div className="flex items-center gap-2 text-sm">
                            <Mail className="h-4 w-4 text-gray-500" />
                            <span>{booking.customer_email}</span>
                          </div>
                          <div className="flex items-center gap-2 text-sm">
                            <Phone className="h-4 w-4 text-gray-500" />
                            <span>{booking.customer_phone || 'Not provided'}</span>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500">House Size:</span>
                            <span className="ml-2 font-medium">{booking.house_size}</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Frequency:</span>
                            <span className="ml-2 font-medium capitalize">{booking.frequency.replace('_', ' ')}</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Amount:</span>
                            <span className="ml-2 font-medium">${booking.total_amount?.toFixed(2)}</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Created:</span>
                            <span className="ml-2 font-medium">
                              {new Date(booking.created_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                        
                        {booking.special_instructions && (
                          <div className="mt-2 p-2 bg-gray-50 rounded text-sm">
                            <span className="text-gray-500">Special Instructions:</span>
                            <p className="mt-1">{booking.special_instructions}</p>
                          </div>
                        )}
                      </div>
                      
                      <div className="flex flex-col gap-2 ml-4">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedBooking(booking);
                            setShowDetails(true);
                          }}
                          className="flex items-center gap-2"
                        >
                          <Eye className="h-4 w-4" />
                          View Details
                        </Button>
                        
                        <div className="flex items-center gap-2">
                          <Select onValueChange={(cleanerId) => assignCleaner(booking.id, cleanerId)}>
                            <SelectTrigger className="w-48">
                              <SelectValue placeholder="Assign Cleaner" />
                            </SelectTrigger>
                            <SelectContent>
                              {cleaners.map((cleaner) => (
                                <SelectItem key={cleaner.id} value={cleaner.id}>
                                  {cleaner.first_name} {cleaner.last_name}
                                  {cleaner.rating && ` (${cleaner.rating}/5)`}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Booking Details Modal */}
      <Dialog open={showDetails} onOpenChange={setShowDetails}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Booking Details</DialogTitle>
          </DialogHeader>
          {selectedBooking && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium text-gray-500">Booking ID</Label>
                  <p className="font-mono">#{selectedBooking.id.slice(-8)}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-500">Status</Label>
                  <div className="mt-1">{getStatusBadge('pending')}</div>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-500">Date & Time</Label>
                  <p>{formatDate(selectedBooking.booking_date)} • {selectedBooking.time_slot}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-500">Amount</Label>
                  <p className="font-semibold">${selectedBooking.total_amount?.toFixed(2)}</p>
                </div>
              </div>
              
              <div>
                <Label className="text-sm font-medium text-gray-500">Customer Information</Label>
                <div className="mt-2 space-y-1">
                  <p><strong>Name:</strong> {selectedBooking.customer_name}</p>
                  <p><strong>Email:</strong> {selectedBooking.customer_email}</p>
                  <p><strong>Phone:</strong> {selectedBooking.customer_phone || 'Not provided'}</p>
                </div>
              </div>
              
              <div>
                <Label className="text-sm font-medium text-gray-500">Service Details</Label>
                <div className="mt-2 space-y-1">
                  <p><strong>House Size:</strong> {selectedBooking.house_size}</p>
                  <p><strong>Frequency:</strong> {selectedBooking.frequency.replace('_', ' ')}</p>
                </div>
              </div>
              
              {selectedBooking.special_instructions && (
                <div>
                  <Label className="text-sm font-medium text-gray-500">Special Instructions</Label>
                  <p className="mt-2 p-3 bg-gray-50 rounded">{selectedBooking.special_instructions}</p>
                </div>
              )}
              
              <div className="flex justify-end gap-2 pt-4">
                <Button variant="outline" onClick={() => setShowDetails(false)}>
                  Close
                </Button>
                <Select onValueChange={(cleanerId) => {
                  assignCleaner(selectedBooking.id, cleanerId);
                  setShowDetails(false);
                }}>
                  <SelectTrigger className="w-64">
                    <SelectValue placeholder="Assign Cleaner" />
                  </SelectTrigger>
                  <SelectContent>
                    {cleaners.map((cleaner) => (
                      <SelectItem key={cleaner.id} value={cleaner.id}>
                        {cleaner.first_name} {cleaner.last_name}
                        {cleaner.rating && ` (${cleaner.rating}/5)`}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default JobAssignmentManager;
