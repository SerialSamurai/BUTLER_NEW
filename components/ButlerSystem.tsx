import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  Send, Mail, Users, Activity, AlertCircle, CheckCircle, Clock, Search, Filter,
  ChevronRight, Shield, Database, Zap, Bot, TrendingUp, FileText, Bell,
  Settings, RefreshCw, Calendar, Wifi, Server, Globe, MapPin
} from 'lucide-react';

interface Message {
  id: number;
  type: 'system' | 'user' | 'butler';
  content: string;
  timestamp: string;
  confidence?: number;
}

interface Email {
  id: number;
  from: string;
  subject: string;
  priority: 'high' | 'normal' | 'urgent';
  unread: boolean;
  time: string;
  preview: string;
  department: string;
  tags: string[];
}

interface SystemMetrics {
  emailsProcessed: number;
  activeAlerts: number;
  responseTime: string;
  uptime: string;
  departmentsMonitored: number;
  avgDailyEmails: number;
  lastUpdated: string;
}

interface QuickAction {
  id: string;
  text: string;
  icon: React.ComponentType<{ className?: string }>;
  action: () => void;
}

interface Alert {
  id: string;
  text: string;
  icon: React.ComponentType<{ className?: string }>;
  severity: 'high' | 'medium' | 'low';
  timestamp: string;
}

const ButlerSystem: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      type: 'system',
      content: 'BUTLER Intelligence System initialized for Dallas County. Ready to assist with operational monitoring and analysis.',
      timestamp: new Date().toISOString(),
      confidence: 100
    }
  ]);
  const [input, setInput] = useState('');
  const [activeTab, setActiveTab] = useState<'assistant' | 'listserv'>('assistant');
  const [currentTime, setCurrentTime] = useState<Date | null>(null);
  const [mounted, setMounted] = useState(false);
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const [listservEmails, setListservEmails] = useState<Email[]>([
    {
      id: 1,
      from: 'emergency.mgmt@dallascounty.org',
      subject: 'Severe Weather Alert - Thunderstorm Warning Active',
      priority: 'urgent',
      unread: true,
      time: '2 min ago',
      preview: 'Thunderstorm warning in effect for northern Dallas County until 6:00 PM. Wind gusts up to 60 mph expected with possible hail.',
      department: 'Emergency Management',
      tags: ['weather', 'alert', 'urgent']
    },
    {
      id: 2,
      from: 'facilities@dallascounty.org',
      subject: 'Maintenance Schedule Update - HVAC Systems',
      priority: 'normal',
      unread: true,
      time: '15 min ago',
      preview: 'Scheduled HVAC maintenance for Buildings A, C, and E will commence at 8:00 PM tonight. Expected duration: 4 hours.',
      department: 'Facilities',
      tags: ['maintenance', 'scheduled']
    },
    {
      id: 3,
      from: 'it.security@dallascounty.org',
      subject: 'Critical Security Patch Deployment - Windows Systems',
      priority: 'high',
      unread: false,
      time: '1 hour ago',
      preview: 'Microsoft security update KB5031354 will be deployed across all county workstations tonight at 11:00 PM.',
      department: 'IT Security',
      tags: ['security', 'patch', 'scheduled']
    },
    {
      id: 4,
      from: 'hr@dallascounty.org',
      subject: 'Policy Update - Remote Work Guidelines',
      priority: 'normal',
      unread: false,
      time: '3 hours ago',
      preview: 'Updated remote work policy effective October 1st. Please review the new approval process and documentation requirements.',
      department: 'Human Resources',
      tags: ['policy', 'remote-work']
    },
    {
      id: 5,
      from: 'public.health@dallascounty.org',
      subject: 'Weekly Health Department Brief - Community Metrics',
      priority: 'normal',
      unread: false,
      time: '5 hours ago',
      preview: 'Weekly health metrics showing positive trends in community health indicators. Vaccination rates up 12% from last month.',
      department: 'Public Health',
      tags: ['weekly-brief', 'metrics']
    },
    {
      id: 6,
      from: 'finance@dallascounty.org',
      subject: 'Q3 Budget Review Meeting - Action Items',
      priority: 'high',
      unread: true,
      time: '6 hours ago',
      preview: 'Q3 budget review completed. Department heads need to submit revised projections by Friday EOB.',
      department: 'Finance',
      tags: ['budget', 'deadline', 'q3']
    }
  ]);

  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics>({
    emailsProcessed: 1247,
    activeAlerts: 3,
    responseTime: '0.8s',
    uptime: '99.9%',
    departmentsMonitored: 14,
    avgDailyEmails: 156,
    lastUpdated: new Date().toISOString()
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Handle client-side mounting to avoid hydration errors
  useEffect(() => {
    setMounted(true);
    setCurrentTime(new Date());
  }, []);

  // Real-time updates
  useEffect(() => {
    if (!mounted) return;

    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);
    return () => clearInterval(timer);
  }, [mounted]);

  // Simulate real-time metric updates
  useEffect(() => {
    if (!mounted) return;

    const interval = setInterval(() => {
      setSystemMetrics(prev => ({
        ...prev,
        emailsProcessed: prev.emailsProcessed + Math.floor(Math.random() * 3),
        responseTime: (Math.random() * 0.4 + 0.6).toFixed(1) + 's',
        lastUpdated: new Date().toISOString()
      }));
    }, 30000);
    return () => clearInterval(interval);
  }, [mounted]);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: messages.length + 1,
      type: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsProcessing(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: messages.length + 2,
        type: 'butler',
        content: generateButlerResponse(input),
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsProcessing(false);
    }, 1500);
  };

  const generateButlerResponse = (query: string): string => {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('weather') || lowerQuery.includes('alert')) {
      return 'I\'ve analyzed the severe weather alert from Emergency Management. A thunderstorm warning is in effect for northern Dallas County until 6:00 PM. I\'ve notified all field personnel and updated the emergency response protocols. Facilities have been secured.';
    } else if (lowerQuery.includes('security') || lowerQuery.includes('patch')) {
      return 'The security patch deployment is scheduled for tonight at 11:00 PM. All critical systems will remain operational. I\'ve verified compatibility with county infrastructure and prepared rollback procedures. No action required from your end.';
    } else if (lowerQuery.includes('email') || lowerQuery.includes('listserv')) {
      return `I'm monitoring ${systemMetrics.emailsProcessed} emails across 14 department listservs. Currently tracking ${systemMetrics.activeAlerts} high-priority items requiring attention. All automated responses are functioning within normal parameters.`;
    } else if (lowerQuery.includes('status') || lowerQuery.includes('system')) {
      return `System Status: All operational. Response time averaging ${systemMetrics.responseTime}. Uptime: ${systemMetrics.uptime}. I'm actively monitoring county communications and ready to assist with any departmental needs.`;
    } else {
      return 'I understand your request. I\'m analyzing relevant county data and communications to provide the most accurate response. How can I assist you with Dallas County operations today?';
    }
  };

  const handleListservAction = (emailId: number, action: string) => {
    if (action === 'analyze') {
      const email = listservEmails.find(e => e.id === emailId);
      if (email) {
        const analysisMessage: Message = {
          id: messages.length + 1,
          type: 'butler',
          content: `Analyzing email from ${email.from}: "${email.subject}"\n\nPriority: ${email.priority.toUpperCase()}\nRecommended Action: ${email.priority === 'high' ? 'Immediate response required. Draft prepared for your review.' : 'Standard processing. Logged for daily digest.'}`,
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, analysisMessage]);
        setActiveTab('assistant');
      }
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-slate-800 to-slate-900 text-white shadow-lg">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <Shield className="w-8 h-8 text-blue-400" />
                <div>
                  <h1 className="text-2xl font-bold tracking-tight">BUTLER</h1>
                  <p className="text-xs text-slate-300 uppercase tracking-wider">Behavioral Understanding & Tactical Law Enforcement Resource</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-6 text-sm">
              <div className="flex items-center space-x-2 bg-slate-700/50 px-3 py-2 rounded-lg">
                <MapPin className="w-4 h-4 text-emerald-400" />
                <span className="font-medium">Dallas County, TX</span>
              </div>
              <div className="flex items-center space-x-2 bg-slate-700/50 px-3 py-2 rounded-lg">
                <Activity className={`w-4 h-4 ${isOnline ? 'text-emerald-400 animate-pulse' : 'text-red-400'}`} />
                <span className="font-medium">{isOnline ? 'System Active' : 'Offline'}</span>
              </div>
              <div className="text-xs text-slate-400 font-mono">
                {mounted && currentTime ? currentTime.toLocaleTimeString() : '--:--:--'}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Metrics Bar */}
      <div className="bg-white border-b border-slate-200 px-6 py-3">
        <div className="grid grid-cols-4 gap-4">
          <div className="flex items-center space-x-3">
            <Mail className="w-5 h-5 text-slate-600" />
            <div>
              <p className="text-xs text-slate-500">Emails Processed</p>
              <p className="text-lg font-semibold text-slate-900">{systemMetrics.emailsProcessed.toLocaleString()}</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-amber-600" />
            <div>
              <p className="text-xs text-slate-500">Active Alerts</p>
              <p className="text-lg font-semibold text-slate-900">{systemMetrics.activeAlerts}</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Zap className="w-5 h-5 text-slate-600" />
            <div>
              <p className="text-xs text-slate-500">Response Time</p>
              <p className="text-lg font-semibold text-slate-900">{systemMetrics.responseTime}</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <div>
              <p className="text-xs text-slate-500">System Uptime</p>
              <p className="text-lg font-semibold text-slate-900">{systemMetrics.uptime}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div className="w-80 bg-white border-r border-slate-200 flex flex-col">
          <div className="border-b border-slate-200">
            <div className="flex">
              <button
                onClick={() => setActiveTab('assistant')}
                className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                  activeTab === 'assistant' 
                    ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50' 
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                AI Assistant
              </button>
              <button
                onClick={() => setActiveTab('listserv')}
                className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                  activeTab === 'listserv' 
                    ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50' 
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                Listserv Monitor
              </button>
            </div>
          </div>

          {activeTab === 'listserv' && (
            <div className="flex-1 overflow-y-auto">
              <div className="p-4 border-b border-slate-200 bg-slate-50">
                <div className="flex items-center space-x-2">
                  <Search className="w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search emails..."
                    className="flex-1 text-sm bg-white border border-slate-200 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button className="p-1 hover:bg-slate-200 rounded">
                    <Filter className="w-4 h-4 text-slate-600" />
                  </button>
                </div>
              </div>
              <div className="divide-y divide-slate-200">
                {listservEmails.map(email => (
                  <div
                    key={email.id}
                    className={`p-4 hover:bg-slate-50 cursor-pointer transition-colors ${
                      email.unread ? 'bg-blue-50' : ''
                    }`}
                    onClick={() => handleListservAction(email.id, 'analyze')}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          {email.unread && <div className="w-2 h-2 bg-blue-600 rounded-full" />}
                          <p className="text-sm font-medium text-slate-900 truncate">{email.from}</p>
                        </div>
                        <p className="text-sm text-slate-900 font-medium mt-1">{email.subject}</p>
                        <div className="flex items-center space-x-3 mt-2">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                            email.priority === 'high' 
                              ? 'bg-red-100 text-red-800' 
                              : 'bg-slate-100 text-slate-700'
                          }`}>
                            {email.priority}
                          </span>
                          <span className="text-xs text-slate-500">{email.time}</span>
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-slate-400 mt-1" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'assistant' && (
            <div className="flex-1 p-4 overflow-y-auto">
              <div className="space-y-3">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <h3 className="text-sm font-medium text-blue-900 mb-2">Quick Actions</h3>
                  <div className="space-y-2">
                    <button className="w-full text-left text-sm text-blue-700 hover:text-blue-900 hover:bg-blue-100 rounded px-2 py-1 transition-colors">
                      → Generate daily brief
                    </button>
                    <button className="w-full text-left text-sm text-blue-700 hover:text-blue-900 hover:bg-blue-100 rounded px-2 py-1 transition-colors">
                      → Check security alerts
                    </button>
                    <button className="w-full text-left text-sm text-blue-700 hover:text-blue-900 hover:bg-blue-100 rounded px-2 py-1 transition-colors">
                      → Review pending approvals
                    </button>
                    <button className="w-full text-left text-sm text-blue-700 hover:text-blue-900 hover:bg-blue-100 rounded px-2 py-1 transition-colors">
                      → Analyze listserv traffic
                    </button>
                  </div>
                </div>

                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                  <h3 className="text-sm font-medium text-amber-900 mb-2">Recent Alerts</h3>
                  <div className="space-y-1 text-xs text-amber-800">
                    <div className="flex items-center space-x-2">
                      <Clock className="w-3 h-3" />
                      <span>Weather warning - North Dallas</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Clock className="w-3 h-3" />
                      <span>IT maintenance window tonight</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Clock className="w-3 h-3" />
                      <span>Budget review deadline Friday</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col bg-white">
          <div className="flex-1 overflow-y-auto p-6">
            <div className="max-w-3xl mx-auto space-y-4">
              {messages.map(message => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-2xl px-4 py-3 rounded-lg ${
                      message.type === 'user'
                        ? 'bg-blue-600 text-white'
                        : message.type === 'butler'
                        ? 'bg-slate-100 text-slate-900 border border-slate-200'
                        : 'bg-amber-50 text-amber-900 border border-amber-200'
                    }`}
                  >
                    {message.type === 'butler' && (
                      <div className="flex items-center space-x-2 mb-2">
                        <Shield className="w-4 h-4 text-blue-600" />
                        <span className="text-xs font-medium text-blue-600 uppercase tracking-wide">BUTLER AI</span>
                      </div>
                    )}
                    {message.type === 'system' && (
                      <div className="flex items-center space-x-2 mb-2">
                        <AlertCircle className="w-4 h-4 text-amber-600" />
                        <span className="text-xs font-medium text-amber-600 uppercase tracking-wide">System</span>
                      </div>
                    )}
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                    <p className={`text-xs mt-2 ${
                      message.type === 'user' ? 'text-blue-100' : 'text-slate-500'
                    }`}>
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
              {isProcessing && (
                <div className="flex justify-start">
                  <div className="bg-slate-100 text-slate-900 px-4 py-3 rounded-lg border border-slate-200">
                    <div className="flex items-center space-x-2">
                      <Shield className="w-4 h-4 text-blue-600 animate-pulse" />
                      <span className="text-xs font-medium text-blue-600 uppercase tracking-wide">BUTLER AI</span>
                    </div>
                    <div className="flex space-x-1 mt-2">
                      <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input Area */}
          <div className="border-t border-slate-200 p-4 bg-slate-50">
            <div className="max-w-3xl mx-auto">
              <div className="flex space-x-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Ask BUTLER about county operations, emails, or alerts..."
                  className="flex-1 px-4 py-3 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  disabled={isProcessing}
                />
                <button
                  onClick={handleSend}
                  disabled={isProcessing || !input.trim()}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
                >
                  <Send className="w-4 h-4" />
                  <span>Send</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ButlerSystem;