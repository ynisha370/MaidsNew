
import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { toast } from 'sonner';

const GoogleCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const handleGoogleCallback = async () => {
      try {
        // Check if we have token and user from backend redirect
        const token = searchParams.get('token');
        const userEmail = searchParams.get('user');
        const code = searchParams.get('code');
        const error = searchParams.get('error');
        const state = searchParams.get('state');

        if (error) {
          setError(`Google OAuth error: ${error}`);
          setLoading(false);
          return;
        }

        // If we have token from backend redirect, use it directly
        if (token && userEmail) {
          console.log('Received token from backend redirect');
          
          // Get the intent from localStorage
          const intent = localStorage.getItem('oauth_intent') || state;
          console.log('OAuth intent:', intent);
          
          // Store the token
          localStorage.setItem('token', token);
          
          // Get user data from backend using the token
          const userResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000'}/api/auth/me`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Accept': 'application/json',
            },
            credentials: 'include', // Required for Safari to send cookies
          });
          
          if (userResponse.ok) {
            const userData = await userResponse.json();
            localStorage.setItem('user', JSON.stringify(userData));
            
            // Clear the intent from localStorage
            localStorage.removeItem('oauth_intent');
            
            // Show appropriate message based on the OAuth intent
            if (intent === 'signup') {
              toast.success('Account created successfully with Google!');
            } else {
              toast.success('Successfully signed in with Google!');
            }
            navigate('/');
          } else {
            throw new Error('Failed to get user data');
          }
        } else if (code) {
          // Fallback: handle code exchange (for direct frontend handling)
          console.log('Received Google OAuth code:', code);
          console.log('OAuth state:', state);
          
          // Get the intent from localStorage
          const intent = localStorage.getItem('oauth_intent') || state;
          console.log('OAuth intent:', intent);

          // Send the code to your backend to exchange for tokens
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000'}/api/auth/google/callback`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
            credentials: 'include', // Required for Safari to send cookies
            body: JSON.stringify({ code }),
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to authenticate with Google');
          }

          const data = await response.json();
          console.log('Google OAuth success:', data);

          // Store the token and user data
          if (data.access_token) {
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // Clear the intent from localStorage
            localStorage.removeItem('oauth_intent');
            
            // Show appropriate message based on the OAuth intent
            if (intent === 'signup') {
              toast.success('Account created successfully with Google!');
            } else {
              toast.success('Successfully signed in with Google!');
            }
            navigate('/');
          } else {
            throw new Error('No access token received');
          }
        } else {
          setError('No authorization code or token received from Google');
          setLoading(false);
          return;
        }

      } catch (err) {
        console.error('Google OAuth callback error:', err);
        setError(err.message);
        toast.error(`Authentication failed: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    handleGoogleCallback();
  }, [searchParams, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Completing Google Sign-in...</h2>
          <p className="text-gray-600">Please wait while we authenticate your account.</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <h2 className="text-xl font-semibold text-red-800 mb-2">Authentication Failed</h2>
            <p className="text-red-600">{error}</p>
          </div>
          <button
            onClick={() => navigate('/login')}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Back to Login
          </button>
        </div>
      </div>
    );
  }

  return null;
};

export default GoogleCallback;
