import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { CheckCircle, Calendar, Clock, MapPin, Phone, Mail, ArrowLeft, Download } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const BookingConfirmation = () => {
  const { bookingId } = useParams();
  const [booking, setBooking] = useState(null);
  const [customer, setCustomer] = useState(null);
  const [services, setServices] = useState([]);
  const [bookingSummary, setBookingSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBookingDetails();
  }, [bookingId]);

  const loadBookingDetails = async () => {
    try {
      setLoading(true);
      
      // Try to load comprehensive booking summary first
      try {
        const summaryResponse = await axios.get(`${API}/bookings/${bookingId}/guest-summary`);
        const summaryData = summaryResponse.data;
        setBookingSummary(summaryData);
        
        // Set basic booking info from summary
        setBooking({
          id: summaryData.booking_id,
          ...summaryData.booking_details,
          total_amount: summaryData.pricing_breakdown.final_total,
          payment_status: summaryData.payment_summary.payment_status
        });
        
        // Set customer info
        setCustomer(summaryData.customer_information);
        
        // Set services from summary
        const allServices = [...summaryData.services_booked, ...summaryData.a_la_carte_services];
        setServices(allServices);
        
      } catch (summaryError) {
        // Fallback to original booking details if summary endpoint fails
        console.log('Summary endpoint failed, falling back to basic booking details:', summaryError);
        
        // Load booking details
        const bookingResponse = await axios.get(`${API}/bookings/${bookingId}`);
        const bookingData = bookingResponse.data;
        setBooking(bookingData);

        // Load customer details
        const customerResponse = await axios.get(`${API}/customers/${bookingData.customer_id}`);
        setCustomer(customerResponse.data);

        // Load all services to get details
        const servicesResponse = await axios.get(`${API}/services`);
        const allServices = servicesResponse.data;
        
        // Map booking services with full service details
        const bookingServices = bookingData.services.map(bookingService => {
          const serviceDetails = allServices.find(s => s.id === bookingService.service_id);
          return {
            ...serviceDetails,
            quantity: bookingService.quantity
          };
        });
        
        // Map a la carte services with full service details
        const aLaCarteServices = (bookingData.a_la_carte_services || []).map(bookingService => {
          const serviceDetails = allServices.find(s => s.id === bookingService.service_id);
          return {
            ...serviceDetails,
            quantity: bookingService.quantity,
            category: 'a_la_carte'
          };
        });
        
        // Combine all services
        const allServicesCombined = [...bookingServices, ...aLaCarteServices];
        setServices(allServicesCombined);
        
        // Set booking summary with fallback data structure
        setBookingSummary({
          booking_id: bookingData.id,
          booking_details: bookingData,
          customer_information: customerResponse.data,
          service_address: bookingData.address,
          services_booked: bookingServices,
          a_la_carte_services: aLaCarteServices,
          rooms_selected: bookingData.rooms || {},
          pricing_breakdown: {
            base_price: bookingData.base_price || 0,
            room_price: bookingData.room_price || 0,
            a_la_carte_total: bookingData.a_la_carte_total || 0,
            subtotal: (bookingData.base_price || 0) + (bookingData.room_price || 0) + (bookingData.a_la_carte_total || 0),
            discount_amount: 0,
            final_total: bookingData.total_amount || 0
          },
          payment_summary: {
            total_amount: bookingData.total_amount || 0,
            payment_status: bookingData.payment_status,
            payment_method: 'Online'
          },
          next_steps: [
            "Confirmation email will be sent shortly",
            "Professional cleaner will be assigned",
            "Cleaner will arrive on scheduled date and time",
            "Service completion and quality check",
            "Follow-up for customer satisfaction"
          ]
        });
      }

    } catch (error) {
      console.error('Failed to load booking details:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { color: 'bg-yellow-100 text-yellow-800', label: 'Pending' },
      confirmed: { color: 'bg-green-100 text-green-800', label: 'Confirmed' },
      in_progress: { color: 'bg-blue-100 text-blue-800', label: 'In Progress' },
      completed: { color: 'bg-purple-100 text-purple-800', label: 'Completed' },
      cancelled: { color: 'bg-red-100 text-red-800', label: 'Cancelled' }
    };
    
    const config = statusConfig[status] || statusConfig.pending;
    return (
      <Badge className={`${config.color} border-0`}>
        {config.label}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4" />
          <p className="text-white">Loading booking details...</p>
        </div>
      </div>
    );
  }

  if (!booking || !customer) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="glass-effect card-shadow">
          <CardContent className="p-8 text-center">
            <h2 className="text-2xl font-bold text-red-600 mb-4">Booking Not Found</h2>
            <p className="text-gray-600 mb-6">The booking you're looking for doesn't exist.</p>
            <Link to="/">
              <Button className="btn-hover">
                <ArrowLeft className="mr-2" size={16} />
                Back to Booking
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatHouseSize = (size) => {
    return size.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatFrequency = (frequency) => {
    return frequency.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  // Get pricing breakdown from summary or calculate from booking
  const pricingBreakdown = bookingSummary?.pricing_breakdown || {
    base_price: booking.base_price || 0,
    room_price: booking.room_price || 0,
    a_la_carte_total: booking.a_la_carte_total || 0,
    subtotal: (booking.base_price || 0) + (booking.room_price || 0) + (booking.a_la_carte_total || 0),
    discount_amount: 0,
    final_total: booking.total_amount || 0
  };

  // Get services breakdown
  const standardServices = bookingSummary?.services_booked || services.filter(s => s.category !== 'a_la_carte');
  const aLaCarteServices = bookingSummary?.a_la_carte_services || services.filter(s => s.category === 'a_la_carte');
  const roomsSelected = bookingSummary?.rooms_selected || {};
  
  // Debug logging
  console.log('Booking Summary Debug:', {
    bookingSummary,
    aLaCarteServices,
    roomsSelected,
    aLaCarteServicesLength: aLaCarteServices.length,
    roomsSelectedKeys: Object.keys(roomsSelected)
  });
  
  // Debug service pricing
  console.log('Service Pricing Debug:', {
    standardServices: standardServices.map(s => ({
      id: s.id,
      name: s.name,
      base_price: s.base_price,
      price: s.price,
      a_la_carte_price: s.a_la_carte_price,
      total_price: s.total_price,
      quantity: s.quantity
    })),
    aLaCarteServices: aLaCarteServices.map(s => ({
      id: s.id,
      name: s.name,
      base_price: s.base_price,
      price: s.price,
      a_la_carte_price: s.a_la_carte_price,
      total_price: s.total_price,
      quantity: s.quantity
    }))
  });

  return (
    <div className="min-h-screen py-8">
      <div className="container max-w-4xl">
        {/* Success Header */}
        <div className="text-center mb-8 fade-in">
          <div className="bg-green-100 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="text-green-600" size={48} />
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">
            Booking Confirmed!
          </h1>
          <p className="text-xl text-white/80">
            Thank you for choosing Maids of Cyfair
          </p>
          <p className="text-white/60 mt-2">
            Booking ID: <strong>{booking.id}</strong>
          </p>
        </div>

        {/* Main Content */}
        <div className="space-y-6 slide-up">
          {/* Booking Status */}
          <Card className="glass-effect card-shadow border-0">
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle className="text-xl font-bold text-gray-800">
                  Booking Status
                </CardTitle>
                {getStatusBadge(booking.status)}
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-6">
                <div className="flex items-center space-x-3">
                  <Calendar className="text-purple-600" size={24} />
                  <div>
                    <p className="text-sm text-gray-600">Date</p>
                    <p className="font-semibold">
                      {formatDate(booking.booking_date)}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <Clock className="text-purple-600" size={24} />
                  <div>
                    <p className="text-sm text-gray-600">Time</p>
                    <p className="font-semibold">{booking.time_slot}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <MapPin className="text-purple-600" size={24} />
                  <div>
                    <p className="text-sm text-gray-600">Location</p>
                    <p className="font-semibold">
                      {customer.address}, {customer.city}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Comprehensive Checkout Summary */}
          <Card className="glass-effect card-shadow border-0">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-gray-800">
                Checkout Summary
              </CardTitle>
              <p className="text-gray-600">Complete breakdown of all items and services checked out</p>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Service Details */}
                <div>
                  <h4 className="font-semibold text-gray-800 mb-4">Services Selected</h4>
                  <div className="space-y-3">
                    {standardServices.map((service) => (
                      <div key={service.id} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <h5 className="font-semibold text-gray-800">{service.name}</h5>
                          <p className="text-sm text-gray-600">{service.description}</p>
                          <div className="flex items-center space-x-4 mt-2">
                            <span className="text-sm text-gray-500">Duration: {service.duration_hours || 'N/A'}h</span>
                            <span className="text-sm text-gray-500">Qty: {service.quantity}</span>
                          </div>
                        </div>
                        <div className="text-right">
                          {(() => {
                            const price = service.base_price || service.price || 0;
                            const total = price * service.quantity;
                            return (
                              <>
                                <p className="font-semibold">{formatCurrency(price)} × {service.quantity}</p>
                                <p className="text-sm text-gray-600">
                                  Total: {formatCurrency(total)}
                                </p>
                                {price === 0 && (
                                  <p className="text-xs text-yellow-600">Price not available</p>
                                )}
                              </>
                            );
                          })()}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* A La Carte Services */}
                {aLaCarteServices.length > 0 ? (
                  <div>
                    <h4 className="font-semibold text-gray-800 mb-4">Additional Services</h4>
                    <div className="space-y-3">
                      {aLaCarteServices.map((service) => (
                        <div key={service.id} className="flex justify-between items-center p-4 bg-blue-50 rounded-lg">
                          <div className="flex-1">
                            <h5 className="font-semibold text-gray-800">{service.name}</h5>
                            <p className="text-sm text-gray-600">{service.description}</p>
                            <div className="flex items-center space-x-4 mt-2">
                              <span className="text-sm text-gray-500">Duration: {service.duration_hours || 'N/A'}h</span>
                              <span className="text-sm text-gray-500">Qty: {service.quantity}</span>
                            </div>
                          </div>
                          <div className="text-right">
                            {(() => {
                              const price = service.a_la_carte_price || service.base_price || service.price || 0;
                              const total = price * service.quantity;
                              return (
                                <>
                                  <p className="font-semibold">{formatCurrency(price)} × {service.quantity}</p>
                                  <p className="text-sm text-gray-600">
                                    Total: {formatCurrency(total)}
                                  </p>
                                  {price === 0 && (
                                    <p className="text-xs text-yellow-600">Price not available</p>
                                  )}
                                </>
                              );
                            })()}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                    <p className="text-sm text-yellow-800">Debug: No additional services found (aLaCarteServices.length = {aLaCarteServices.length})</p>
                  </div>
                )}

                {/* Room Selection */}
                {Object.keys(roomsSelected).length > 0 ? (
                  <div>
                    <h4 className="font-semibold text-gray-800 mb-4">Room Selection</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {Object.entries(roomsSelected).map(([roomType, details]) => {
                        // Get the correct price for each room type
                        const getRoomPrice = (type) => {
                          const roomPrices = {
                            'bedrooms': 8.50,
                            'bathrooms': 15.00,
                            'halfBathrooms': 10.00,
                            'livingRoom': 8.50,
                            'kitchen': 20.00,
                            'diningRoom': 8.50,
                            'office': 8.50,
                            'mediaRoom': 8.50,
                            'gameRoom': 8.50
                          };
                          return roomPrices[type] || 0;
                        };

                        const roomPrice = getRoomPrice(roomType);
                        const quantity = details.quantity || 1;
                        const totalPrice = roomPrice * quantity;

                        return (
                          <div key={roomType} className="p-3 bg-green-50 rounded-lg">
                            <h5 className="font-semibold text-gray-800 capitalize">
                              {roomType.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim()}
                            </h5>
                            <p className="text-sm text-gray-600">
                              {quantity} {quantity === 1 ? 'room' : 'rooms'}
                            </p>
                            <div className="mt-2">
                              <p className="text-sm text-gray-600">
                                ${roomPrice.toFixed(2)} each
                              </p>
                              <p className="text-sm font-semibold text-green-600">
                                Total: {formatCurrency(totalPrice)}
                              </p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ) : (
                  <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <p className="text-sm text-gray-600">No rooms selected</p>
                  </div>
                )}

                {/* Property Details */}
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="p-4 bg-purple-50 rounded-lg">
                    <h4 className="font-semibold text-gray-800 mb-2">Property Details</h4>
                    <div className="space-y-1">
                      <p className="text-sm"><span className="font-medium">House Size:</span> {formatHouseSize(booking.house_size)}</p>
                      <p className="text-sm"><span className="font-medium">Service Frequency:</span> {formatFrequency(booking.frequency)}</p>
                      {booking.estimated_duration_hours && (
                        <p className="text-sm"><span className="font-medium">Estimated Duration:</span> {booking.estimated_duration_hours} hours</p>
                      )}
                    </div>
                  </div>
                  
                  <div className="p-4 bg-orange-50 rounded-lg">
                    <h4 className="font-semibold text-gray-800 mb-2">Service Schedule</h4>
                    <div className="space-y-1">
                      <p className="text-sm"><span className="font-medium">Date:</span> {formatDate(booking.booking_date)}</p>
                      <p className="text-sm"><span className="font-medium">Time:</span> {booking.time_slot}</p>
                      <p className="text-sm"><span className="font-medium">Status:</span> {getStatusBadge(booking.status)}</p>
                    </div>
                  </div>
                </div>

                {/* Pricing Breakdown */}
                <div className="border-t pt-4">
                  <h4 className="font-semibold text-gray-800 mb-4">Pricing Breakdown</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Base Service Price:</span>
                      <span>{formatCurrency(pricingBreakdown.base_price)}</span>
                    </div>
                    
                    {/* Room Pricing Breakdown */}
                    {Object.keys(roomsSelected).length > 0 && (
                      <div className="border-l-2 border-blue-200 pl-3 ml-2">
                        <p className="text-sm font-medium text-gray-700 mb-2">Room Pricing:</p>
                        {Object.entries(roomsSelected).map(([roomType, details]) => {
                          const getRoomPrice = (type) => {
                            const roomPrices = {
                              'bedrooms': 8.50,
                              'bathrooms': 15.00,
                              'halfBathrooms': 10.00,
                              'livingRoom': 8.50,
                              'kitchen': 20.00,
                              'diningRoom': 8.50,
                              'office': 8.50,
                              'mediaRoom': 8.50,
                              'gameRoom': 8.50
                            };
                            return roomPrices[type] || 0;
                          };
                          
                          const roomPrice = getRoomPrice(roomType);
                          const quantity = details.quantity || 1;
                          const totalPrice = roomPrice * quantity;
                          
                          return (
                            <div key={roomType} className="flex justify-between text-sm">
                              <span className="text-gray-600">
                                {roomType.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim()} ({quantity}x):
                              </span>
                              <span>{formatCurrency(totalPrice)}</span>
                            </div>
                          );
                        })}
                        <div className="flex justify-between font-medium text-gray-800 mt-2 pt-1 border-t border-gray-200">
                          <span>Room Total:</span>
                          <span>{formatCurrency(
                            Object.entries(roomsSelected).reduce((total, [roomType, details]) => {
                              const getRoomPrice = (type) => {
                                const roomPrices = {
                                  'bedrooms': 8.50, 'bathrooms': 15.00, 'halfBathrooms': 10.00,
                                  'livingRoom': 8.50, 'kitchen': 20.00, 'diningRoom': 8.50,
                                  'office': 8.50, 'mediaRoom': 8.50, 'gameRoom': 8.50
                                };
                                return roomPrices[type] || 0;
                              };
                              return total + (getRoomPrice(roomType) * (details.quantity || 1));
                            }, 0)
                          )}</span>
                        </div>
                      </div>
                    )}
                    
                    {pricingBreakdown.a_la_carte_total > 0 && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Additional Services:</span>
                        <span>{formatCurrency(pricingBreakdown.a_la_carte_total)}</span>
                      </div>
                    )}
                    <div className="flex justify-between font-semibold">
                      <span>Subtotal:</span>
                      <span>{formatCurrency(pricingBreakdown.subtotal)}</span>
                    </div>
                    {pricingBreakdown.discount_amount > 0 && (
                      <div className="flex justify-between text-green-600">
                        <span>Discount Applied:</span>
                        <span>-{formatCurrency(pricingBreakdown.discount_amount)}</span>
                      </div>
                    )}
                    <div className="flex justify-between items-center text-lg font-bold border-t pt-2">
                      <span>Total Amount:</span>
                      <span className="text-purple-600">{formatCurrency(pricingBreakdown.final_total)}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span>Payment Status:</span>
                      <span className={`font-medium ${
                        booking.payment_status === 'paid' ? 'text-green-600' : 'text-yellow-600'
                      }`}>
                        {booking.payment_status.charAt(0).toUpperCase() + booking.payment_status.slice(1)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Customer Information */}
          <Card className="glass-effect card-shadow border-0">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-gray-800">
                Your Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3">Contact Details</h4>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Mail className="text-gray-500" size={16} />
                      <span>{customer.email}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Phone className="text-gray-500" size={16} />
                      <span>{customer.phone}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3">Service Address</h4>
                  <div className="text-gray-600">
                    <p>{customer.first_name} {customer.last_name}</p>
                    <p>{customer.address}</p>
                    <p>{customer.city}, {customer.state} {customer.zip_code}</p>
                  </div>
                </div>
              </div>
              
              {booking.special_instructions && (
                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-2">Special Instructions</h4>
                  <p className="text-gray-700">{booking.special_instructions}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* What's Next */}
          <Card className="glass-effect card-shadow border-0">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-gray-800">
                What Happens Next?
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="bg-purple-100 rounded-full p-2 mt-1">
                    <span className="text-purple-600 font-bold text-sm">1</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-800">Confirmation Email</h4>
                    <p className="text-gray-600">You'll receive a confirmation email shortly with all booking details.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <div className="bg-purple-100 rounded-full p-2 mt-1">
                    <span className="text-purple-600 font-bold text-sm">2</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-800">Cleaner Assignment</h4>
                    <p className="text-gray-600">We'll assign the best available cleaner and send you their profile.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <div className="bg-purple-100 rounded-full p-2 mt-1">
                    <span className="text-purple-600 font-bold text-sm">3</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-800">Day of Service</h4>
                    <p className="text-gray-600">Your cleaner will arrive on time and provide exceptional service.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <div className="bg-purple-100 rounded-full p-2 mt-1">
                    <span className="text-purple-600 font-bold text-sm">4</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-800">Follow-up</h4>
                    <p className="text-gray-600">We'll follow up to ensure you're completely satisfied with our service.</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button variant="outline" className="btn-hover">
              <Download className="mr-2" size={16} />
              Download Receipt
            </Button>
            
            <Link to="/">
              <Button className="btn-hover bg-purple-600 hover:bg-purple-700 w-full sm:w-auto">
                Book Another Service
              </Button>
            </Link>
          </div>

          {/* Support Information */}
          <Card className="glass-effect card-shadow border-0">
            <CardContent className="p-6 text-center">
              <h3 className="font-semibold text-gray-800 mb-2">Need Help?</h3>
              <p className="text-gray-600 mb-4">
                Our customer support team is here to assist you with any questions or concerns.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button variant="outline" size="sm">
                  <Phone className="mr-2" size={16} />
                  Call (281) 555-0123
                </Button>
                <Button variant="outline" size="sm">
                  <Mail className="mr-2" size={16} />
                  Email Support
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default BookingConfirmation;