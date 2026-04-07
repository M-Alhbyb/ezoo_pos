/**
 * FeeEditor Component
 * 
 * Add/edit fixed or percentage fees to the sale.
 * Task: T072
 * Tasks: T020-T030 - Quick-amount preset buttons
 */

"use client";

import { useState, useEffect, useRef } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency } from "@/lib/utils/format";

interface Fee {
  fee_type: "shipping" | "installation" | "custom";
  fee_label: string;
  fee_value_type: "fixed" | "percent";
  fee_value: number;
}

interface FeePresetsConfig {
  shipping: number[];
  installation: number[];
  custom: number[];
}

interface FeeEditorProps {
  fees: Fee[];
  onFeesChange: (fees: Fee[]) => void;
}

const FEE_TYPES = [
  { value: "shipping", label: ARABIC.pos.shipping || 'شحن' },
  { value: "installation", label: ARABIC.pos.installation || 'تركيب' },
  { value: "custom", label: ARABIC.pos.custom || 'مخصص' },
] as const;

export default function FeeEditor({ fees, onFeesChange }: FeeEditorProps) {
  const [showForm, setShowForm] = useState(false);
  const [newFee, setNewFee] = useState<Fee>({
    fee_type: "shipping",
    fee_label: "",
    fee_value_type: "fixed",
    fee_value: 0,
  });

  // T021: State management for fee presets
  const [feePresets, setFeePresets] = useState<FeePresetsConfig>({
    shipping: [],
    installation: [],
    custom: [],
  });
  const [loadingPresets, setLoadingPresets] = useState(true);

  // T023: WebSocket listener for preset updates
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect to WebSocket for real-time preset updates
    const connectWebSocket = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/stock-updates`;
      
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Handle preset updates
          if (data.event === 'preset_updated') {
            const { fee_type, presets } = data.data;
            setFeePresets((prev) => ({
              ...prev,
              [fee_type]: presets,
            }));
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      wsRef.current.onclose = () => {
        console.log('WebSocket closed, attempting reconnect...');
        setTimeout(connectWebSocket, 3000); // Reconnect after 3 seconds
      };
    };
    
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // T022: Fetch presets on component mount
  useEffect(() => {
    async function fetchFeePresets() {
      try {
        const response = await fetch("/api/settings/fee-presets?location_id=1");
        if (response.ok) {
          const data = await response.json();
          setFeePresets(data.presets_by_fee_type);
        }
      } catch (error) {
        console.error("Failed to load fee presets:", error);
      } finally {
        setLoadingPresets(false);
      }
    }
    fetchFeePresets();
  }, []);

  const handleAddFee = () => {
    if (newFee.fee_value > 0) {
      const finalLabel = newFee.fee_label.trim() || 
        (FEE_TYPES.find(t => t.value === newFee.fee_type)?.label || newFee.fee_type);
      
      const feeToAdd = { ...newFee, fee_label: finalLabel };
      
      onFeesChange([...fees, feeToAdd]);
      setNewFee({
        fee_type: "shipping",
        fee_label: "",
        fee_value_type: "fixed",
        fee_value: 0,
      });
      setShowForm(false);
    }
  };

  const handleRemoveFee = (index: number) => {
    const newFees = fees.filter((_, i) => i !== index);
    onFeesChange(newFees);
  };

  const handlePresetClick = (amount: number) => {
    setNewFee({ ...newFee, fee_value: amount });
  };

  const QuickAmountButtons = ({ presets, onSelect }: { presets: number[]; onSelect: (amount: number) => void }) => {
    if (loadingPresets) {
      return <div className="text-sm text-slate-400 py-2">{ARABIC.common.loading}</div>;
    }

    if (presets.length === 0) {
      return (
        <div className="text-sm text-slate-500 italic py-2">
          {ARABIC.pos.configurePresets || 'تكوين الإعدادات المسبقة في الإعدادات'}
        </div>
      );
    }

    return (
      <div className="flex flex-wrap gap-2 py-2">
        {presets.map((amount) => (
          <button
            key={amount}
            type="button"
            onClick={() => onSelect(amount)}
            className="px-3 py-1.5 rounded-lg text-sm font-medium bg-slate-100 
                      hover:bg-slate-200 text-slate-700 transition-colors"
          >
            {formatCurrency(amount)}
          </button>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="font-medium">{ARABIC.pos.additionalFees || 'رسوم إضافية'}</h3>
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            className="text-blue-600 hover:text-blue-800 text-sm"
          >
            + {ARABIC.common.add || 'إضافة'}
          </button>
        )}
      </div>

      {fees.length > 0 && (
        <div className="space-y-2">
          {fees.map((fee, index) => (
            <div key={index} className="flex justify-between items-center border rounded p-3">
              <div>
                <div className="font-medium">{fee.fee_label}</div>
                <div className="text-sm text-slate-500">
                  {fee.fee_value_type === "percent" ? `${fee.fee_value}% ${ARABIC.pos.ofSubtotal || 'من المجموع الفرعي'}` : `${formatCurrency(fee.fee_value)} ${ARABIC.pos.fixed || 'ثابت'}`}
                </div>
              </div>
              <button
                onClick={() => handleRemoveFee(index)}
                className="text-red-600 hover:text-red-800 text-sm"
              >
                {ARABIC.common.delete || 'حذف'}
              </button>
            </div>
          ))}
        </div>
      )}

      {showForm && (
        <div className="border rounded p-4 space-y-3">
          <div>
            <label className="block text-sm font-medium mb-1">{ARABIC.pos.feeType || 'نوع الرسوم'}</label>
            <select
              value={newFee.fee_type}
              onChange={(e) => setNewFee({ ...newFee, fee_type: e.target.value as any })}
              className="border rounded px-3 py-2 w-full"
            >
              {FEE_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">{ARABIC.pos.labelOptional || 'التسمية (اختياري)'}</label>
            <input
              type="text"
              value={newFee.fee_label}
              onChange={(e) => setNewFee({ ...newFee, fee_label: e.target.value })}
              placeholder={ARABIC.pos.expressExample || 'مثال: توصيل سريع'}
              className="border rounded px-3 py-2 w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">{ARABIC.pos.valueType || 'نوع القيمة'}</label>
            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="fee_value_type"
                  value="fixed"
                  checked={newFee.fee_value_type === "fixed"}
                  onChange={(e) => setNewFee({ ...newFee, fee_value_type: "fixed" })}
                  className="me-2"
                />
                {ARABIC.pos.fixedAmount || 'مبلغ ثابت'} ({formatCurrency(0)})
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="fee_value_type"
                  value="percent"
                  checked={newFee.fee_value_type === "percent"}
                  onChange={(e) => setNewFee({ ...newFee, fee_value_type: "percent" })}
                  className="me-2"
                />
                {ARABIC.pos.percentage || 'نسبة مئوية'} (%)
              </label>
            </div>
          </div>

          {newFee.fee_value_type === "fixed" && (
            <div>
              <label className="block text-sm font-medium mb-1">{ARABIC.pos.quickAmounts || 'مبالغ سريعة'}</label>
              <QuickAmountButtons
                presets={feePresets[newFee.fee_type]}
                onSelect={handlePresetClick}
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-1">
              {newFee.fee_value_type === "fixed" ? ARABIC.pos.amount || 'المبلغ' : ARABIC.pos.percentage || 'النسبة المئوية'}
            </label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={newFee.fee_value}
              onChange={(e) => setNewFee({ ...newFee, fee_value: parseFloat(e.target.value) || 0 })}
              className="border rounded px-3 py-2 w-full"
            />
          </div>

          <div className="flex justify-end space-x-2">
            <button
              onClick={() => setShowForm(false)}
              className="px-4 py-2 border rounded hover:bg-slate-50"
            >
              {ARABIC.common.cancel || 'إلغاء'}
            </button>
            <button
              onClick={handleAddFee}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              {ARABIC.pos.addFee || 'إضافة الرسوم'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}