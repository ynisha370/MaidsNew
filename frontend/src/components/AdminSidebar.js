import React, { useState } from 'react';
import { 
  BarChart3,
  Calendar,
  CalendarDays,
  Receipt,
  UserCheck,
  Package,
  DollarSign,
  TrendingUp,
  FileText,
  MessageSquare,
  Mail,
  Smartphone,
  Settings,
  LogOut,
  Menu,
  X,
  ChevronDown,
  ChevronRight,
  Home,
  Users,
  Bell
} from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { cn } from '../lib/utils';

const AdminSidebar = ({ 
  activeTab, 
  onTabChange, 
  isCollapsed, 
  onToggleCollapse,
  stats = {},
  counts = {},
  onLogout
}) => {
  const [expandedSections, setExpandedSections] = useState({
    management: true,
    analytics: true,
    communication: true
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const menuItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: Home,
      shortcut: '1',
      color: 'blue',
      description: 'Overview and statistics'
    },
    {
      id: 'bookings',
      label: 'Bookings',
      icon: Calendar,
      shortcut: '2',
      color: 'green',
      count: counts.bookings || 0,
      description: 'Manage all bookings'
    },
    {
      id: 'calendar',
      label: 'Calendar',
      icon: CalendarDays,
      shortcut: '3',
      color: 'purple',
      description: 'Job assignment & scheduling'
    },
    {
      id: 'invoices',
      label: 'Invoices',
      icon: Receipt,
      shortcut: '4',
      color: 'orange',
      description: 'Invoice management'
    },
    {
      id: 'cleaners',
      label: 'Cleaners',
      icon: UserCheck,
      shortcut: '5',
      color: 'teal',
      count: counts.cleaners || 0,
      description: 'Cleaner management'
    },
    {
      id: 'services',
      label: 'Services',
      icon: Package,
      shortcut: '6',
      color: 'indigo',
      count: counts.services || 0,
      description: 'Service catalog'
    },
    {
      id: 'promos',
      label: 'Promo Codes',
      icon: DollarSign,
      shortcut: '7',
      color: 'yellow',
      description: 'Discount management'
    },
    {
      id: 'reports',
      label: 'Reports',
      icon: TrendingUp,
      shortcut: '8',
      color: 'red',
      description: 'Analytics & insights'
    },
    {
      id: 'orders',
      label: 'Orders',
      icon: Users,
      shortcut: '9',
      color: 'pink',
      count: counts.orders || 0,
      description: 'Order management'
    },
    {
      id: 'faqs',
      label: 'FAQs',
      icon: FileText,
      shortcut: '0',
      color: 'gray',
      count: counts.faqs || 0,
      description: 'Frequently asked questions'
    },
    {
      id: 'tickets',
      label: 'Support Tickets',
      icon: MessageSquare,
      shortcut: 'Shift+1',
      color: 'rose',
      count: counts.tickets || 0,
      description: 'Customer support'
    },
    {
      id: 'email-reminders',
      label: 'Email Reminders',
      icon: Mail,
      shortcut: 'Shift+2',
      color: 'blue',
      description: 'Email notifications'
    },
    {
      id: 'sms-reminders',
      label: 'SMS Reminders',
      icon: Smartphone,
      shortcut: 'Shift+3',
      color: 'green',
      description: 'SMS notifications'
    }
  ];

  const getColorClasses = (color) => {
    const colorMap = {
      blue: 'bg-blue-500 hover:bg-blue-600 text-white',
      green: 'bg-green-500 hover:bg-green-600 text-white',
      purple: 'bg-purple-500 hover:bg-purple-600 text-white',
      orange: 'bg-orange-500 hover:bg-orange-600 text-white',
      teal: 'bg-teal-500 hover:bg-teal-600 text-white',
      indigo: 'bg-indigo-500 hover:bg-indigo-600 text-white',
      yellow: 'bg-yellow-500 hover:bg-yellow-600 text-white',
      red: 'bg-red-500 hover:bg-red-600 text-white',
      pink: 'bg-pink-500 hover:bg-pink-600 text-white',
      gray: 'bg-gray-500 hover:bg-gray-600 text-white',
      rose: 'bg-rose-500 hover:bg-rose-600 text-white'
    };
    return colorMap[color] || colorMap.blue;
  };

  const getActiveColorClasses = (color) => {
    const colorMap = {
      blue: 'bg-blue-50 border-blue-200 text-blue-700',
      green: 'bg-green-50 border-green-200 text-green-700',
      purple: 'bg-purple-50 border-purple-200 text-purple-700',
      orange: 'bg-orange-50 border-orange-200 text-orange-700',
      teal: 'bg-teal-50 border-teal-200 text-teal-700',
      indigo: 'bg-indigo-50 border-indigo-200 text-indigo-700',
      yellow: 'bg-yellow-50 border-yellow-200 text-yellow-700',
      red: 'bg-red-50 border-red-200 text-red-700',
      pink: 'bg-pink-50 border-pink-200 text-pink-700',
      gray: 'bg-gray-50 border-gray-200 text-gray-700',
      rose: 'bg-rose-50 border-rose-200 text-rose-700'
    };
    return colorMap[color] || colorMap.blue;
  };

  return (
    <div className={cn(
      "fixed top-0 left-0 h-full bg-white border-r border-gray-200 shadow-lg z-50 transition-all duration-300 ease-in-out",
      isCollapsed ? "w-16" : "w-72"
    )}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-blue-600 to-indigo-600">
        <div className="flex items-center justify-center">
          {!isCollapsed ? (
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white">Admin Panel</h2>
                <p className="text-xs text-blue-100">Management Dashboard</p>
              </div>
            </div>
          ) : (
            <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-blue-600" />
            </div>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleCollapse}
            className="text-white hover:bg-white/20 p-2 ml-auto"
          >
            {isCollapsed ? <Menu size={20} /> : <X size={20} />}
          </Button>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto py-4">
        <div className="px-3 space-y-2">
          {menuItems.map((item) => {
            const IconComponent = item.icon;
            const isActive = activeTab === item.id;
            const colorClasses = getColorClasses(item.color);
            const activeColorClasses = getActiveColorClasses(item.color);

            return (
              <button
                key={item.id}
                onClick={() => onTabChange(item.id)}
                className={cn(
                  "w-full flex items-center rounded-xl transition-all duration-200 group relative overflow-hidden",
                  isCollapsed ? "justify-center px-2 py-3" : "space-x-3 px-3 py-3",
                  isActive 
                    ? `${activeColorClasses} border shadow-sm` 
                    : "hover:bg-gray-50 text-gray-700 hover:text-gray-900"
                )}
                title={!isCollapsed ? item.description : item.label}
              >
                {/* Background gradient on hover */}
                <div className={cn(
                  "absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-200",
                  `bg-gradient-to-r from-${item.color}-500/10 to-${item.color}-600/10`
                )} />
                
                {/* Icon */}
                <div className={cn(
                  "flex-shrink-0 rounded-lg flex items-center justify-center transition-all duration-200",
                  isCollapsed ? "w-10 h-10" : "w-8 h-8",
                  isActive 
                    ? colorClasses 
                    : "bg-gray-100 group-hover:bg-gray-200"
                )}>
                  <IconComponent size={isCollapsed ? 20 : 16} className={isActive ? "text-white" : "text-gray-600"} />
                </div>

                {!isCollapsed && (
                  <>
                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-sm truncate">{item.label}</span>
                        <div className="flex items-center space-x-2">
                          {item.count !== undefined && item.count > 0 && (
                            <Badge 
                              className={cn(
                                "text-xs px-2 py-0.5 rounded-full",
                                isActive 
                                  ? "bg-white/20 text-white" 
                                  : "bg-blue-100 text-blue-700"
                              )}
                            >
                              {item.count}
                            </Badge>
                          )}
                          <span className="text-xs text-gray-400 hidden group-hover:inline">
                            {item.shortcut}
                          </span>
                        </div>
                      </div>
                      {isActive && (
                        <p className="text-xs text-gray-500 mt-1">{item.description}</p>
                      )}
                    </div>
                  </>
                )}

                {/* Active indicator */}
                {isActive && (
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-blue-500 rounded-l-full" />
                )}

                {/* Count badge for collapsed state */}
                {isCollapsed && item.count !== undefined && item.count > 0 && (
                  <div className="absolute -top-1 -right-1 w-5 h-5 bg-blue-500 text-white text-xs rounded-full flex items-center justify-center">
                    {item.count}
                  </div>
                )}
              </button>
            );
          })}
        </div>

        {/* Quick Stats */}
        {!isCollapsed && (
          <div className="px-3 mt-6">
            <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl p-4 border border-gray-200">
              <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                <Bell size={16} className="mr-2" />
                Quick Stats
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="text-center">
                  <div className="text-lg font-bold text-blue-600">{stats.total_bookings || 0}</div>
                  <div className="text-xs text-gray-500">Bookings</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-green-600">{stats.total_revenue || 0}</div>
                  <div className="text-xs text-gray-500">Revenue</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        {!isCollapsed && (
          <div className="text-xs text-gray-500 text-center mb-3">
            Use keyboard shortcuts for quick navigation
          </div>
        )}
        <Button
          variant="ghost"
          className={cn(
            "w-full text-gray-600 hover:text-red-600 hover:bg-red-50",
            isCollapsed ? "justify-center px-2" : "justify-start"
          )}
          onClick={onLogout}
        >
          <LogOut size={isCollapsed ? 20 : 16} className={isCollapsed ? "" : "mr-3"} />
          {!isCollapsed && "Logout"}
        </Button>
      </div>
    </div>
  );
};

export default AdminSidebar;
