import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Switch } from './ui/switch';
import { toast } from 'sonner';
import { 
  MessageSquare, 
  Settings, 
  Send, 
  Plus, 
  Edit, 
  Trash2, 
  Play, 
  Pause, 
  CheckCircle, 
  XCircle,
  Clock,
  Phone
} from 'lucide-react';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const SMSReminderManagement = () => {
  const [templates, setTemplates] = useState([]);
  const [reminderLogs, setReminderLogs] = useState([]);
  const [schedulerStatus, setSchedulerStatus] = useState(null);
  const [smsStatus, setSmsStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [isTemplateDialogOpen, setIsTemplateDialogOpen] = useState(false);
  const [isSendDialogOpen, setIsSendDialogOpen] = useState(false);
  const [templateForm, setTemplateForm] = useState({
    name: '',
    type: 'booking_confirmation',
    template: '',
    send_timing: 'immediate',
    is_active: true
  });
  const [sendForm, setSendForm] = useState({
    booking_id: '',
    template_id: '',
    custom_message: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadTemplates(),
        loadReminderLogs(),
        loadSchedulerStatus(),
        loadSmsStatus()
      ]);
    } catch (error) {
      toast.error('Failed to load data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await fetch(`${API}/reminder-templates`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      if (data.success) {
        setTemplates(data.templates);
      }
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  const loadReminderLogs = async () => {
    try {
      const response = await fetch(`${API}/reminders/logs?limit=50`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      if (data.success) {
        setReminderLogs(data.logs);
      }
    } catch (error) {
      console.error('Error loading reminder logs:', error);
    }
  };

  const loadSchedulerStatus = async () => {
    try {
      const response = await fetch(`${API}/reminders/scheduler/status`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      if (data.success) {
        setSchedulerStatus(data.status);
      }
    } catch (error) {
      console.error('Error loading scheduler status:', error);
    }
  };

  const loadSmsStatus = async () => {
    try {
      const response = await fetch(`${API}/reminders/sms-status`);
      const data = await response.json();
      if (data.success) {
        setSmsStatus(data);
      }
    } catch (error) {
      console.error('Error loading SMS status:', error);
    }
  };

  const handleCreateTemplate = async () => {
    try {
      const response = await fetch(`${API}/reminder-templates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(templateForm)
      });
      
      const data = await response.json();
      if (data.success) {
        toast.success('Template created successfully');
        setIsTemplateDialogOpen(false);
        setTemplateForm({
          name: '',
          type: 'booking_confirmation',
          template: '',
          send_timing: 'immediate',
          is_active: true
        });
        loadTemplates();
      } else {
        toast.error(data.message || 'Failed to create template');
      }
    } catch (error) {
      toast.error('Failed to create template');
      console.error(error);
    }
  };

  const handleUpdateTemplate = async (templateId, updates) => {
    try {
      const response = await fetch(`${API}/reminder-templates/${templateId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(updates)
      });
      
      const data = await response.json();
      if (data.success) {
        toast.success('Template updated successfully');
        loadTemplates();
      } else {
        toast.error(data.message || 'Failed to update template');
      }
    } catch (error) {
      toast.error('Failed to update template');
      console.error(error);
    }
  };

  const handleDeleteTemplate = async (templateId) => {
    if (!window.confirm('Are you sure you want to delete this template?')) {
      return;
    }

    try {
      const response = await fetch(`${API}/reminder-templates/${templateId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      const data = await response.json();
      if (data.success) {
        toast.success('Template deleted successfully');
        loadTemplates();
      } else {
        toast.error(data.message || 'Failed to delete template');
      }
    } catch (error) {
      toast.error('Failed to delete template');
      console.error(error);
    }
  };

  const handleSendReminder = async () => {
    try {
      const response = await fetch(`${API}/reminders/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(sendForm)
      });
      
      const data = await response.json();
      if (data.success) {
        toast.success('Reminder sent successfully');
        setIsSendDialogOpen(false);
        setSendForm({
          booking_id: '',
          template_id: '',
          custom_message: ''
        });
        loadReminderLogs();
      } else {
        toast.error(data.message || 'Failed to send reminder');
      }
    } catch (error) {
      toast.error('Failed to send reminder');
      console.error(error);
    }
  };

  const handleSchedulerToggle = async () => {
    try {
      const endpoint = schedulerStatus?.is_running 
        ? '/reminders/scheduler/stop' 
        : '/reminders/scheduler/start';
      
      const response = await fetch(`${API}${endpoint}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      const data = await response.json();
      if (data.success) {
        toast.success(data.message);
        loadSchedulerStatus();
      } else {
        toast.error(data.message || 'Failed to toggle scheduler');
      }
    } catch (error) {
      toast.error('Failed to toggle scheduler');
      console.error(error);
    }
  };

  const getReminderTypeLabel = (type) => {
    const labels = {
      'booking_confirmation': 'Booking Confirmation',
      'day_before_reminder': 'Day Before Reminder',
      'hour_before_reminder': 'Hour Before Reminder',
      'cleaner_on_the_way': 'Cleaner On The Way',
      'service_completed': 'Service Completed',
      'custom': 'Custom'
    };
    return labels[type] || type;
  };

  const getStatusBadge = (status) => {
    const variants = {
      'sent': { variant: 'default', icon: CheckCircle, color: 'text-green-600' },
      'failed': { variant: 'destructive', icon: XCircle, color: 'text-red-600' },
      'pending': { variant: 'secondary', icon: Clock, color: 'text-yellow-600' }
    };
    const config = variants[status] || variants['pending'];
    const Icon = config.icon;
    
    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="w-3 h-3" />
        {status}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">SMS Reminder Management</h2>
          <p className="text-gray-600">Manage text message reminders and templates</p>
        </div>
        <div className="flex items-center gap-4">
          <Badge 
            variant={smsStatus?.sms_configured ? "default" : "destructive"}
            className="flex items-center gap-1"
          >
            <Phone className="w-3 h-3" />
            {smsStatus?.sms_configured ? 'SMS Configured' : 'SMS Not Configured'}
          </Badge>
          <Badge 
            variant={schedulerStatus?.is_running ? "default" : "secondary"}
            className="flex items-center gap-1"
          >
            <MessageSquare className="w-3 h-3" />
            Scheduler {schedulerStatus?.is_running ? 'Running' : 'Stopped'}
          </Badge>
        </div>
      </div>

      <Tabs defaultValue="templates" className="space-y-4">
        <TabsList>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="logs">Reminder Logs</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="templates" className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Reminder Templates</h3>
            <Dialog open={isTemplateDialogOpen} onOpenChange={setIsTemplateDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Template
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Reminder Template</DialogTitle>
                  <DialogDescription>
                    Create a new SMS reminder template with customizable text.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="name">Template Name</Label>
                    <Input
                      id="name"
                      value={templateForm.name}
                      onChange={(e) => setTemplateForm({...templateForm, name: e.target.value})}
                      placeholder="e.g., Day Before Reminder"
                    />
                  </div>
                  <div>
                    <Label htmlFor="type">Reminder Type</Label>
                    <Select 
                      value={templateForm.type} 
                      onValueChange={(value) => setTemplateForm({...templateForm, type: value})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="booking_confirmation">Booking Confirmation</SelectItem>
                        <SelectItem value="day_before_reminder">Day Before Reminder</SelectItem>
                        <SelectItem value="hour_before_reminder">Hour Before Reminder</SelectItem>
                        <SelectItem value="cleaner_on_the_way">Cleaner On The Way</SelectItem>
                        <SelectItem value="service_completed">Service Completed</SelectItem>
                        <SelectItem value="custom">Custom</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="template">Message Template</Label>
                    <Textarea
                      id="template"
                      value={templateForm.template}
                      onChange={(e) => setTemplateForm({...templateForm, template: e.target.value})}
                      placeholder="Hi {customer_name}! Your cleaning service is confirmed for {booking_date} at {time_slot}..."
                      rows={4}
                    />
                    <p className="text-sm text-gray-500 mt-1">
                      Available variables: {'{customer_name}'}, {'{booking_date}'}, {'{time_slot}'}, {'{house_size}'}, {'{services}'}, {'{eta}'}, {'{company_name}'}
                    </p>
                  </div>
                  <div>
                    <Label htmlFor="timing">Send Timing</Label>
                    <Select 
                      value={templateForm.send_timing} 
                      onValueChange={(value) => setTemplateForm({...templateForm, send_timing: value})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="immediate">Immediate</SelectItem>
                        <SelectItem value="24h">24 Hours Before</SelectItem>
                        <SelectItem value="1h">1 Hour Before</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="active"
                      checked={templateForm.is_active}
                      onCheckedChange={(checked) => setTemplateForm({...templateForm, is_active: checked})}
                    />
                    <Label htmlFor="active">Active</Label>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsTemplateDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleCreateTemplate}>
                    Create Template
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          <div className="grid gap-4">
            {templates.map((template) => (
              <Card key={template.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{template.name}</CardTitle>
                      <CardDescription>
                        {getReminderTypeLabel(template.type)} • {template.send_timing}
                      </CardDescription>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={template.is_active ? "default" : "secondary"}>
                        {template.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setSelectedTemplate(template);
                          setTemplateForm({
                            name: template.name,
                            type: template.type,
                            template: template.template,
                            send_timing: template.send_timing,
                            is_active: template.is_active
                          });
                          setIsTemplateDialogOpen(true);
                        }}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteTemplate(template.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                    {template.template}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="logs" className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Reminder Logs</h3>
            <Button onClick={loadReminderLogs} variant="outline">
              Refresh
            </Button>
          </div>

          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Booking ID</TableHead>
                  <TableHead>Phone</TableHead>
                  <TableHead>Template</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Sent At</TableHead>
                  <TableHead>Message</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {reminderLogs.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell className="font-mono text-sm">{log.booking_id}</TableCell>
                    <TableCell className="font-mono text-sm">{log.customer_phone}</TableCell>
                    <TableCell>{log.template_id}</TableCell>
                    <TableCell>{getStatusBadge(log.status)}</TableCell>
                    <TableCell>{new Date(log.sent_at).toLocaleString()}</TableCell>
                    <TableCell className="max-w-xs truncate">{log.message}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  Scheduler Settings
                </CardTitle>
                <CardDescription>
                  Control the automatic reminder scheduler
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Automatic Scheduler</p>
                    <p className="text-sm text-gray-600">
                      Automatically send reminders based on booking dates
                    </p>
                  </div>
                  <Button
                    onClick={handleSchedulerToggle}
                    variant={schedulerStatus?.is_running ? "destructive" : "default"}
                  >
                    {schedulerStatus?.is_running ? (
                      <>
                        <Pause className="w-4 h-4 mr-2" />
                        Stop Scheduler
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 mr-2" />
                        Start Scheduler
                      </>
                    )}
                  </Button>
                </div>
                
                {schedulerStatus && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm">
                      <strong>Status:</strong> {schedulerStatus.is_running ? 'Running' : 'Stopped'}
                    </p>
                    <p className="text-sm">
                      <strong>Last Check:</strong> {new Date(schedulerStatus.last_check).toLocaleString()}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Send className="w-5 h-5" />
                  Send Manual Reminder
                </CardTitle>
                <CardDescription>
                  Send a reminder immediately for a specific booking
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Dialog open={isSendDialogOpen} onOpenChange={setIsSendDialogOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Send className="w-4 h-4 mr-2" />
                      Send Manual Reminder
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Send Manual Reminder</DialogTitle>
                      <DialogDescription>
                        Send a reminder immediately for a specific booking.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="booking_id">Booking ID</Label>
                        <Input
                          id="booking_id"
                          value={sendForm.booking_id}
                          onChange={(e) => setSendForm({...sendForm, booking_id: e.target.value})}
                          placeholder="Enter booking ID"
                        />
                      </div>
                      <div>
                        <Label htmlFor="template_id">Template</Label>
                        <Select 
                          value={sendForm.template_id} 
                          onValueChange={(value) => setSendForm({...sendForm, template_id: value})}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select template" />
                          </SelectTrigger>
                          <SelectContent>
                            {templates.map((template) => (
                              <SelectItem key={template.id} value={template.id}>
                                {template.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label htmlFor="custom_message">Custom Message (Optional)</Label>
                        <Textarea
                          id="custom_message"
                          value={sendForm.custom_message}
                          onChange={(e) => setSendForm({...sendForm, custom_message: e.target.value})}
                          placeholder="Override template with custom message..."
                          rows={3}
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsSendDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={handleSendReminder}>
                        Send Reminder
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SMSReminderManagement;
