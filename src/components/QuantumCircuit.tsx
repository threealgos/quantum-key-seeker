
import React from 'react';
import { Card } from '@/components/ui/card';
import { AlertCircle } from 'lucide-react';

const QuantumCircuit: React.FC = () => {
  return (
    <Card className="p-6 bg-white/80 backdrop-blur-lg border border-gray-200">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Quantum Circuit Visualization</h3>
          <span className="text-sm text-gray-500">18 qubits</span>
        </div>
        <div className="h-[200px] w-full bg-gray-50 rounded-lg border border-gray-100 flex flex-col items-center justify-center gap-3">
          <AlertCircle className="h-6 w-6 text-gray-400" />
          <div className="text-center">
            <p className="text-gray-400">Circuit visualization unavailable</p>
            <p className="text-sm text-gray-400 mt-1">Configure IBM Quantum API to visualize circuits</p>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default QuantumCircuit;
