import React from 'react';

interface NumberInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange' | 'value'> {
  value: number;
  onChange: (value: number) => void;
  label?: string;
  error?: string;
  suffix?: string;
  containerClassName?: string;
}

export default function NumberInput({
  value,
  onChange,
  label,
  error,
  suffix,
  className = "",
  containerClassName = "",
  ...props
}: NumberInputProps) {
  
  const toComma = (val: number | string) => {
    if (!val && val !== 0) return "";
    const parts = val.toString().split(".");
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return parts.join(".");
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const rawValue = e.target.value.replace(/,/g, '');
    const numValue = parseFloat(rawValue) || 0;
    onChange(numValue);
  };

  return (
    <div className={`w-full ${containerClassName}`}>
      {label && (
        <label className="block text-sm font-medium text-slate-700 mb-1.5">
          {label} {suffix && <span className="text-slate-400 font-normal">({suffix})</span>}
        </label>
      )}
      <div className="relative">
        <input
          {...props}
          type="text"
          value={toComma(value)}
          onChange={handleChange}
          className={`w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all font-mono text-end ${className} ${error ? 'border-rose-300 ring-rose-100' : ''}`}
        />
      </div>
      {error && <p className="mt-1 text-xs text-rose-600">{error}</p>}
    </div>
  );
}
