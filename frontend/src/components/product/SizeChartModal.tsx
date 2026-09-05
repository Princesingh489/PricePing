import React, { useState } from 'react';
import { X, Ruler } from 'lucide-react';

interface SizeChartModalProps {
  isOpen: boolean;
  onClose: () => void;
  productType?: 'footwear' | 'clothing';
}

interface FootwearSize {
  uk: string;
  us: string;
  eu: string;
  cm: string;
  inches: string;
}

const FOOTWEAR_SIZES: FootwearSize[] = [
  { uk: '6', us: '7', eu: '40', cm: '24.5', inches: '9.6' },
  { uk: '7', us: '8', eu: '41', cm: '25.4', inches: '10.0' },
  { uk: '8', us: '9', eu: '42', cm: '26.0', inches: '10.2' },
  { uk: '9', us: '10', eu: '43', cm: '27.0', inches: '10.6' },
  { uk: '10', us: '11', eu: '44', cm: '27.9', inches: '11.0' },
  { uk: '11', us: '12', eu: '45', cm: '28.8', inches: '11.3' },
  { uk: '12', us: '13', eu: '46', cm: '29.7', inches: '11.7' },
];

interface ClothingSize {
  size: string;
  chest: string;
  waist: string;
  length: string;
  shoulder: string;
}

const CLOTHING_SIZES: ClothingSize[] = [
  { size: 'S', chest: '36-38 in (91-96 cm)', waist: '30-32 in', length: '27.5 in', shoulder: '17.0 in' },
  { size: 'M', chest: '38-40 in (96-101 cm)', waist: '32-34 in', length: '28.5 in', shoulder: '17.5 in' },
  { size: 'L', chest: '40-42 in (101-106 cm)', waist: '34-36 in', length: '29.5 in', shoulder: '18.0 in' },
  { size: 'XL', chest: '42-44 in (106-111 cm)', waist: '36-38 in', length: '30.5 in', shoulder: '18.5 in' },
  { size: 'XXL', chest: '44-46 in (111-116 cm)', waist: '38-40 in', length: '31.5 in', shoulder: '19.0 in' },
];

export const SizeChartModal: React.FC<SizeChartModalProps> = ({
  isOpen,
  onClose,
  productType = 'footwear',
}) => {
  const [activeTab, setActiveTab] = useState<'footwear' | 'clothing'>(productType);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn"
      onClick={onClose}
    >
      <div
        className="bg-white dark:bg-gray-800 rounded-2xl max-w-2xl w-full shadow-2xl overflow-hidden border border-gray-100 dark:border-gray-700"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <Ruler className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">
              Official Size Chart & Guide
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab switcher */}
        <div className="flex border-b border-gray-100 dark:border-gray-700 px-6 pt-3 bg-gray-50/50 dark:bg-gray-900/50">
          <button
            onClick={() => setActiveTab('footwear')}
            className={`pb-3 px-4 text-sm font-semibold border-b-2 transition-colors ${
              activeTab === 'footwear'
                ? 'border-blue-600 text-blue-600 dark:text-blue-400 dark:border-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-800 dark:hover:text-gray-200'
            }`}
          >
            Footwear (Shoes / Sandals)
          </button>
          <button
            onClick={() => setActiveTab('clothing')}
            className={`pb-3 px-4 text-sm font-semibold border-b-2 transition-colors ${
              activeTab === 'clothing'
                ? 'border-blue-600 text-blue-600 dark:text-blue-400 dark:border-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-800 dark:hover:text-gray-200'
            }`}
          >
            Apparel & Clothing
          </button>
        </div>

        {/* Content */}
        <div className="p-6 max-h-[70vh] overflow-y-auto">
          {activeTab === 'footwear' ? (
            <div>
              <div className="overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-700">
                <table className="w-full text-left text-sm">
                  <thead className="bg-gray-50 dark:bg-gray-900 text-gray-600 dark:text-gray-300 font-semibold border-b border-gray-200 dark:border-gray-700">
                    <tr>
                      <th className="px-4 py-3 text-center bg-blue-50/70 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300">
                        UK / India
                      </th>
                      <th className="px-4 py-3 text-center">US</th>
                      <th className="px-4 py-3 text-center">EU</th>
                      <th className="px-4 py-3 text-center">Foot Length (CM)</th>
                      <th className="px-4 py-3 text-center">Foot Length (Inches)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                    {FOOTWEAR_SIZES.map((row) => (
                      <tr
                        key={row.uk}
                        className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                      >
                        <td className="px-4 py-3 text-center font-bold text-gray-900 dark:text-white bg-blue-50/30 dark:bg-blue-900/10">
                          {row.uk}
                        </td>
                        <td className="px-4 py-3 text-center text-gray-700 dark:text-gray-300">
                          {row.us}
                        </td>
                        <td className="px-4 py-3 text-center text-gray-700 dark:text-gray-300">
                          {row.eu}
                        </td>
                        <td className="px-4 py-3 text-center text-gray-700 dark:text-gray-300">
                          {row.cm} cm
                        </td>
                        <td className="px-4 py-3 text-center text-gray-700 dark:text-gray-300">
                          {row.inches}&quot;
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="mt-4 p-4 rounded-xl bg-blue-50 dark:bg-blue-950/40 border border-blue-100 dark:border-blue-900 text-xs text-blue-900 dark:text-blue-200 leading-relaxed">
                <p className="font-bold mb-1">💡 How to Measure Your Foot Length:</p>
                <ol className="list-decimal list-inside space-y-1 text-gray-600 dark:text-gray-300">
                  <li>Stand on a blank sheet of paper with your heel against a flat wall.</li>
                  <li>Mark the tip of your longest toe on the paper with a pencil.</li>
                  <li>Measure the distance from the edge of the paper to the mark in centimeters.</li>
                  <li>Compare with the chart above. If you are between sizes, we recommend sizing up.</li>
                </ol>
              </div>
            </div>
          ) : (
            <div>
              <div className="overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-700">
                <table className="w-full text-left text-sm">
                  <thead className="bg-gray-50 dark:bg-gray-900 text-gray-600 dark:text-gray-300 font-semibold border-b border-gray-200 dark:border-gray-700">
                    <tr>
                      <th className="px-4 py-3 text-center bg-blue-50/70 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300">
                        Size
                      </th>
                      <th className="px-4 py-3">Chest (To Fit)</th>
                      <th className="px-4 py-3">Waist</th>
                      <th className="px-4 py-3">Length</th>
                      <th className="px-4 py-3">Shoulder</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                    {CLOTHING_SIZES.map((row) => (
                      <tr
                        key={row.size}
                        className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                      >
                        <td className="px-4 py-3 text-center font-bold text-gray-900 dark:text-white bg-blue-50/30 dark:bg-blue-900/10">
                          {row.size}
                        </td>
                        <td className="px-4 py-3 text-gray-700 dark:text-gray-300">{row.chest}</td>
                        <td className="px-4 py-3 text-gray-700 dark:text-gray-300">{row.waist}</td>
                        <td className="px-4 py-3 text-gray-700 dark:text-gray-300">{row.length}</td>
                        <td className="px-4 py-3 text-gray-700 dark:text-gray-300">{row.shoulder}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="mt-4 p-4 rounded-xl bg-blue-50 dark:bg-blue-950/40 border border-blue-100 dark:border-blue-900 text-xs text-blue-900 dark:text-blue-200 leading-relaxed">
                <p className="font-bold mb-1">💡 How to Measure:</p>
                <ul className="list-disc list-inside space-y-1 text-gray-600 dark:text-gray-300">
                  <li><strong>Chest:</strong> Measure around the fullest part of your chest, keeping tape horizontal.</li>
                  <li><strong>Waist:</strong> Measure around your natural waistline, where trousers usually sit.</li>
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-gray-50 dark:bg-gray-900/50 border-t border-gray-100 dark:border-gray-700 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 text-sm font-semibold rounded-xl bg-gray-900 hover:bg-gray-800 text-white dark:bg-gray-100 dark:text-gray-900 dark:hover:bg-white transition-all shadow-sm"
          >
            Got it
          </button>
        </div>
      </div>
    </div>
  );
};
