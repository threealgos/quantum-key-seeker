
import React from 'react';
import QuantumCircuit from '@/components/QuantumCircuit';
import ResultsDisplay from '@/components/ResultsDisplay';
import ControlPanel from '@/components/ControlPanel';

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

        <footer className="text-center text-sm text-gray-400 pt-8">
          <p>Running on IBM Quantum Hardware</p>
        </footer>
      </div>
    </div>
  );
};

export default Index;
