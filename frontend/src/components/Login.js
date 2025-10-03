import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, User } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { toast } from 'sonner';
import { useAuth } from '../contexts/AuthContext';
import ImageSlideshow from './ImageSlideshow';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Slideshow images from the slides folder
  const slideshowImages = [
    '/slides/bridgeland.jpeg',
    '/slides/townelake.jpg',
    '/slides/fairfield.jpg',
    '/slides/colescrossing.jpg'
  ];

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await login(formData.email, formData.password);
      
      if (result.success) {
        toast.success('Login successful!');
        navigate('/');
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = () => {
    // Try environment variable first, fallback to hardcoded value
    const googleClientId = process.env.REACT_APP_GOOGLE_CLIENT_ID || '758684152649-6o73m1nt3okhh6v32oi6ki5fq2khd51t.apps.googleusercontent.com';
    
    console.log('Environment check:');
    console.log('- NODE_ENV:', process.env.NODE_ENV);
    console.log('- REACT_APP_GOOGLE_CLIENT_ID:', process.env.REACT_APP_GOOGLE_CLIENT_ID);
    console.log('- All REACT_APP vars:', Object.keys(process.env).filter(key => key.startsWith('REACT_APP')));
    console.log('- Using Google Client ID:', googleClientId);
    
    if (!googleClientId) {
      toast.error('Google OAuth not configured. Please contact support.');
      console.error('No Google Client ID available');
      return;
    }
    
    // Store signin intent in localStorage
    localStorage.setItem('oauth_intent', 'signin');
    
    // Use backend redirect URI to ensure consistency
    const baseUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
    const redirectUri = encodeURIComponent(`${baseUrl}/api/auth/google/callback`);
    const scope = encodeURIComponent('openid email profile');
    const responseType = 'code';
    const state = encodeURIComponent('signin'); // Add state to distinguish sign-in
    const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${googleClientId}&redirect_uri=${redirectUri}&scope=${scope}&response_type=${responseType}&state=${state}&access_type=offline&prompt=consent`;
    
    // Debug logging
    console.log('OAuth Debug Information:');
    console.log('- Base URL:', baseUrl);
    console.log('- Redirect URI (raw):', `${baseUrl}/api/auth/google/callback`);
    console.log('- Redirect URI (encoded):', redirectUri);
    console.log('- Google Client ID:', googleClientId);
    console.log('- Full OAuth URL:', googleAuthUrl);
    
    console.log('Redirecting to:', googleAuthUrl);
    
    // Ensure OAuth opens in system browser, not embedded WebView
    // This prevents the Google OAuth policy compliance error
    window.open(googleAuthUrl, '_blank', 'noopener,noreferrer');
  };

  const handleContinueAsGuest = () => {
    toast.success('Continuing as guest...');
    navigate('/guest-booking');
  };

  return (
    <div className="min-h-screen flex">
      {/* Login Form - Left Side */}
      <div className="w-full lg:w-2/5 xl:w-1/3 flex flex-col justify-center px-4 sm:px-8 lg:px-12 xl:px-16 py-8 bg-gray-50">
        <div className="w-full max-w-md mx-auto lg:mx-0">
          <div className="text-left mb-8">
            <h2 className="text-3xl font-bold text-gray-900">
              Welcome Back
            </h2>
            <p className="mt-2 text-gray-600">
              Sign in to your account to book cleaning services
            </p>
          </div>
          <Card className="auth-form backdrop-blur-sm bg-white/95 shadow-2xl">
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
              {/* Email Field */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <Input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="Enter your email"
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              {/* Password Field */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="Enter your password"
                    className="pl-10 pr-10"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              {/* Demo Credentials */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-blue-800 mb-2">Demo Credentials</h4>
                <div className="text-sm text-blue-700">
                  <p><strong>Email:</strong> test@maids.com</p>
                  <p><strong>Password:</strong> test@maids@1234</p>
                </div>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="mt-2"
                  onClick={() => setFormData({ email: 'test@maids.com', password: 'test@maids@1234' })}
                >
                  Use Demo Credentials
                </Button>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full btn-hover bg-primary hover:bg-primary-light"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <div className="loading-spinner mr-2" />
                    Signing In...
                  </>
                ) : (
                  'Sign In'
                )}
              </Button>
            </form>

            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">Or</span>
                </div>
              </div>

              {/* Google Sign-in Button */}
              <div className="mt-6">
                <Button
                  type="button"
                  variant="outline"
                  className="w-full btn-hover border-gray-300 hover:bg-gray-50"
                  onClick={handleGoogleSignIn}
                >
                  <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Sign in with Google
                </Button>
              </div>

              {/* Sign Up Button */}
              <div className="mt-4">
                <Button
                  type="button"
                  variant="outline"
                  className="w-full btn-hover border-green-300 text-green-600 hover:bg-green-50"
                  onClick={() => navigate('/register')}
                >
                  <User className="w-5 h-5 mr-2" />
                  Create New Account
                </Button>
              </div>

              {/* Continue as Guest Button */}
              <div className="mt-4">
                <Button
                  type="button"
                  variant="outline"
                  className="w-full btn-hover border-blue-300 text-blue-600 hover:bg-blue-50"
                  onClick={handleContinueAsGuest}
                >
                  <User className="w-5 h-5 mr-2" />
                  Continue as Guest
                </Button>
              </div>

              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Image Slideshow - Right Side */}
      <div className="hidden lg:flex lg:w-3/5 xl:w-2/3 relative">
        <ImageSlideshow 
          images={slideshowImages} 
          interval={6000}
          className="w-full h-full"
        />
      </div>
    </div>
  );
};

export default Login;