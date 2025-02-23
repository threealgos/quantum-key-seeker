
import React from 'react';
import QuantumCircuit from '@/components/QuantumCircuit';
import ResultsDisplay from '@/components/ResultsDisplay';
import ControlPanel from '@/components/ControlPanel';
import DonationCard from '@/components/DonationCard';
import { AlertCircle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <header className="text-center space-y-4">
          <h1 className="text-4xl font-semibold tracking-tight">
            Quantum Key Seeker
          </h1>
          <p className="text-gray-500 max-w-2xl mx-auto">
            Advanced quantum computing interface for ECDLP solving using IBM Quantum hardware
          </p>
        </header>

        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Deprecation Notice</AlertTitle>
          <AlertDescription>
            The qiskit.compiler.assembler.assemble() function is deprecated as of Qiskit 1.2. 
            We are working on updating to BackendV2 workflow.
          </AlertDescription>
        </Alert>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-2 space-y-8">
            <QuantumCircuit />
            <ResultsDisplay />
            <DonationCard />
          </div>
          <div className="space-y-8">
            <ControlPanel />
          </div>
        </div>

        <footer className="text-center text-sm text-gray-400 pt-8">
          <p>Running on IBM Quantum Hardware - Using BackendV2 workflow</p>
          <p className="mt-2">Current Backend: IBM Sherbrooke</p>
        </footer>
      </div>
    </div>
  );
};

export default Index;
