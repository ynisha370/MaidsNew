import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, Clock, MapPin, CreditCard, Home, Repeat, Check, ArrowRight, ArrowLeft, Plus, Minus, BedDouble, Tag, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Alert, AlertDescription } from './ui/alert';
import { toast } from 'sonner';
import axios from 'axios';
import { isSafari, getBrowserInfo } from '../utils/browserCompatibility';


const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Debug environment variables and browser info
console.log('BookingFlow - BACKEND_URL:', BACKEND_URL);
console.log('BookingFlow - API:', API);

// Safari-specific debugging
const browserInfo = getBrowserInfo();
console.log('Browser Info:', browserInfo);
if (isSafari()) {
  console.log('Safari detected - enabling enhanced debugging');
  console.log('Safari User Agent:', navigator.userAgent);
  console.log('Safari Version:', browserInfo.version);
}

// Servicable zip codes
const SERVICABLE_ZIP_CODES = ['77433', '77429', '77095', '77377', '77070', '77065'];

const BookingFlow = ({ isGuest = false }) => {
  const navigate = useNavigate(); 
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);

  // Data states
  const [allServices, setAllServices] = useState([]);
  const [houseSize, setHouseSize] = useState('');
  const [frequency, setFrequency] = useState('');
  const [basePrice, setBasePrice] = useState(0);
  const [selectedServices, setSelectedServices] = useState([]);
  const [aLaCarteCart, setALaCarteCart] = useState([]);
  const [rooms, setRooms] = useState({
    bedrooms: 0,
    bathrooms: 0,
    halfBathrooms: 0,
    diningRoom: false,
    kitchen: false,
    livingRoom: false,
    mediaRoom: false,
    gameRoom: false,
    office: false
  });
  const [selectedDate, setSelectedDate] = useState('');
  const [availableDates, setAvailableDates] = useState([]);
  const [timeSlots, setTimeSlots] = useState([]);
  const [selectedTimeSlot, setSelectedTimeSlot] = useState('');
  const [customerInfo, setCustomerInfo] = useState({
    email: '',
    firstName: '',
    lastName: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    zipCode: ''
  });
  const [specialInstructions, setSpecialInstructions] = useState('');
  const [promoCode, setPromoCode] = useState('');
  const [appliedPromo, setAppliedPromo] = useState(null);
  const [promoLoading, setPromoLoading] = useState(false);
  const [roomPricing, setRoomPricing] = useState(null);
  const [roomPricingLoading, setRoomPricingLoading] = useState(false);
  
  // Booking completion states
  const [bookingStatus, setBookingStatus] = useState('pending'); // 'pending', 'processing', 'error'
  const [bookingId, setBookingId] = useState(null);

  // Demo booking function
  const createDemoBooking = async () => {
    setLoading(true);
    try {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      const tomorrowStr = tomorrow.toISOString().split('T')[0];

      const demoBookingData = {
        customer: {
          email: "demo@example.com",
          first_name: "Demo",
          last_name: "Customer",
          phone: "555-0123",
          address: "123 Demo Street",
          city: "Houston",
          state: "TX",
          zip_code: "77001",
          is_guest: true
        },
        house_size: "medium",
        frequency: "one_time",
        base_price: 150.0,
        rooms: {
          masterBedroom: true,
          masterBathroom: true,
          otherBedrooms: 2,
          otherFullBathrooms: 1,
          halfBathrooms: 1,
          diningRoom: true,
          kitchen: true,
          livingRoom: true,
          mediaRoom: false,
          gameRoom: false,
          office: false
        },
        services: [
          {
            service_id: "standard_cleaning",
            quantity: 1
          }
        ],
        a_la_carte_services: [
          {
            service_id: "deep_cleaning",
            quantity: 1
          }
        ],
        booking_date: tomorrowStr,
        time_slot: "9:00 AM - 11:00 AM",
        special_instructions: "Demo booking for testing purposes",
        promo_code: null
      };

      const response = await axios.post(`${API}/bookings/guest`, demoBookingData);
      
      // Skip payment processing for demo booking
      toast.success('Demo booking created successfully!');
      navigate(`/confirmation/${response.data.id}`);
    } catch (error) {
      toast.error('Demo booking failed. Please try again.');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const services = allServices.filter(s => !s.is_a_la_carte);
  const aLaCarteServices = allServices.filter(s => s.is_a_la_carte);

  // Load initial data
  useEffect(() => {
    console.log('BookingFlow: Initializing component');
    if (isSafari()) {
      console.log('Safari: Component initialization started');
    }
    
    // Add a small delay for Safari to ensure proper initialization
    const initDelay = isSafari() ? 100 : 0;
    
    setTimeout(() => {
      loadAllServices();
      loadAvailableDates();
    }, initDelay);
  }, []);

  // Update pricing when house size or frequency changes
  useEffect(() => {
    console.log('BookingFlow - useEffect triggered - houseSize:', houseSize, 'frequency:', frequency);
    if (houseSize && frequency) {
      fetchPricing();
    }
  }, [houseSize, frequency]);

  // Calculate room pricing when rooms or frequency change
  useEffect(() => {
    if (frequency) {
      console.log('Rooms changed, triggering room pricing calculation:', rooms);
      calculateRoomPricing();
    }
  }, [rooms, frequency]);

  const loadAllServices = async () => {
    try {
      console.log('Loading services from:', `${API}/services`);
      if (isSafari()) {
        console.log('Safari: Making services API call');
      }
      
      const response = await axios.get(`${API}/services`, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        timeout: 10000, // 10 second timeout
      });
      
      console.log('Services response:', response.data);
      setAllServices(response.data);
      
      if (isSafari()) {
        console.log('Safari: Services loaded successfully');
      }
    } catch (error) {
      console.error('Failed to load services:', error);
      if (isSafari()) {
        console.error('Safari: Services API error:', error.message);
        console.error('Safari: Error details:', error.response?.data);
      }
      toast.error('Failed to load services');
    }
  };

  const loadAvailableDates = async () => {
    try {
      console.log('Loading available dates from:', `${API}/available-dates`);
      if (isSafari()) {
        console.log('Safari: Making available dates API call');
      }
      
      const response = await axios.get(`${API}/available-dates`, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        timeout: 10000, // 10 second timeout
      });
      
      console.log('Available dates response:', response.data);
      setAvailableDates(response.data);
      
      if (isSafari()) {
        console.log('Safari: Available dates loaded successfully');
      }
    } catch (error) {
      console.error('Failed to load available dates:', error);
      if (isSafari()) {
        console.error('Safari: Available dates API error:', error.message);
        console.error('Safari: Error details:', error.response?.data);
      }
      toast.error('Failed to load available dates');
    }
  };

  const fetchPricing = async () => {
    try {
      console.log('BookingFlow - Fetching pricing for:', houseSize, frequency);
      const response = await axios.get(`${API}/pricing/${houseSize}/${frequency}`);
      console.log('BookingFlow - Pricing response:', response.data);
      setBasePrice(response.data.base_price);
    } catch (error) {
      console.error('Failed to fetch pricing:', error);
      setBasePrice(125); // fallback to minimum price
    }
  };

  const loadTimeSlots = async (date) => {
    try {
      console.log('Loading time slots for date:', date);
      if (isSafari()) {
        console.log('Safari: Making time slots API call for date:', date);
      }
      
      const response = await axios.get(`${API}/time-slots?date=${date}`, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        timeout: 10000, // 10 second timeout
      });
      
      console.log('Time slots response:', response.data);
      setTimeSlots(response.data);
      
      if (isSafari()) {
        console.log('Safari: Time slots loaded successfully');
      }
    } catch (error) {
      console.error('Failed to load time slots:', error);
      if (isSafari()) {
        console.error('Safari: Time slots API error:', error.message);
        console.error('Safari: Error details:', error.response?.data);
      }
      toast.error('Failed to load time slots');
    }
  };

  // House size options
  const houseSizeOptions = [
    { value: '1000-1500', label: '1000-1500 sq ft' },
    { value: '1500-2000', label: '1500-2000 sq ft' },
    { value: '2000-2500', label: '2000-2500 sq ft' },
    { value: '2500-3000', label: '2500-3000 sq ft' },
    { value: '3000-3500', label: '3000-3500 sq ft' },
    { value: '3500-4000', label: '3500-4000 sq ft' },
    { value: '4000-4500', label: '4000-4500 sq ft' },
    { value: '5000+', label: '5000+ sq ft' }
  ];

  // Frequency options
  const frequencyOptions = [
    { value: 'one_time', label: 'One Time  Clean / Move Out' },
    { value: 'monthly', label: 'Monthly' },
    { value: 'every_3_weeks', label: 'Every 3 Weeks' },
    { value: 'bi_weekly', label: 'Bi-Weekly' },
    { value: 'weekly', label: 'Weekly' }
  ];

  // Service functions
  const addService = (service) => {
    if (!selectedServices.find(s => s.serviceId === service.id)) {
      setSelectedServices([...selectedServices, {
        serviceId: service.id,
        serviceName: service.name,
        quantity: 1
      }]);
      toast.success(`${service.name} added`);
    }
  };

  const removeService = (serviceId) => {
    setSelectedServices(selectedServices.filter(s => s.serviceId !== serviceId));
  };

  // A la carte functions
  const addToALaCarte = (service) => {
    const existingItem = aLaCarteCart.find(item => item.serviceId === service.id);
    if (existingItem) {
      setALaCarteCart(aLaCarteCart.map(item => 
        item.serviceId === service.id 
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setALaCarteCart([...aLaCarteCart, {
        serviceId: service.id,
        serviceName: service.name,
        price: service.a_la_carte_price,
        quantity: 1
      }]);
    }
    toast.success(`${service.name} added to cart`);
  };

  const updateALaCarteQuantity = (serviceId, quantity) => {
    if (quantity === 0) {
      setALaCarteCart(aLaCarteCart.filter(item => item.serviceId !== serviceId));
      return;
    }
    setALaCarteCart(aLaCarteCart.map(item => 
      item.serviceId === serviceId ? { ...item, quantity } : item
    ));
  };

  const getALaCarteTotal = () => {
    return aLaCarteCart.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  const getTotalAmount = () => {
    // Always include base service price
    let subtotal = basePrice;
    
    // Add room pricing if rooms are selected (but don't display individual room prices)
    if (roomPricing && roomPricing.total_price && roomPricing.total_price > 0) {
      subtotal += roomPricing.total_price;
    }
    
    // Add a la carte services
    subtotal += getALaCarteTotal();
    
    if (appliedPromo) {
      const discount = calculateDiscount(subtotal);
      return Math.max(0, subtotal - discount);
    }
    return subtotal;
  };

  const calculateRoomPricing = async () => {
    if (!frequency) return;
    
    console.log('Calculating room pricing for:', { rooms, frequency });
    setRoomPricingLoading(true);
    try {
      const response = await axios.post(`${API}/calculate-room-pricing`, {
        rooms: rooms,
        frequency: frequency
      });
      console.log('Room pricing response:', response.data);
      setRoomPricing(response.data);
    } catch (error) {
      console.error('Error calculating room pricing:', error);
    } finally {
      setRoomPricingLoading(false);
    }
  };


  const calculateDiscount = (subtotal) => {
    if (!appliedPromo) return 0;
    
    let discount = 0;
    if (appliedPromo.discount_type === 'percentage') {
      discount = (subtotal * appliedPromo.discount_value) / 100;
    } else {
      discount = appliedPromo.discount_value;
    }
    
    // Apply maximum discount limit if set
    if (appliedPromo.maximum_discount_amount && discount > appliedPromo.maximum_discount_amount) {
      discount = appliedPromo.maximum_discount_amount;
    }
    
    return Math.min(discount, subtotal);
  };

  const validatePromoCode = async () => {
    if (!promoCode.trim()) {
      toast.error('Please enter a promo code');
      return;
    }

    setPromoLoading(true);
    try {
      const response = await axios.post(`${API}/validate-promo-code`, {
        code: promoCode.trim().toUpperCase(),
        subtotal: basePrice + getALaCarteTotal()
      });

      if (response.data.valid) {
        setAppliedPromo(response.data.promo);
        toast.success(`Promo code applied! You saved $${response.data.discount.toFixed(2)}`);
      } else {
        toast.error(response.data.message || 'Invalid promo code');
        setAppliedPromo(null);
      }
    } catch (error) {
      toast.error('Failed to validate promo code');
      setAppliedPromo(null);
    } finally {
      setPromoLoading(false);
    }
  };

  const removePromoCode = () => {
    setAppliedPromo(null);
    setPromoCode('');
    toast.success('Promo code removed');
  };

  // Step navigation
  const nextStep = () => {
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  // Date selection handler
  const handleDateSelect = (date) => {
    setSelectedDate(date);
    setSelectedTimeSlot('');
    loadTimeSlots(date);
  };

  // Complete booking
  const submitBooking = async () => {
    setLoading(true);
    setBookingStatus('processing');
    try {
      const bookingData = {
        customer: {
          email: customerInfo.email,
          first_name: customerInfo.firstName,
          last_name: customerInfo.lastName,
          phone: customerInfo.phone,
          address: customerInfo.address,
          city: customerInfo.city,
          state: customerInfo.state,
          zip_code: customerInfo.zipCode,
          is_guest: isGuest
        },
        house_size: houseSize,
        frequency: frequency,
        base_price: basePrice,
        rooms: rooms,
        services: selectedServices.map(item => ({
          service_id: item.serviceId,
          quantity: item.quantity
        })),
        a_la_carte_services: aLaCarteCart.map(item => ({
          service_id: item.serviceId,
          quantity: item.quantity
        })),
        booking_date: selectedDate,
        time_slot: selectedTimeSlot,
        special_instructions: specialInstructions,
        promo_code: appliedPromo?.code || null
      };

      const endpoint = isGuest ? `${API}/bookings/guest` : `${API}/bookings`;
      const response = await axios.post(endpoint, bookingData);
      setBookingId(response.data.id);
      
      // Redirect to booking confirmation page
      toast.success('Booking confirmed successfully!');
      navigate(`/confirmation/${response.data.id}`);
    } catch (error) {
      toast.error('Booking failed. Please try again.');
      console.error(error);
      setBookingStatus('error');
    } finally {
      setLoading(false);
    }
  };

  // Zip code validation
  const isValidZipCode = (zipCode) => {
    return SERVICABLE_ZIP_CODES.includes(zipCode);
  };

  // Step validation
  const canProceedToStep = (step) => {
    switch (step) {
      case 1: return houseSize && frequency;
      case 2: return selectedDate !== '' && selectedTimeSlot !== '';
      case 3: return customerInfo.email && customerInfo.firstName && customerInfo.lastName && 
                     customerInfo.zipCode && isValidZipCode(customerInfo.zipCode);
      default: return true;
    }
  };

  // Step indicators
  const steps = [
    { number: 0, title: 'Services & Rooms', icon: Home },
    { number: 1, title: 'Date & Time', icon: Calendar },
    { number: 2, title: 'Your Details', icon: Clock },
    { number: 3, title: 'Confirm & Pay', icon: MapPin },
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container">
        {/* Header */}
        <div className="professional-header mb-8 rounded-xl">
          <h1 className="text-4xl font-bold mb-4">
            Book Your Cleaning Service
          </h1>
          <p className="text-xl opacity-90">
            Professional cleaning services at your convenience
          </p>
        </div>

        {/* Step Indicator */}
        <div className="flex justify-center mb-8">
          <div className="step-indicator flex space-x-4 p-2">
            {steps.map((step) => {
              const Icon = step.icon;
              const isActive = currentStep === step.number;
              const isCompleted = currentStep > step.number;
              
              return (
                <div
                  key={step.number}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-all duration-300 ${
                    isActive
                      ? 'step-active'
                      : isCompleted
                      ? 'step-completed'
                      : 'step-inactive'
                  }`}
                >
                  <Icon size={20} />
                  <span className="font-medium hidden md:block">{step.title}</span>
                  {isCompleted && <Check size={16} />}
                </div>
              );
            })}
          </div>
        </div>

        {/* Main Content */}
        <Card className="booking-card slide-up">
          <CardContent className="p-8">
            {/* Step 1: Service & Size, Rooms & Areas, A La Carte (Combined) */}
            {currentStep === 0 && (
              <div>
                <CardHeader className="text-center pb-6">
                  <CardTitle className="text-2xl font-bold text-gray-800">
                    Select Your Cleaning Services
                  </CardTitle>
                  <p className="text-gray-600">Choose your service type, house size, rooms, and any add-ons</p>
                </CardHeader>

                <div className="space-y-8">
                  {/* Service & House Size Selection */}
                  <div className="bg-white p-6 rounded-lg border">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Service Type & House Size</h3>
                    <div className="grid md:grid-cols-2 gap-6">
                  <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                      House Size (Square Footage)
                    </label>
                    <Select value={houseSize} onValueChange={setHouseSize}>
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Select your house size" />
                      </SelectTrigger>
                      <SelectContent>
                        {houseSizeOptions.map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                      Service Frequency
                    </label>
                    <Select value={frequency} onValueChange={setFrequency}>
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Select service frequency" />
                      </SelectTrigger>
                      <SelectContent>
                        {frequencyOptions.map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                      </div>
                  </div>

                  {/* Pricing Display */}
                  {basePrice > 0 && (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
                      <div className="flex justify-between items-center">
                        <span className="text-lg font-semibold text-gray-800">Base Price:</span>
                        <span className="text-2xl font-bold text-primary">${basePrice.toFixed(2)}</span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                  </p>
                    </div>
                  )}

                  {/* Standard Services Selection */}
                    <div className="mt-6">

                    <div className="grid md:grid-cols-2 gap-4">
                      {services.map((service) => {
                        const isSelected = selectedServices.find(s => s.serviceId === service.id);
                        return (
                          <Card 
                            key={service.id} 
                            className={`service-card cursor-pointer ${isSelected ? 'selected' : ''}`}
                            onClick={() => isSelected ? removeService(service.id) : addService(service)}
                          >
                            <CardContent className="p-4">
                              <div className="flex justify-between items-start mb-2">
                                <h4 className="font-semibold text-gray-800">{service.name}</h4>
                                {isSelected && <Check className="text-primary" size={20} />}
                              </div>
                              <p className="text-sm text-gray-600 mb-3">{service.description}</p>
                              {service.duration_hours && (
                                <span className="text-sm text-gray-500">Duration: {service.duration_hours} hours</span>
                              )}
                            </CardContent>
                          </Card>
                        );
                      })}
                    </div>
                  </div>
                </div>

                  {/* Rooms & Areas Selection */}
                  <div className="bg-white p-6 rounded-lg border">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Rooms & Areas</h3>
                <div className="grid lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-2 space-y-6">
                        <div>
                          <h4 className="text-md font-medium text-gray-700 mb-3">Bedrooms & Bathrooms</h4>
                          <div className="grid md:grid-cols-3 gap-4">
                            <div className="bg-gray-50 p-4 rounded-lg">
                        <div className="flex justify-between items-center mb-2">
                                <span className="text-gray-800 text-sm">Bedrooms</span>
                                {/* <span className="text-xs font-medium text-primary">$8.50 each</span> */}
                        </div>
                        <Select
                          value={String(rooms.bedrooms)}
                          onValueChange={(v) => setRooms({ ...rooms, bedrooms: Number(v) })}
                        >
                          <SelectTrigger className="w-full">
                            <SelectValue placeholder="Select count" />
                          </SelectTrigger>
                          <SelectContent>
                            {[0,1,2,3,4,5,6].map((n) => (
                              <SelectItem key={n} value={String(n)}>{n}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                            <div className="bg-gray-50 p-4 rounded-lg">
                        <div className="flex justify-between items-center mb-2">
                                <span className="text-gray-800 text-sm">Bathrooms</span>
                                {/* <span className="text-xs font-medium text-primary">$15 each</span> */}
                        </div>
                        <Select
                          value={String(rooms.bathrooms)}
                          onValueChange={(v) => setRooms({ ...rooms, bathrooms: Number(v) })}
                        >
                          <SelectTrigger className="w-full">
                            <SelectValue placeholder="Select count" />
                          </SelectTrigger>
                          <SelectContent>
                            {[0,1,2,3,4,5,6].map((n) => (
                              <SelectItem key={n} value={String(n)}>{n}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                            <div className="bg-gray-50 p-4 rounded-lg">
                        <div className="flex justify-between items-center mb-2">
                                <span className="text-gray-800 text-sm">Half Bathrooms</span>
                                {/* <span className="text-xs font-medium text-primary">$10 each</span> */}
                        </div>
                        <Select
                          value={String(rooms.halfBathrooms)}
                          onValueChange={(v) => setRooms({ ...rooms, halfBathrooms: Number(v) })}
                        >
                          <SelectTrigger className="w-full">
                            <SelectValue placeholder="Select count" />
                          </SelectTrigger>
                          <SelectContent>
                            {[0,1,2,3,4,5,6].map((n) => (
                              <SelectItem key={n} value={String(n)}>{n}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                            </div>
                      </div>
                    </div>

                        <div>
                          <h4 className="text-md font-medium text-gray-700 mb-3">Common Areas</h4>
                    <div className="grid md:grid-cols-2 gap-4">
                            <label className="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            checked={rooms.diningRoom}
                            onChange={(e) => setRooms({ ...rooms, diningRoom: e.target.checked })}
                          />
                                <span className="text-gray-800 text-sm">Clean Dining Room</span>
                        </div>
                              {/* <span className="text-xs font-medium text-primary">$8.50</span> */}
                      </label>
                            <label className="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            checked={rooms.kitchen}
                            onChange={(e) => setRooms({ ...rooms, kitchen: e.target.checked })}
                          />
                                <span className="text-gray-800 text-sm">Clean Kitchen</span>
                        </div>
                              {/* <span className="text-xs font-medium text-primary">$20</span> */}
                      </label>
                            <label className="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            checked={rooms.livingRoom}
                            onChange={(e) => setRooms({ ...rooms, livingRoom: e.target.checked })}
                          />
                                <span className="text-gray-800 text-sm">Clean Living Room</span>
                        </div>
                              {/* <span className="text-xs font-medium text-primary">$8.50</span> */}
                      </label>
                            <label className="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            checked={rooms.mediaRoom}
                            onChange={(e) => setRooms({ ...rooms, mediaRoom: e.target.checked })}
                          />
                                <span className="text-gray-800 text-sm">Clean Media Room</span>
                        </div>
                              {/* <span className="text-xs font-medium text-primary">$8.50</span> */}
                      </label>
                            <label className="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            checked={rooms.gameRoom}
                            onChange={(e) => setRooms({ ...rooms, gameRoom: e.target.checked })}
                          />
                                <span className="text-gray-800 text-sm">Clean Game Room</span>
                        </div>
                              {/* <span className="text-xs font-medium text-primary">$8.50</span> */}
                      </label>
                            <label className="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            checked={rooms.office}
                            onChange={(e) => setRooms({ ...rooms, office: e.target.checked })}
                          />
                                <span className="text-gray-800 text-sm">Clean Office</span>
                        </div>
                              {/* <span className="text-xs font-medium text-primary">$8.50</span> */}
                      </label>
                          </div>
                    </div>
                  </div>

                      {/* Pricing Summary */}
                  <div className="bg-gray-50 rounded-lg p-6">
                        <h4 className="text-md font-semibold text-gray-800 mb-4">Pricing Summary</h4>
                        <div className="space-y-3">
                          <div className="flex justify-between">
                            <span className="text-gray-600 text-sm">Base Service:</span>
                            <span className="font-medium">${basePrice.toFixed(2)}</span>
                      </div>
                          <div className="border-t pt-3">
                            <div className="flex justify-between text-lg font-semibold">
                          <span>Total:</span>
                              <span className="text-primary">${getTotalAmount().toFixed(2)}</span>
                        </div>
                      </div>
                  </div>
                </div>
              </div>
                  </div>

                  {/* A La Carte Add-ons */}
                  <div className="bg-white p-6 rounded-lg border">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">A La Carte Add-ons (Optional)</h3>
                <div className="grid lg:grid-cols-3 gap-6">
                  {/* A La Carte Services */}
                  <div className="lg:col-span-2">
                    <div className="grid md:grid-cols-2 gap-4 max-h-96 overflow-y-auto">
                      {aLaCarteServices.map((service) => (
                        <Card key={service.id} className="service-card">
                          <CardContent className="p-4">
                            <div className="flex justify-between items-start mb-2">
                              <h4 className="font-semibold text-gray-800 text-sm">{service.name}</h4>
                              <Badge variant="secondary">${service.a_la_carte_price}</Badge>
                            </div>
                            <p className="text-xs text-gray-600 mb-3">{service.description}</p>
                            <Button 
                              onClick={() => addToALaCarte(service)}
                              className="w-full btn-hover bg-primary hover:bg-primary-light"
                              size="sm"
                            >
                              Add to Cart
                            </Button>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>

                  {/* A La Carte Cart */}
                  <div className="bg-gray-50 rounded-lg p-6">
                        <h4 className="text-md font-semibold text-gray-800 mb-4">
                      A La Carte Cart ({aLaCarteCart.length} items)
                        </h4>
                    
                    {aLaCarteCart.length === 0 ? (
                          <p className="text-gray-500 text-center py-4 text-sm">No add-on services selected</p>
                    ) : (
                      <>
                        <div className="space-y-3 mb-4 max-h-64 overflow-y-auto">
                          {aLaCarteCart.map((item) => (
                            <div key={item.serviceId} className="flex justify-between items-center bg-white p-3 rounded-lg">
                              <div className="flex-1">
                                <h4 className="font-medium text-gray-800 text-sm">{item.serviceName}</h4>
                                    <p className="text-xs text-gray-500">${item.price} each</p>
                              </div>
                              <div className="flex items-center space-x-2">
                                <Button 
                                      onClick={() => updateALaCarteQuantity(item.serviceId, item.quantity - 1)}
                                  variant="outline" 
                                  size="sm"
                                      className="w-8 h-8 p-0"
                                >
                                      -
                                </Button>
                                    <span className="w-8 text-center text-sm font-medium">{item.quantity}</span>
                                <Button 
                                      onClick={() => updateALaCarteQuantity(item.serviceId, item.quantity + 1)}
                                  variant="outline" 
                                  size="sm"
                                      className="w-8 h-8 p-0"
                                >
                                      +
                                </Button>
                              </div>
                            </div>
                          ))}
                        </div>
                        <div className="border-t pt-3">
                              <div className="flex justify-between text-lg font-semibold">
                                <span>Total:</span>
                            <span className="text-primary">${getALaCarteTotal().toFixed(2)}</span>
                          </div>
                        </div>
                      </>
                    )}
                        </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Step 2: Choose Date & Pick Time (Combined) */}
            {currentStep === 1 && (
              <div>
                <CardHeader className="text-center pb-6">
                  <CardTitle className="text-2xl font-bold text-gray-800">
                    Choose Date & Time
                  </CardTitle>
                  <p className="text-gray-600">Select your preferred date and time slot</p>
                </CardHeader>

                <div className="space-y-8">
                  {/* Date Selection */}
                  <div className="bg-white p-6 rounded-lg border">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Select Your Preferred Date</h3>
                <div className="grid grid-cols-3 md:grid-cols-5 gap-4">
                  {availableDates.map((date) => {
                    const dateObj = new Date(date);
                    const isSelected = selectedDate === date;
                    
                    return (
                      <Card 
                        key={date}
                        className={`service-card cursor-pointer ${isSelected ? 'selected' : ''}`}
                        onClick={() => handleDateSelect(date)}
                      >
                        <CardContent className="p-4 text-center">
                          <div className="text-sm text-gray-500 mb-1">
                            {dateObj.toLocaleDateString('en-US', { weekday: 'short' })}
                          </div>
                          <div className="text-lg font-semibold text-gray-800">
                            {dateObj.getDate()}
                          </div>
                          <div className="text-sm text-gray-500">
                            {dateObj.toLocaleDateString('en-US', { month: 'short' })}
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              </div>

                  {/* Time Selection */}
                  {selectedDate && (
                    <div className="bg-white p-6 rounded-lg border">
                      <h3 className="text-lg font-semibold text-gray-800 mb-4">
                    Choose Your Time Slot
                      </h3>
                      <p className="text-gray-600 mb-4">
                    Available times for {new Date(selectedDate).toLocaleDateString('en-US', { 
                      weekday: 'long', 
                      year: 'numeric', 
                      month: 'long', 
                      day: 'numeric' 
                    })}
                  </p>
                      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                        {timeSlots.map((slot) => (
                      <Card 
                            key={slot.id || slot.time_slot}
                            className={`service-card cursor-pointer ${selectedTimeSlot === slot.time_slot ? 'selected' : ''}`}
                            onClick={() => setSelectedTimeSlot(slot.time_slot)}
                      >
                        <CardContent className="p-4 text-center">
                              <Clock className="mx-auto mb-2 text-primary" size={20} />
                              <span className="font-medium text-gray-800">{slot.time_slot}</span>
                        </CardContent>
                      </Card>
                        ))}
                    </div>
                  </div>
                  )}
                </div>
              </div>
            )}

            

            {/* Step 3: Your Details */}
            {currentStep === 2 && (
              <div>
                <CardHeader className="text-center pb-6">
                  <CardTitle className="text-2xl font-bold text-gray-800">
                    Your Contact Information
                  </CardTitle>
                  <p className="text-gray-600">We need this to confirm your booking</p>
                </CardHeader>

                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
                      <Input
                        type="email"
                        value={customerInfo.email}
                        onChange={(e) => setCustomerInfo({...customerInfo, email: e.target.value})}
                        placeholder="your@email.com"
                        required
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">First Name *</label>
                      <Input
                        value={customerInfo.firstName}
                        onChange={(e) => setCustomerInfo({...customerInfo, firstName: e.target.value})}
                        placeholder="John"
                        required
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Last Name *</label>
                      <Input
                        value={customerInfo.lastName}
                        onChange={(e) => setCustomerInfo({...customerInfo, lastName: e.target.value})}
                        placeholder="Doe"
                        required
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                      <Input
                        type="tel"
                        value={customerInfo.phone}
                        onChange={(e) => setCustomerInfo({...customerInfo, phone: e.target.value})}
                        placeholder="(555) 123-4567"
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Address *</label>
                      <Input
                        value={customerInfo.address}
                        onChange={(e) => setCustomerInfo({...customerInfo, address: e.target.value})}
                        placeholder="123 Main St"
                        required
                      />
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">City *</label>
                        <Input
                          value={customerInfo.city}
                          onChange={(e) => setCustomerInfo({...customerInfo, city: e.target.value})}
                          placeholder="Houston"
                          required
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">State *</label>
                        <Input
                          value={customerInfo.state}
                          onChange={(e) => setCustomerInfo({...customerInfo, state: e.target.value})}
                          placeholder="TX"
                          required
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">ZIP Code *</label>
                      <Input
                        value={customerInfo.zipCode}
                        onChange={(e) => setCustomerInfo({...customerInfo, zipCode: e.target.value})}
                        placeholder="77095"
                        required
                      />
                      {customerInfo.zipCode && !isValidZipCode(customerInfo.zipCode) && (
                        <p className="text-red-500 text-sm mt-1">We don't service this ZIP code yet</p>
                      )}
                    </div>
                  </div>
                </div>

                <div className="mt-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Special Instructions (Optional)</label>
                  <Textarea
                    value={specialInstructions}
                    onChange={(e) => setSpecialInstructions(e.target.value)}
                    placeholder="Any special requests or instructions for our cleaning team..."
                    rows={3}
                  />
                </div>

                <div className="mt-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Promo Code (Optional)</label>
                  <div className="flex gap-2">
                    <Input
                      value={promoCode}
                      onChange={(e) => setPromoCode(e.target.value)}
                      placeholder="Enter promo code"
                    />
                    <Button
                      onClick={validatePromoCode}
                      disabled={promoLoading || !promoCode}
                      variant="outline"
                    >
                      {promoLoading ? 'Applying...' : 'Apply'}
                    </Button>
                  </div>
                  {appliedPromo && (
                    <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                      <p className="text-green-800 text-sm">
                        ✓ Promo code "{appliedPromo.code}" applied! 
                        {appliedPromo.discount_type === 'percentage' 
                          ? ` ${appliedPromo.discount_value}% off`
                          : ` $${appliedPromo.discount_value} off`
                        }
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            
            {/* Step 4: Confirm and Complete Booking */}
            {currentStep === 3 && (
              <div>
                <CardHeader className="text-center pb-6">
                  <CardTitle className="text-2xl font-bold text-gray-800">
                    {bookingStatus === 'processing' ? 'Processing Booking...' :
                     bookingStatus === 'error' ? 'Booking Error' :
                     'Confirm Your Booking'}
                  </CardTitle>
                  <p className="text-gray-600">
                    {bookingStatus === 'processing' ? 'Please wait while we process your booking.' :
                     bookingStatus === 'error' ? 'There was an issue with your booking. Please try again.' :
                     'Review your details and confirm your booking'}
                  </p>
                </CardHeader>


                {/* Booking Processing */}
                {bookingStatus === 'processing' && (
                  <div className="space-y-6">
                    <Card className="border border-blue-200 bg-blue-50">
                      <CardContent className="p-8 text-center">
                        <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4 text-blue-500" />
                        <h3 className="text-xl font-bold text-blue-800 mb-2">Processing Your Booking</h3>
                        <p className="text-blue-600">Please wait while we confirm your booking details...</p>
                      </CardContent>
                    </Card>
                  </div>
                )}

                {/* Booking Error */}
                {bookingStatus === 'error' && (
                  <div className="space-y-6">
                    <Alert className="border-red-200 bg-red-50">
                      <AlertCircle className="h-4 w-4 text-red-500" />
                      <AlertDescription className="text-red-800">
                        There was an issue processing your booking. Please try again or contact support if the problem persists.
                      </AlertDescription>
                    </Alert>
                    
                    <div className="text-center">
                      <Button 
                        onClick={() => {
                          setBookingStatus('pending');
                          setBookingId(null);
                        }}
                        className="btn-hover bg-primary hover:bg-primary-light"
                      >
                        Try Again
                      </Button>
                    </div>
                  </div>
                )}

                {/* Initial Confirmation View */}
                {bookingStatus === 'pending' && (
                  <div className="space-y-6">
                    {/* Booking Summary */}
                    <Card className="border border-gray-200">
                      <CardHeader>
                        <CardTitle className="text-lg">Booking Summary</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div className="flex justify-between">
                            <span className="text-gray-600">House Size:</span>
                            <span className="font-medium">{houseSize} sq ft</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Frequency:</span>
                            <span className="font-medium">
                              {frequencyOptions.find(f => f.value === frequency)?.label}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Date:</span>
                            <span className="font-medium">
                              {new Date(selectedDate).toLocaleDateString('en-US', { 
                                weekday: 'long', 
                                year: 'numeric', 
                                month: 'long', 
                                day: 'numeric' 
                              })}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Time:</span>
                            <span className="font-medium">{selectedTimeSlot}</span>
                          </div>
                          <div className="border-t pt-3">
                            <div className="space-y-2">
                              <div className="flex justify-between">
                                <span className="text-gray-600">Base Service:</span>
                                <span>${basePrice.toFixed(2)}</span>
                              </div>
                              {aLaCarteCart.length > 0 && (
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Add-on Services:</span>
                                  <span>${getALaCarteTotal().toFixed(2)}</span>
                                </div>
                              )}
                              {appliedPromo && (
                                <div className="flex justify-between text-green-600">
                                  <span>Discount ({appliedPromo.code}):</span>
                                  <span>-${calculateDiscount(getTotalAmount()).toFixed(2)}</span>
                                </div>
                              )}
                              <div className="flex justify-between font-semibold text-lg border-t pt-2">
                                <span>Total Amount:</span>
                                <span className="text-primary">${getTotalAmount().toFixed(2)}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Customer Info */}
                    <Card className="border border-gray-200">
                      <CardHeader>
                        <CardTitle className="text-lg">Contact Information</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid md:grid-cols-2 gap-4">
                          <div>
                            <p className="text-sm text-gray-600">Name</p>
                            <p className="font-medium">{customerInfo.firstName} {customerInfo.lastName}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-600">Email</p>
                            <p className="font-medium">{customerInfo.email}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-600">Phone</p>
                            <p className="font-medium">{customerInfo.phone || 'Not provided'}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-600">Address</p>
                            <p className="font-medium">
                              {customerInfo.address && customerInfo.city && customerInfo.state && customerInfo.zipCode
                                ? `${customerInfo.address}, ${customerInfo.city}, ${customerInfo.state} ${customerInfo.zipCode}`
                                : 'Not provided'
                              }
                            </p>
                          </div>
                        </div>
                        {specialInstructions && (
                          <div className="mt-4">
                            <p className="text-sm text-gray-600">Special Instructions</p>
                            <p className="font-medium">{specialInstructions}</p>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                )}
              </div>
            )}


            {/* Navigation Buttons */}
            {bookingStatus !== 'processing' && (
              <div className="flex justify-between mt-8">
                <Button
                  variant="outline"
                  onClick={prevStep}
                  disabled={currentStep === 0 || bookingStatus === 'processing'}
                  className="btn-hover"
                >
                  <ArrowLeft className="mr-2" size={16} />
                  Previous
                </Button>

                {currentStep < 3 ? (
                  <Button
                    onClick={nextStep}
                    disabled={!canProceedToStep(currentStep + 1)}
                    className="btn-hover bg-primary hover:bg-primary-light"
                  >
                    Next
                    <ArrowRight className="ml-2" size={16} />
                  </Button>
                ) : (
                  <Button
                    onClick={submitBooking}
                    disabled={loading || bookingStatus === 'processing'}
                    className="btn-hover bg-green-600 hover:bg-green-700"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processing...
                      </>
                    ) : bookingStatus === 'processing' ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processing Booking...
                      </>
                    ) : (
                      <>
                        Confirm Booking
                        <Check className="ml-2" size={16} />
                      </>
                    )}
                  </Button>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default BookingFlow;