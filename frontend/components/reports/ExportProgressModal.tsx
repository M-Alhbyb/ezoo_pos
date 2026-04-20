'use client';

import React from 'react';
import { X } from 'lucide-react';

export interface ExportProgressModalProps {
  isOpen: boolean;
  progress: number;
  onCancel: () => void;
  status?: 'started' | 'processing' | 'completed' | 'failed';
  errorMessage?: string;
}

export function ExportProgressModal({
  isOpen,
  progress,
  onCancel,
  status = 'processing',
  errorMessage
}: ExportProgressModalProps) {
  if (!isOpen) return null;

  const getStatusText = () => {
    switch (status) {
      case 'started':
        return 'Initializing export...';
      case 'processing':
        return 'Generating report...';
      case 'completed':
        return 'Export complete!';
      case 'failed':
        return 'Export failed';
      default:
        return 'Processing...';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'failed':
        return 'bg-red-500';
      default:
        return 'bg-blue-500';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Export Progress</h2>
          <button
            onClick={onCancel}
            className="text-gray-500 hover:text-gray-700 transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6">
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-2">{getStatusText()}</p>
            
            <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
              <div
                className={`h-full ${getStatusColor()} transition-all duration-300`}
                style={{ width: `${progress}%` }}
              />
            </div>
            
            <p className="text-right text-sm text-gray-500 mt-1">{progress}%</p>
          </div>

          {errorMessage && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md mb-4">
              <p className="text-sm text-red-800">{errorMessage}</p>
            </div>
          )}

          <div className="flex justify-end gap-3">
            {status !== 'completed' && status !== 'failed' && (
              <button
                onClick={onCancel}
                className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
              >
                Cancel
              </button>
            )}
            
            {(status === 'completed' || status === 'failed') && (
              <button
                onClick={onCancel}
                className="px-4 py-2 text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
              >
                Close
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}