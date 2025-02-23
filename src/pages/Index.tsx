
import React from 'react';
import QuantumCircuit from '@/components/QuantumCircuit';
import ResultsDisplay from '@/components/ResultsDisplay';
import ControlPanel from '@/components/ControlPanel';
import { Bitcoin } from 'lucide-react';
import { Card } from '@/components/ui/card';

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <header className="text-center space-y-4">
          <h1 className="text-4xl font-semibold tracking-tight">
            Quantum Key Seeker
          </h1>
          <p className="text-gray-500 max-w-2xl mx-auto">
            A quantum computing interface for ECDLP solving, powered by advanced quantum algorithms
            and real quantum hardware.
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-2 space-y-8">
            <QuantumCircuit />
            <ResultsDisplay />
          </div>
          <div>
            <ControlPanel />
          </div>
        </div>

        {/* Donation Section */}
        <Card className="p-6 bg-white/80 backdrop-blur-lg border border-gray-200">
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center gap-2">
              <Bitcoin className="h-6 w-6 text-orange-500" />
              <h3 className="text-lg font-semibold">Support Quantum Key Seeker</h3>
            </div>
            <p className="text-gray-600">
              If you find this project useful, consider supporting its development:
            </p>
            <div className="bg-gray-50 p-4 rounded-lg inline-block">
              <code className="font-mono text-sm">
                1NEJcwfcEm7Aax8oJNjRUnY3hEavCjNrai
              </code>
            </div>
          </div>
        </Card>

        <footer className="text-center text-sm text-gray-400 pt-8">
          <p>Running on IBM Quantum Hardware</p>
        </footer>
      </div>
    </div>
  );
};

export default Index;
