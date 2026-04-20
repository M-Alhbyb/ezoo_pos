"use client";

import { AlertCircle, XCircle, CheckCircle, Info } from "lucide-react";

type ErrorType = "error" | "warning" | "success" | "info";

interface ErrorMessageProps {
  type?: ErrorType;
  message: string;
  onDismiss?: () => void;
  className?: string;
}

const typeConfig = {
  error: {
    icon: XCircle,
    containerClass: "bg-red-50 text-red-700 border-red-200",
    iconClass: "text-red-500",
  },
  warning: {
    icon: AlertCircle,
    containerClass: "bg-amber-50 text-amber-700 border-amber-200",
    iconClass: "text-amber-500",
  },
  success: {
    icon: CheckCircle,
    containerClass: "bg-emerald-50 text-emerald-700 border-emerald-200",
    iconClass: "text-emerald-500",
  },
  info: {
    icon: Info,
    containerClass: "bg-blue-50 text-blue-700 border-blue-200",
    iconClass: "text-blue-500",
  },
};

export default function ErrorMessage({
  type = "error",
  message,
  onDismiss,
  className = "",
}: ErrorMessageProps) {
  const config = typeConfig[type];
  const Icon = config.icon;

  return (
    <div
      className={`flex items-center gap-3 px-4 py-3 rounded-xl border animate-slide-up ${config.containerClass} ${className}`}
    >
      <Icon className={`w-5 h-5 flex-shrink-0 ${config.iconClass}`} />
      <span className="flex-1 text-sm font-medium">{message}</span>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="p-1 hover:bg-white/50 rounded-lg transition-colors"
        >
          <XCircle className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
