import React, { useState } from 'react';
import { DndContext, DragOverlay, useDraggable, useDroppable, closestCenter } from '@dnd-kit/core';
import { Card, CardContent } from './ui/card';

// Simple draggable item
const DraggableItem = ({ id, children }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    isDragging,
  } = useDraggable({
    id: id,
    data: {
      type: 'item',
      id: id
    }
  });

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
      className="cursor-grab active:cursor-grabbing p-4 bg-blue-100 border-2 border-blue-300"
    >
      <CardContent>
        {children}
      </CardContent>
    </Card>
  );
};

// Simple droppable area
const DroppableArea = ({ id, children }) => {
  const { isOver, setNodeRef } = useDroppable({
    id: id,
    data: {
      type: 'drop-zone',
      id: id
    }
  });

  return (
    <div
      ref={setNodeRef}
      className={`p-8 border-2 border-dashed rounded-lg ${
        isOver ? 'bg-green-100 border-green-400' : 'bg-gray-100 border-gray-300'
      }`}
    >
      {children}
    </div>
  );
};

// Test component
const DragDropTest = () => {
  const [draggedItem, setDraggedItem] = useState(null);
  const [droppedItems, setDroppedItems] = useState([]);

  const handleDragStart = (event) => {
    console.log('🎯 Test drag started:', event);
    const { active } = event;
    if (active.data.current?.type === 'item') {
      setDraggedItem(active.data.current.id);
    }
  };

  const handleDragEnd = (event) => {
    console.log('🎯 Test drag ended:', event);
    const { active, over } = event;
    setDraggedItem(null);

    if (!over || !active.data.current?.id) {
      console.log('❌ No valid drop target');
      return;
    }

    const itemId = active.data.current.id;
    const dropZoneId = over.data.current?.id;

    if (dropZoneId) {
      console.log(`✅ Dropped item ${itemId} in zone ${dropZoneId}`);
      setDroppedItems(prev => [...prev, { itemId, dropZoneId, timestamp: Date.now() }]);
    }
  };

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-6">Drag and Drop Test</h2>
      
      <DndContext
        collisionDetection={closestCenter}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <div className="grid grid-cols-2 gap-8">
          {/* Draggable Items */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Draggable Items</h3>
            <div className="space-y-4">
              <DraggableItem id="item-1">Item 1</DraggableItem>
              <DraggableItem id="item-2">Item 2</DraggableItem>
              <DraggableItem id="item-3">Item 3</DraggableItem>
            </div>
          </div>

          {/* Drop Zones */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Drop Zones</h3>
            <div className="space-y-4">
              <DroppableArea id="zone-1">Drop Zone 1</DroppableArea>
              <DroppableArea id="zone-2">Drop Zone 2</DroppableArea>
            </div>
          </div>
        </div>

        {/* Drag Overlay */}
        <DragOverlay>
          {draggedItem ? (
            <Card className="p-4 bg-blue-200 border-2 border-blue-400">
              <CardContent>
                Dragging: {draggedItem}
              </CardContent>
            </Card>
          ) : null}
        </DragOverlay>
      </DndContext>

      {/* Results */}
      <div className="mt-8">
        <h3 className="text-lg font-semibold mb-4">Drop Results</h3>
        <div className="space-y-2">
          {droppedItems.map((drop, index) => (
            <div key={index} className="p-2 bg-green-100 rounded">
              Item {drop.itemId} dropped in {drop.dropZoneId} at {new Date(drop.timestamp).toLocaleTimeString()}
            </div>
          ))}
          {droppedItems.length === 0 && (
            <div className="text-gray-500">No drops yet. Try dragging items to the drop zones!</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DragDropTest;
