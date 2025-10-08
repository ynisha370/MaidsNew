import React, { useState, useEffect } from 'react';
import {
  Settings,
  User,
  Bell,
  Shield,
  Phone,
  Mail,
  MapPin,
  Edit,
  Save,
  X,
  Eye,
  EyeOff,
  AlertTriangle
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Switch } from './ui/switch';
import { toast } from 'sonner';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
const API = `${BACKEND_URL}/api`;

const CleanerSettings = () => {
  const { user } = useAuth();
  const [settings, setSettings] = useState({
    notifications: {
      job_assignments: true,
      job_reminders: true,
      payment_notifications: true,
      schedule_changes: true
    },
    profile: {
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      phone: user?.phone || '',
      email: user?.email || ''
    },
    privacy: {
      show_contact_info: true,
      allow_marketing: false
    }
  });
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await axios.get(`${API}/cleaner/settings`);
      setSettings(response.data || settings);
    } catch (error) {
      console.error('Failed to load settings:', error);
      // Use default settings if API fails
    }
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      await axios.post(`${API}/cleaner/settings`, settings);
      toast.success('Settings saved successfully!');
      setEditing(false);
    } catch (error) {
      toast.error('Failed to save settings');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    loadSettings(); // Reset to saved values
    setEditing(false);
  };

  const updateSetting = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
  };

  return (
    <div className="space-y-6">
      {/* Profile Settings */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="flex items-center">
              <User className="mr-2" size={20} />
              Profile Information
            </CardTitle>
            <div className="flex gap-2">
              {editing ? (
                <>
                  <Button variant="outline" size="sm" onClick={handleCancel}>
                    <X className="mr-2" size={16} />
                    Cancel
                  </Button>
                  <Button size="sm" onClick={handleSave} disabled={loading}>
                    <Save className="mr-2" size={16} />
                    Save
                  </Button>
                </>
              ) : (
                <Button variant="outline" size="sm" onClick={() => setEditing(true)}>
                  <Edit className="mr-2" size={16} />
                  Edit
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="first_name">First Name</Label>
              <Input
                id="first_name"
                value={settings.profile.first_name}
                onChange={(e) => updateSetting('profile', 'first_name', e.target.value)}
                disabled={!editing}
              />
            </div>
            <div>
              <Label htmlFor="last_name">Last Name</Label>
              <Input
                id="last_name"
                value={settings.profile.last_name}
                onChange={(e) => updateSetting('profile', 'last_name', e.target.value)}
                disabled={!editing}
              />
            </div>
            <div>
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={settings.profile.email}
                onChange={(e) => updateSetting('profile', 'email', e.target.value)}
                disabled={!editing}
              />
            </div>
            <div>
              <Label htmlFor="phone">Phone Number</Label>
              <Input
                id="phone"
                value={settings.profile.phone}
                onChange={(e) => updateSetting('profile', 'phone', e.target.value)}
                disabled={!editing}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Bell className="mr-2" size={20} />
            Notification Preferences
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="job_assignments">Job Assignments</Label>
              <p className="text-sm text-gray-500">Get notified when new jobs are assigned</p>
            </div>
            <Switch
              id="job_assignments"
              checked={settings.notifications.job_assignments}
              onCheckedChange={(checked) => updateSetting('notifications', 'job_assignments', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="job_reminders">Job Reminders</Label>
              <p className="text-sm text-gray-500">Reminders before scheduled jobs</p>
            </div>
            <Switch
              id="job_reminders"
              checked={settings.notifications.job_reminders}
              onCheckedChange={(checked) => updateSetting('notifications', 'job_reminders', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="payment_notifications">Payment Notifications</Label>
              <p className="text-sm text-gray-500">Alerts for payments and withdrawals</p>
            </div>
            <Switch
              id="payment_notifications"
              checked={settings.notifications.payment_notifications}
              onCheckedChange={(checked) => updateSetting('notifications', 'payment_notifications', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="schedule_changes">Schedule Changes</Label>
              <p className="text-sm text-gray-500">Notifications for booking changes</p>
            </div>
            <Switch
              id="schedule_changes"
              checked={settings.notifications.schedule_changes}
              onCheckedChange={(checked) => updateSetting('notifications', 'schedule_changes', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Privacy Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Shield className="mr-2" size={20} />
            Privacy & Security
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="show_contact_info">Show Contact Information</Label>
              <p className="text-sm text-gray-500">Allow customers to see your phone number</p>
            </div>
            <Switch
              id="show_contact_info"
              checked={settings.privacy.show_contact_info}
              onCheckedChange={(checked) => updateSetting('privacy', 'show_contact_info', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="allow_marketing">Marketing Communications</Label>
              <p className="text-sm text-gray-500">Receive promotional emails and offers</p>
            </div>
            <Switch
              id="allow_marketing"
              checked={settings.privacy.allow_marketing}
              onCheckedChange={(checked) => updateSetting('privacy', 'allow_marketing', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Account Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <AlertTriangle className="mr-2" size={20} />
            Account Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Member Since</p>
              <p className="font-medium">January 2024</p>
            </div>
            <div>
              <p className="text-gray-500">Account Status</p>
              <p className="font-medium text-green-600">Active</p>
            </div>
            <div>
              <p className="text-gray-500">Cleaner ID</p>
              <p className="font-medium">{user?.id || 'N/A'}</p>
            </div>
            <div>
              <p className="text-gray-500">Total Jobs Completed</p>
              <p className="font-medium">25</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CleanerSettings;
