import React, { useState, useEffect, useCallback } from 'react';
import { DndContext, DragOverlay, useDraggable, useDroppable, closestCenter } from '@dnd-kit/core';
import { 
  Calendar, 
  Clock, 
  User, 
  DollarSign, 
  Home, 
  MapPin,
  Repeat,
  AlertCircle,
  CheckCircle,
  XCircle,
  RefreshCw,
  Move,
  Trash2,
  Edit
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Textarea } from './ui/textarea';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Draggable Job Card Component
const DraggableJobCard = ({ job }) => {
  console.log('🎯 Rendering DraggableJobCard for job:', job);
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    isDragging,
  } = useDraggable({
    id: job.id,
    data: {
      type: 'job',
      job: job
    }
  });
  
  console.log('Draggable attributes:', { attributes, listeners, isDragging });

  const style = transform ? {
    transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
    opacity: isDragging ? 0.6 : 1,
  } : undefined;

  return (
    <Card
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className={`cursor-grab active:cursor-grabbing transition-all duration-200 hover:shadow-md ${
        isDragging ? 'opacity-60' : ''
      }`}
      onMouseDown={(e) => {
        console.log('🖱️ Mouse down on job card:', job.id);
        e.preventDefault();
      }}
      onDragStart={(e) => {
        console.log('🎯 Native drag start on job card:', job.id);
      }}
    >
      <CardContent className="p-4">
        <div className="flex justify-between items-start mb-3">
          <div>
            <h4 className="font-semibold text-sm">#{job.id.slice(-8)}</h4>
            <p className="text-xs text-gray-500">Customer: {typeof job.customer_id === 'object' ? job.customer_id.name || 'Unknown' : job.customer_id}</p>
          </div>
          <Badge variant="outline" className="text-xs">
            {job.estimated_duration_hours}h
          </Badge>
        </div>
        
        <div className="space-y-2">
          <div className="flex items-center text-xs text-gray-600">
            <Calendar className="w-3 h-3 mr-1" />
            <span>{typeof job.booking_date === 'object' ? job.booking_date.date || job.booking_date : job.booking_date}</span>
          </div>
          
          <div className="flex items-center text-xs text-gray-600">
            <Clock className="w-3 h-3 mr-1" />
            <span>{typeof job.time_slot === 'object' ? job.time_slot.start + '-' + job.time_slot.end : job.time_slot}</span>
          </div>
          
          <div className="flex items-center text-xs text-gray-600">
            <Home className="w-3 h-3 mr-1" />
            <span>{job.house_size}</span>
          </div>
          
          <div className="flex items-center text-xs text-gray-600">
            <Repeat className="w-3 h-3 mr-1" />
            <span>{typeof job.frequency === 'object' ? job.frequency.type || job.frequency : job.frequency?.replace('_', ' ') || 'One-time'}</span>
          </div>
          
          <div className="flex items-center text-xs font-medium text-green-600">
            <DollarSign className="w-3 h-3 mr-1" />
            <span>${job.total_amount}</span>
          </div>
          
          {job.address && (
            <div className="flex items-center text-xs text-gray-600">
              <MapPin className="w-3 h-3 mr-1" />
              <span>
                {typeof job.address === 'object' 
                  ? `${job.address.city || ''}, ${job.address.state || ''}`.replace(/^,\s*|,\s*$/g, '').replace(/,\s*,/g, ',')
                  : job.address || 'No address'
                }
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// Droppable Calendar Cell Component
const DroppableCalendarCell = ({ cleaner, timeSlot, date, isAvailable, existingJobs, onJobMove, onJobEdit, onJobDelete }) => {
  console.log('🎯 Rendering DroppableCalendarCell:', { cleaner: cleaner.cleaner_id, timeSlot, isAvailable });
  const { isOver, setNodeRef } = useDroppable({
    id: `${cleaner.cleaner_id}-${timeSlot}`,
    data: {
      type: 'calendar-slot',
      cleanerId: cleaner.cleaner_id,
      timeSlot: timeSlot,
      date: date,
      isAvailable: isAvailable
    }
  });
  
  console.log('Droppable cell isOver:', isOver);

  const getCellColor = () => {
    if (existingJobs.length > 0) return 'bg-blue-100 border-blue-200';
    if (isAvailable === false) return 'bg-red-50 border-red-100';
    if (isAvailable === true) return 'bg-green-50 border-green-100';
    return 'bg-gray-50 border-gray-200';
  };

  const getIcon = () => {
    if (existingJobs.length > 0) return <CheckCircle className="w-4 h-4 text-blue-600" />;
    if (isAvailable === false) return <XCircle className="w-4 h-4 text-red-500" />;
    if (isAvailable === true) return <CheckCircle className="w-4 h-4 text-green-600" />;
    return <AlertCircle className="w-4 h-4 text-gray-400" />;
  };

  return (
    <div
      ref={setNodeRef}
      className={`
        relative h-20 border-2 rounded-lg transition-all duration-200
        ${getCellColor()}
        ${isOver ? 'border-blue-400 bg-blue-100' : ''}
        ${isAvailable ? 'cursor-pointer hover:shadow-md' : 'cursor-not-allowed'}
      `}
    >
      <div className="p-2 h-full flex flex-col justify-between">
        <div className="flex justify-center">
          {getIcon()}
        </div>
        
        {existingJobs.length > 0 && (
          <div className="text-xs text-center">
            <Badge variant="secondary" className="text-xs">
              {existingJobs.length} job{existingJobs.length > 1 ? 's' : ''}
            </Badge>
          </div>
        )}
        
        <div className="text-xs text-center text-gray-600">
          {timeSlot}
        </div>
        
        {existingJobs.length > 0 && (
          <div className="absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity duration-200 bg-black bg-opacity-50 rounded-lg">
            <div className="flex space-x-1">
              <Button
                size="sm"
                variant="secondary"
                className="h-6 w-6 p-0"
                onClick={(e) => {
                  e.stopPropagation();
                  onJobEdit?.(existingJobs[0]);
                }}
              >
                <Edit className="w-3 h-3" />
              </Button>
              <Button
                size="sm"
                variant="destructive"
                className="h-6 w-6 p-0"
                onClick={(e) => {
                  e.stopPropagation();
                  onJobDelete?.(existingJobs[0]);
                }}
              >
                <Trash2 className="w-3 h-3" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Main Calendar Job Assignment Component
const CalendarJobAssignment = () => {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [unassignedJobs, setUnassignedJobs] = useState([]);
  const [cleanerAvailability, setCleanerAvailability] = useState([]);
  const [loading, setLoading] = useState(false);
  const [draggedJob, setDraggedJob] = useState(null);
  const [confirmDialog, setConfirmDialog] = useState(null);
  const [assignmentNotes, setAssignmentNotes] = useState('');
  
  // Job management state
  const [selectedJob, setSelectedJob] = useState(null);
  const [showJobDetails, setShowJobDetails] = useState(false);

  const timeSlots = ["08:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00", "16:00-18:00"];

  useEffect(() => {
    loadData();
  }, [selectedDate]);

  const loadData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadUnassignedJobs(),
        loadCleanerAvailability()
      ]);
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const loadUnassignedJobs = async () => {
    try {
      console.log('🔄 Loading unassigned jobs...');
      const response = await axios.get(`${API}/admin/calendar/unassigned-jobs`);
      console.log('Unassigned jobs response:', response.data);
      setUnassignedJobs(response.data.unassigned_jobs || []);
    } catch (error) {
      console.error('Failed to load unassigned jobs:', error);
    }
  };

  const loadCleanerAvailability = async () => {
    try {
      console.log('🔄 Loading cleaner availability...');
      const response = await axios.get(`${API}/admin/calendar/availability-summary?date=${selectedDate}`);
      console.log('Cleaner availability response:', response.data);
      setCleanerAvailability(response.data.cleaners || []);
    } catch (error) {
      console.error('Failed to load cleaner availability:', error);
    }
  };

  const handleDragStart = (event) => {
    console.log('🎯 Drag started:', event);
    const { active } = event;
    console.log('Active data:', active.data.current);
    if (active.data.current?.type === 'job') {
      console.log('Setting dragged job:', active.data.current.job);
      setDraggedJob(active.data.current.job);
    }
  };

  const handleDragEnd = async (event) => {
    console.log('🎯 Drag ended:', event);
    const { active, over } = event;
    console.log('Active:', active);
    console.log('Over:', over);
    setDraggedJob(null);

    if (!over || !active.data.current?.job) {
      console.log('❌ No valid drop target or job data');
      return;
    }

    const job = active.data.current.job;
    const dropData = over.data.current;
    console.log('Job:', job);
    console.log('Drop data:', dropData);

    if (dropData?.type === 'calendar-slot') {
      const { cleanerId, timeSlot, isAvailable } = dropData;

      // Check if this is moving an existing job or assigning a new one
      const isExistingJob = job.cleaner_id && job.time_slot;
      
      if (isExistingJob) {
        // Moving existing job to new slot
        const warnings = [];
        
        if (!isAvailable) {
          warnings.push('Time slot is marked as unavailable');
        }

        // Check if there are already existing jobs in this slot
        const existingJobs = getExistingJobsForSlot(cleanerId, timeSlot);
        if (existingJobs.length > 0) {
          warnings.push(`${existingJobs.length} job(s) already assigned to this slot`);
        }

        // Show confirmation dialog for moving job
        setConfirmDialog({
          job,
          cleanerId,
          timeSlot,
          date: selectedDate,
          warnings,
          isMove: true
        });
      } else {
        // Assigning new job to slot
        const warnings = [];
        
        if (!isAvailable) {
          warnings.push('Time slot is marked as unavailable');
        }

        // Check if there are already existing jobs in this slot
        const existingJobs = getExistingJobsForSlot(cleanerId, timeSlot);
        if (existingJobs.length > 0) {
          warnings.push(`${existingJobs.length} job(s) already assigned to this slot`);
        }

        // Show confirmation dialog for assignment
        setConfirmDialog({
          job,
          cleanerId,
          timeSlot,
          date: selectedDate,
          warnings,
          isMove: false
        });
      }
    }
  };

  const confirmAssignment = async () => {
    if (!confirmDialog) return;

    try {
      const { job, cleanerId, timeSlot, isMove } = confirmDialog;
      
      // Parse time slot to create start and end times
      const [startTimeStr, endTimeStr] = timeSlot.split('-');
      const startTime = new Date(`${selectedDate}T${startTimeStr}:00`);
      const endTime = new Date(`${selectedDate}T${endTimeStr}:00`);

      if (isMove) {
        // Moving existing job
        const moveData = {
          cleaner_id: cleanerId,
          start_time: startTime.toISOString(),
          end_time: endTime.toISOString(),
          notes: assignmentNotes || `Moved to new slot on ${selectedDate}`
        };

        await axios.patch(`${API}/admin/bookings/${job.id}`, moveData);
        toast.success('Job moved successfully');
      } else {
        // Assigning new job
        const assignmentData = {
          booking_id: job.id,
          cleaner_id: cleanerId,
          start_time: startTime.toISOString(),
          end_time: endTime.toISOString(),
          notes: assignmentNotes
        };

        const response = await axios.post(`${API}/admin/calendar/assign-job`, assignmentData);
        
        // Handle response with warnings
        if (response.data.warning) {
          toast.warning(response.data.message || 'Job assigned with warnings');
        } else {
          toast.success('Job assigned successfully');
        }
      }
      
      setConfirmDialog(null);
      setAssignmentNotes('');
      
      // Reload data
      await loadData();
      
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to process job');
    }
  };

  const getExistingJobsForSlot = (cleanerId, timeSlot) => {
    // Get cleaner data from the availability response
    const cleaner = cleanerAvailability.find(c => c.cleaner_id === cleanerId);
    if (!cleaner || !cleaner.slots[timeSlot]) {
      return [];
    }

    // Return existing jobs from the slot data
    return cleaner.slots[timeSlot].existing_jobs || [];
  };

  // Handle job edit
  const handleJobEdit = (job) => {
    setSelectedJob(job);
    setShowJobDetails(true);
  };

  // Handle job delete
  const handleJobDelete = async (job) => {
    if (window.confirm('Are you sure you want to delete this job?')) {
      try {
        await axios.delete(`${API}/admin/bookings/${job.id}`);
        toast.success('Job deleted successfully');
        loadData();
      } catch (error) {
        toast.error('Failed to delete job');
      }
    }
  };

  // Handle job move between time slots
  const handleJobMove = async (job, newCleanerId, newTimeSlot) => {
    try {
      const [startTimeStr, endTimeStr] = newTimeSlot.split('-');
      const startTime = new Date(`${selectedDate}T${startTimeStr}:00`);
      const endTime = new Date(`${selectedDate}T${endTimeStr}:00`);

      const moveData = {
        cleaner_id: newCleanerId,
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString(),
        notes: `Moved from previous slot on ${selectedDate}`
      };

      await axios.patch(`${API}/admin/bookings/${job.id}`, moveData);
      toast.success('Job moved successfully');
      loadData();
    } catch (error) {
      toast.error('Failed to move job');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Calendar Job Assignment</h2>
          <p className="text-gray-600">Drag jobs to assign them to cleaner schedules</p>
        </div>
        <Button onClick={loadData} disabled={loading} variant="outline">
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Date Selector */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium">Assignment Date:</label>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              min={new Date().toISOString().split('T')[0]}
              className="px-3 py-2 border rounded-md"
            />
            <Badge variant="outline">
              {cleanerAvailability.length} cleaners available
            </Badge>
          </div>
        </CardContent>
      </Card>

      <DndContext
        collisionDetection={closestCenter}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <div className="grid lg:grid-cols-4 gap-6">
          {/* Unassigned Jobs Panel */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calendar className="w-5 h-5 mr-2" />
                  Unassigned Jobs ({unassignedJobs.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {unassignedJobs.map((job) => (
                    <DraggableJobCard key={job.id} job={job} />
                  ))}
                  {unassignedJobs.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-500" />
                      <p>All jobs assigned!</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Calendar Grid */}
          <div className="lg:col-span-3">
            <Card>
              <CardHeader>
                <CardTitle>Cleaner Schedules - {selectedDate}</CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                {loading ? (
                  <div className="flex justify-center py-8">
                    <RefreshCw className="w-8 h-8 animate-spin text-gray-400" />
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse">
                      <thead>
                        <tr>
                          <th className="border p-3 text-left bg-gray-50 min-w-32">
                            <div className="flex items-center">
                              <User className="w-4 h-4 mr-2" />
                              Cleaner
                            </div>
                          </th>
                          {timeSlots.map((slot) => (
                            <th key={slot} className="border p-3 text-center bg-gray-50 min-w-24">
                              <div className="text-sm font-medium">
                                {slot}
                              </div>
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {cleanerAvailability.map((cleaner) => (
                          <tr key={cleaner.cleaner_id}>
                            <td className="border p-3">
                              <div>
                                <p className="font-medium text-sm">{cleaner.cleaner_name}</p>
                                <div className="flex items-center mt-1">
                                  <Badge 
                                    className={`text-xs ${
                                      cleaner.calendar_enabled 
                                        ? 'bg-green-100 text-green-800' 
                                        : 'bg-gray-100 text-gray-800'
                                    }`}
                                  >
                                    {cleaner.calendar_enabled ? 'Connected' : 'No Calendar'}
                                  </Badge>
                                </div>
                              </div>
                            </td>
                            {timeSlots.map((slot) => {
                              const slotData = cleaner.slots[slot];
                              const isAvailable = slotData?.available;
                              const existingJobs = getExistingJobsForSlot(cleaner.cleaner_id, slot);

                              return (
                                <td key={slot} className="border p-2">
                                  <DroppableCalendarCell
                                    cleaner={cleaner}
                                    timeSlot={slot}
                                    date={selectedDate}
                                    isAvailable={isAvailable}
                                    existingJobs={existingJobs}
                                    onJobMove={handleJobMove}
                                    onJobEdit={handleJobEdit}
                                    onJobDelete={handleJobDelete}
                                  />
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>

                    {cleanerAvailability.length === 0 && (
                      <div className="text-center py-8 text-gray-500">
                        <AlertCircle className="w-12 h-12 mx-auto mb-4" />
                        <p>No cleaners found</p>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Drag Overlay */}
        <DragOverlay>
          {draggedJob ? (
            <Card className="opacity-90 rotate-3 shadow-2xl">
              <CardContent className="p-4">
                <div className="text-sm font-medium">#{draggedJob.id.slice(-8)}</div>
                <div className="text-xs text-gray-500">{draggedJob.house_size}</div>
                <div className="text-xs text-green-600">${draggedJob.total_amount}</div>
              </CardContent>
            </Card>
          ) : null}
        </DragOverlay>
      </DndContext>

      {/* Assignment/Move Confirmation Dialog */}
      {confirmDialog && (
        <Dialog open={true} onOpenChange={() => setConfirmDialog(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {confirmDialog.isMove ? 'Confirm Job Move' : 'Confirm Job Assignment'}
              </DialogTitle>
            </DialogHeader>
            
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-2">Job Details</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>Job ID: #{confirmDialog.job.id.slice(-8)}</div>
                  <div>Amount: ${confirmDialog.job.total_amount}</div>
                  <div>House Size: {confirmDialog.job.house_size}</div>
                  <div>Duration: {confirmDialog.job.estimated_duration_hours}h</div>
                </div>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-2">
                  {confirmDialog.isMove ? 'Move Details' : 'Assignment Details'}
                </h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>Date: {confirmDialog.date}</div>
                  <div>Time: {confirmDialog.timeSlot}</div>
                  <div className="col-span-2">
                    Cleaner: {cleanerAvailability.find(c => c.cleaner_id === confirmDialog.cleanerId)?.cleaner_name}
                  </div>
                  {confirmDialog.isMove && (
                    <div className="col-span-2 text-orange-600 font-medium">
                      This will move the job from its current slot to the new slot
                    </div>
                  )}
                </div>
              </div>

              {confirmDialog.warnings && confirmDialog.warnings.length > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                  <h4 className="font-semibold mb-2 text-yellow-800 flex items-center">
                    <AlertCircle className="w-4 h-4 mr-2" />
                    Warnings
                  </h4>
                  <ul className="text-sm text-yellow-800 list-disc list-inside space-y-1">
                    {confirmDialog.warnings.map((warning, index) => (
                      <li key={index}>{warning}</li>
                    ))}
                  </ul>
                  <p className="text-xs text-yellow-700 mt-2">
                    You can proceed with the assignment, but be aware of these conflicts.
                  </p>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium mb-2">Assignment Notes (Optional)</label>
                <Textarea
                  value={assignmentNotes}
                  onChange={(e) => setAssignmentNotes(e.target.value)}
                  placeholder="Add any special notes for this assignment..."
                  rows={3}
                />
              </div>

              <div className="flex justify-end space-x-3">
                <Button
                  variant="outline"
                  onClick={() => setConfirmDialog(null)}
                >
                  Cancel
                </Button>
                <Button onClick={confirmAssignment}>
                  {confirmDialog.isMove ? 'Move Job' : 'Assign Job'}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Legend */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-6 text-sm">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>Available</span>
            </div>
            <div className="flex items-center space-x-2">
              <XCircle className="w-4 h-4 text-red-500" />
              <span>Busy/Unavailable</span>
            </div>
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-gray-400" />
              <span>No Calendar Data</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-blue-100 border border-blue-200 rounded"></div>
              <span>Has Assigned Jobs (hover to edit/delete)</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Job Details Modal */}
      {showJobDetails && selectedJob && (
        <Dialog open={true} onOpenChange={() => setShowJobDetails(false)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Job Details</DialogTitle>
            </DialogHeader>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Customer:</span>
                  <p>{selectedJob.customer_name}</p>
                </div>
                <div>
                  <span className="font-medium">Service:</span>
                  <p>{selectedJob.service_name}</p>
                </div>
                <div>
                  <span className="font-medium">House Size:</span>
                  <p>{selectedJob.house_size}</p>
                </div>
                <div>
                  <span className="font-medium">Duration:</span>
                  <p>{selectedJob.estimated_duration_hours} hours</p>
                </div>
                <div>
                  <span className="font-medium">Price:</span>
                  <p>${selectedJob.total_price}</p>
                </div>
                <div>
                  <span className="font-medium">Status:</span>
                  <p>{selectedJob.status}</p>
                </div>
                <div className="col-span-2">
                  <span className="font-medium">Address:</span>
                  <p>
                    {typeof selectedJob.address === 'object' 
                      ? `${selectedJob.address.street || ''}${selectedJob.address.apartment ? ', ' + selectedJob.address.apartment : ''}, ${selectedJob.address.city || ''}, ${selectedJob.address.state || ''} ${selectedJob.address.zip_code || ''}`.replace(/^,\s*|,\s*$/g, '').replace(/,\s*,/g, ',')
                      : selectedJob.address || 'No address provided'
                    }
                  </p>
                </div>
                {selectedJob.notes && (
                  <div className="col-span-2">
                    <span className="font-medium">Notes:</span>
                    <p>{selectedJob.notes}</p>
                  </div>
                )}
              </div>
              
              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setShowJobDetails(false)}>
                  Close
                </Button>
                <Button 
                  variant="destructive"
                  onClick={() => {
                    setShowJobDetails(false);
                    handleJobDelete(selectedJob);
                  }}
                >
                  Delete Job
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}

    </div>
  );
};

export default CalendarJobAssignment;