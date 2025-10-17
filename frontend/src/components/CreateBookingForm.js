import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Calendar, Clock, Home, MapPin, Phone, Mail, XCircle } from 'lucide-react';
import { toast } from 'sonner';
import CancellationRequestModal from './CancellationRequestModal';

const CreateBookingForm = ({ customer, services, onSubmit, onCancel, existingBooking = null, onCancelBooking = null }) => {
  const [formData, setFormData] = useState({
    customer_id: customer.id,
    house_size: '',
    frequency: 'one_time',
    services: [],
    a_la_carte_services: [],
    rooms: {},
    booking_date: '',
    time_slot: '',
    address: {
      street: customer.address || '',
      city: customer.city || '',
      state: customer.state || '',
      zip_code: customer.zip_code || ''
    },
    special_instructions: '',
    promo_code: ''
  });

  const [availableTimeSlots, setAvailableTimeSlots] = useState([]);
  const [pricing, setPricing] = useState({ base_price: 0, total: 0 });
  const [showCancellationModal, setShowCancellationModal] = useState(false);

  const houseSizes = [
    { value: '1000-2000', label: '1000-1999 sq ft' },
    { value: '2000-2500', label: '2000-2499 sq ft' },
    { value: '2500-3000', label: '2500-2999 sq ft' },
    { value: '3000-3500', label: '3000-3499 sq ft' },
    { value: '3500-4000', label: '3500-3999 sq ft' },
    { value: '4000-4500', label: '4000-4499 sq ft' },
    { value: '4500-5000', label: '4500-4999 sq ft' },
    { value: '5000-6000', label: '5000-5999 sq ft' }
  ];

  const frequencies = [
    { value: 'one_time', label: 'One Time' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'bi_weekly', label: 'Bi-Weekly' },
    { value: 'every_3_weeks', label: 'Every 3 Weeks' },
    { value: 'monthly', label: 'Monthly' }
  ];

  const timeSlots = [
    '8:00 AM - 10:00 AM',
    '10:00 AM - 12:00 PM',
    '12:00 PM - 2:00 PM',
    '2:00 PM - 4:00 PM',
    '4:00 PM - 6:00 PM',
    '6:00 PM - 8:00 PM'
  ];

  const roomTypes = [
    { key: 'bedrooms', label: 'Bedrooms', type: 'count' },
    { key: 'bathrooms', label: 'Bathrooms', type: 'count' },
    { key: 'halfBathrooms', label: 'Half Bathrooms', type: 'count' },
    { key: 'diningRoom', label: 'Dining Room', type: 'boolean' },
    { key: 'kitchen', label: 'Kitchen', type: 'boolean' },
    { key: 'livingRoom', label: 'Living Room', type: 'boolean' },
    { key: 'mediaRoom', label: 'Media Room', type: 'boolean' },
    { key: 'gameRoom', label: 'Game Room', type: 'boolean' },
    { key: 'office', label: 'Office', type: 'boolean' }
  ];

  useEffect(() => {
    if (existingBooking) {
      // Populate form with existing booking data
      setFormData({
        customer_id: existingBooking.customer_id || customer.id,
        house_size: existingBooking.house_size || '',
        frequency: existingBooking.frequency || 'one_time',
        services: existingBooking.services || [],
        a_la_carte_services: existingBooking.a_la_carte_services || [],
        rooms: existingBooking.rooms || {},
        booking_date: existingBooking.booking_date || '',
        time_slot: existingBooking.time_slot || '',
        address: existingBooking.address || {
          street: customer.address || '',
          city: customer.city || '',
          state: customer.state || '',
          zip_code: customer.zip_code || ''
        },
        special_instructions: existingBooking.special_instructions || '',
        promo_code: existingBooking.promo_code || ''
      });
    }
  }, [existingBooking, customer]);

  useEffect(() => {
    if (formData.house_size && formData.frequency) {
      calculatePricing();
    }
  }, [formData.house_size, formData.frequency, formData.rooms, formData.services, formData.a_la_carte_services]);

  const calculatePricing = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/pricing/${formData.house_size}/${formData.frequency}`);
      const data = await response.json();
      
      let total = data.base_price;
      
      // Add room pricing if rooms are selected
      if (Object.keys(formData.rooms).length > 0) {
        const roomResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/calculate-room-pricing`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            rooms: formData.rooms,
            frequency: formData.frequency
          })
        });
        const roomData = await roomResponse.json();
        total += roomData.total_price;
      }
      
      // Add a la carte services pricing
      formData.a_la_carte_services.forEach(service => {
        const serviceObj = services.find(s => s.id === service.service_id);
        if (serviceObj && serviceObj.a_la_carte_price) {
          total += serviceObj.a_la_carte_price * service.quantity;
        }
      });
      
      setPricing({ base_price: data.base_price, total });
    } catch (error) {
      console.error('Failed to calculate pricing:', error);
    }
  };

  const handleServiceToggle = (service) => {
    const isSelected = formData.services.some(s => s.service_id === service.id);
    
    if (isSelected) {
      setFormData(prev => ({
        ...prev,
        services: prev.services.filter(s => s.service_id !== service.id)
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        services: [...prev.services, { service_id: service.id, quantity: 1 }]
      }));
    }
  };

  const handleALaCarteServiceToggle = (service) => {
    const isSelected = formData.a_la_carte_services.some(s => s.service_id === service.id);
    
    if (isSelected) {
      setFormData(prev => ({
        ...prev,
        a_la_carte_services: prev.a_la_carte_services.filter(s => s.service_id !== service.id)
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        a_la_carte_services: [...prev.a_la_carte_services, { service_id: service.id, quantity: 1 }]
      }));
    }
  };

  const handleRoomChange = (roomKey, value) => {
    setFormData(prev => ({
      ...prev,
      rooms: {
        ...prev.rooms,
        [roomKey]: value
      }
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!formData.house_size || !formData.booking_date || !formData.time_slot) {
      toast.error('Please fill in all required fields');
      return;
    }
    
    onSubmit(formData);
  };

  const handleCancelBooking = () => {
    if (existingBooking && onCancelBooking) {
      onCancelBooking(existingBooking);
    } else {
      setShowCancellationModal(true);
    }
  };

  const handleCancellationModalClose = () => {
    setShowCancellationModal(false);
  };

  const standardServices = services.filter(s => !s.is_a_la_carte);
  const aLaCarteServices = services.filter(s => s.is_a_la_carte);

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Customer Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Mail className="mr-2 h-5 w-5" />
            Customer Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Name</Label>
              <Input value={`${customer.first_name} ${customer.last_name}`} disabled />
            </div>
            <div>
              <Label>Email</Label>
              <Input value={customer.email} disabled />
            </div>
            <div>
              <Label>Phone</Label>
              <Input value={customer.phone || 'Not provided'} disabled />
            </div>
            <div>
              <Label>Customer Type</Label>
              <Input value={customer.is_guest ? 'Guest' : 'Registered'} disabled />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Service Details */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Home className="mr-2 h-5 w-5" />
            Service Details
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="house_size">House Size *</Label>
              <Select value={formData.house_size} onValueChange={(value) => setFormData(prev => ({ ...prev, house_size: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Select house size" />
                </SelectTrigger>
                <SelectContent>
                  {houseSizes.map(size => (
                    <SelectItem key={size.value} value={size.value}>{size.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="frequency">Frequency *</Label>
              <Select value={formData.frequency} onValueChange={(value) => setFormData(prev => ({ ...prev, frequency: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Select frequency" />
                </SelectTrigger>
                <SelectContent>
                  {frequencies.map(freq => (
                    <SelectItem key={freq.value} value={freq.value}>{freq.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Standard Services */}
          <div>
            <Label>Standard Services</Label>
            <div className="grid grid-cols-2 gap-2 mt-2">
              {standardServices.map(service => (
                <div key={service.id} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id={`service-${service.id}`}
                    checked={formData.services.some(s => s.service_id === service.id)}
                    onChange={() => handleServiceToggle(service)}
                    className="rounded"
                  />
                  <label htmlFor={`service-${service.id}`} className="text-sm">
                    {service.name}
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* A La Carte Services */}
          {aLaCarteServices.length > 0 && (
            <div>
              <Label>Additional Services</Label>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {aLaCarteServices.map(service => (
                  <div key={service.id} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id={`a-la-carte-${service.id}`}
                      checked={formData.a_la_carte_services.some(s => s.service_id === service.id)}
                      onChange={() => handleALaCarteServiceToggle(service)}
                      className="rounded"
                    />
                    <label htmlFor={`a-la-carte-${service.id}`} className="text-sm">
                      {service.name} (${service.a_la_carte_price})
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Room Selection */}
          <div>
            <Label>Rooms & Areas</Label>
            <div className="grid grid-cols-3 gap-4 mt-2">
              {roomTypes.map(room => (
                <div key={room.key}>
                  {room.type === 'count' ? (
                    <div>
                      <Label htmlFor={room.key} className="text-sm">{room.label}</Label>
                      <Input
                        id={room.key}
                        type="number"
                        min="0"
                        value={formData.rooms[room.key] || 0}
                        onChange={(e) => handleRoomChange(room.key, parseInt(e.target.value) || 0)}
                      />
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id={room.key}
                        checked={formData.rooms[room.key] || false}
                        onChange={(e) => handleRoomChange(room.key, e.target.checked)}
                        className="rounded"
                      />
                      <label htmlFor={room.key} className="text-sm">{room.label}</label>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Scheduling */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Calendar className="mr-2 h-5 w-5" />
            Scheduling
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="booking_date">Date *</Label>
              <Input
                id="booking_date"
                type="date"
                value={formData.booking_date}
                onChange={(e) => setFormData(prev => ({ ...prev, booking_date: e.target.value }))}
                min={new Date().toISOString().split('T')[0]}
              />
            </div>
            <div>
              <Label htmlFor="time_slot">Time Slot *</Label>
              <Select value={formData.time_slot} onValueChange={(value) => setFormData(prev => ({ ...prev, time_slot: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Select time slot" />
                </SelectTrigger>
                <SelectContent>
                  {timeSlots.map(slot => (
                    <SelectItem key={slot} value={slot}>{slot}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Address */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <MapPin className="mr-2 h-5 w-5" />
            Service Address
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="street">Street Address</Label>
              <Input
                id="street"
                value={formData.address.street}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  address: { ...prev.address, street: e.target.value }
                }))}
              />
            </div>
            <div>
              <Label htmlFor="city">City</Label>
              <Input
                id="city"
                value={formData.address.city}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  address: { ...prev.address, city: e.target.value }
                }))}
              />
            </div>
            <div>
              <Label htmlFor="state">State</Label>
              <Input
                id="state"
                value={formData.address.state}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  address: { ...prev.address, state: e.target.value }
                }))}
              />
            </div>
            <div>
              <Label htmlFor="zip_code">ZIP Code</Label>
              <Input
                id="zip_code"
                value={formData.address.zip_code}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  address: { ...prev.address, zip_code: e.target.value }
                }))}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Special Instructions */}
      <Card>
        <CardContent className="pt-6">
          <div>
            <Label htmlFor="special_instructions">Special Instructions</Label>
            <Textarea
              id="special_instructions"
              value={formData.special_instructions}
              onChange={(e) => setFormData(prev => ({ ...prev, special_instructions: e.target.value }))}
              placeholder="Any special instructions for the cleaner..."
              rows={3}
            />
          </div>
        </CardContent>
      </Card>

      {/* Pricing Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Pricing Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Base Price:</span>
              <span>${pricing.base_price.toFixed(2)}</span>
            </div>
            <div className="flex justify-between font-bold text-lg">
              <span>Total:</span>
              <span>${pricing.total.toFixed(2)}</span>
            </div>
            {formData.frequency !== 'one_time' && (
              <Badge variant="outline" className="mt-2">
                Recurring: {frequencies.find(f => f.value === formData.frequency)?.label}
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex justify-between">
        {existingBooking && (
          <Button 
            type="button" 
            variant="destructive" 
            onClick={handleCancelBooking}
            className="bg-red-600 hover:bg-red-700"
          >
            <XCircle className="mr-2 h-4 w-4" />
            Cancel Booking
          </Button>
        )}
        <div className="flex space-x-2 ml-auto">
          <Button type="button" variant="outline" onClick={onCancel}>
            {existingBooking ? 'Close' : 'Cancel'}
          </Button>
          <Button type="submit" className="bg-blue-600 hover:bg-blue-700">
            {existingBooking ? 'Update Booking' : 'Create Booking'}
          </Button>
        </div>
      </div>

      {/* Cancellation Modal */}
      {existingBooking && (
        <CancellationRequestModal
          isOpen={showCancellationModal}
          onClose={handleCancellationModalClose}
          booking={existingBooking}
        />
      )}
    </form>
  );
};

export default CreateBookingForm;
