/**
 * FeeEditor Component
 * 
 * Add/edit fixed or percentage fees to the sale.
 */

"use client";

import { useState, useEffect, useRef } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency } from "@/lib/utils/format";
import NumberInput from "@/components/shared/NumberInput";

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

  const [feePresets, setFeePresets] = useState<FeePresetsConfig>({
    shipping: [],
    installation: [],
    custom: [],
  });
  const [loadingPresets, setLoadingPresets] = useState(true);

  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const connectWebSocket = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/stock-updates`;
      
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
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
      
      wsRef.current.onclose = () => {
        setTimeout(connectWebSocket, 3000);
      };
    };
    
    connectWebSocket();
    
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

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
      
      onFeesChange([...fees, { ...newFee, fee_label: finalLabel }]);
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
    onFeesChange(fees.filter((_, i) => i !== index));
  };

  const QuickAmountButtons = ({ presets, onSelect }: { presets: number[]; onSelect: (amount: number) => void }) => {
    if (loadingPresets) return <div className="text-sm text-slate-400 py-2">{ARABIC.common.loading}</div>;
    if (presets.length === 0) return <div className="text-sm text-slate-500 italic py-2">{ARABIC.pos.configurePresets || 'تكوين الإعدادات المسبقة في الإعدادات'}</div>;

    return (
      <div className="flex flex-wrap gap-2 py-2">
        {presets.map((amount) => (
          <button
            key={amount}
            type="button"
            onClick={() => onSelect(amount)}
            className="px-3 py-1.5 rounded-lg text-sm font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors"
          >
            {formatCurrency(amount)}
          </button>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-4 text-start">
      <div className="flex justify-between items-center">
        <h3 className="font-medium text-slate-700">{ARABIC.pos.additionalFees || 'رسوم إضافية'}</h3>
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            className="text-blue-600 hover:text-blue-800 text-sm font-bold"
          >
            + {ARABIC.common.add || 'إضافة'}
          </button>
        )}
      </div>

      {fees.length > 0 && (
        <div className="space-y-2">
          {fees.map((fee, index) => (
            <div key={index} className="flex justify-between items-center bg-slate-50 border border-slate-100 rounded-xl p-3">
              <div>
                <div className="font-bold text-slate-800">{fee.fee_label}</div>
                <div className="text-xs text-slate-500">
                  {fee.fee_value_type === "percent" ? `${fee.fee_value}% ${ARABIC.pos.ofSubtotal || 'من المجموع الفرعي'}` : `${formatCurrency(fee.fee_value)} ${ARABIC.pos.fixed || 'ثابت'}`}
                </div>
              </div>
              <button
                onClick={() => handleRemoveFee(index)}
                className="p-2 text-rose-500 hover:bg-rose-50 rounded-lg transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
              </button>
            </div>
          ))}
        </div>
      )}

      {showForm && (
        <div className="glass border-slate-200 rounded-2xl p-5 space-y-4 shadow-sm">
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">{ARABIC.pos.feeType || 'نوع الرسوم'}</label>
            <select
              value={newFee.fee_type}
              onChange={(e) => setNewFee({ ...newFee, fee_type: e.target.value as any })}
              className="w-full bg-white border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500"
            >
              {FEE_TYPES.map((type) => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">{ARABIC.pos.labelOptional || 'التسمية (اختياري)'}</label>
            <input
              type="text"
              value={newFee.fee_label}
              onChange={(e) => setNewFee({ ...newFee, fee_label: e.target.value })}
              placeholder={ARABIC.pos.expressExample || 'مثال: توصيل سريع'}
              className="w-full bg-white border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">{ARABIC.pos.valueType || 'نوع القيمة'}</label>
            <div className="flex gap-4 p-1 bg-slate-100 rounded-xl">
              <button
                type="button"
                onClick={() => setNewFee({ ...newFee, fee_value_type: "fixed" })}
                className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${newFee.fee_value_type === 'fixed' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500'}`}
              >
                {ARABIC.pos.fixedAmount || 'مبلغ ثابت'}
              </button>
              <button
                type="button"
                onClick={() => setNewFee({ ...newFee, fee_value_type: "percent" })}
                className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${newFee.fee_value_type === 'percent' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500'}`}
              >
                {ARABIC.pos.percentage || 'نسبة مئوية'}
              </button>
            </div>
          </div>

          {newFee.fee_value_type === "fixed" && (
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">{ARABIC.pos.quickAmounts || 'مبالغ سريعة'}</label>
              <QuickAmountButtons
                presets={feePresets[newFee.fee_type]}
                onSelect={(amount) => setNewFee({ ...newFee, fee_value: amount })}
              />
            </div>
          )}

          <NumberInput
            label={newFee.fee_value_type === "fixed" ? ARABIC.pos.amount || 'المبلغ' : ARABIC.pos.percentage || 'النسبة المئوية'}
            suffix={newFee.fee_value_type === "fixed" ? "ج.س" : "%"}
            value={newFee.fee_value}
            onChange={(val) => setNewFee({ ...newFee, fee_value: val })}
          />

          <div className="flex justify-end gap-3 pt-2">
            <button
              onClick={() => setShowForm(false)}
              className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-xl"
            >
              {ARABIC.common.cancel || 'إلغاء'}
            </button>
            <button
              onClick={handleAddFee}
              className="px-6 py-2 bg-blue-600 text-white text-sm font-bold rounded-xl hover:bg-blue-700 shadow-lg shadow-blue-100"
            >
              {ARABIC.pos.addFee || 'إضافة الرسوم'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}