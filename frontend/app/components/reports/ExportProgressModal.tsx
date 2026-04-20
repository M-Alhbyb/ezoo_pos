'use client';

import React from 'react';

interface ExportProgressModalProps {
  isOpen: boolean;
  progress: number;
  error?: string | null;
  onCancel: () => void;
}

export function ExportProgressModal({ isOpen, progress, error, onCancel }: ExportProgressModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 className="text-lg font-semibold mb-4">
          {error ? 'Export Failed' : 'Exporting...'}
        </h3>
        
        {error ? (
          <div className="text-red-600 mb-4">{error}</div>
        ) : (
          <div className="mb-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-sm text-gray-600 mt-2">{progress}% complete</p>
          </div>
        )}
        
        <button
          onClick={onCancel}
          className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
        >
          {error ? 'Close' : 'Cancel'}
        </button>
      </div>
    </div>
  );
}