
import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { AlertCircle } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const ControlPanel: React.FC = () => {
  const [isConfiguring, setIsConfiguring] = useState(false);
  const { toast } = useToast();

  const handleInitialize = () => {
    setIsConfiguring(true);
    toast({
      title: "Backend Configuration Required",
      description: "To run quantum computations, you need to set up a backend server with Qiskit or configure IBM Quantum API credentials.",
      variant: "destructive",
      duration: 5000,
    });
    setIsConfiguring(false);
  };

  return (
    <Card className="p-6 bg-white/80 backdrop-blur-lg border border-gray-200">
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold mb-4">Control Panel</h3>
          <div className="space-y-4">
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex gap-2">
                <AlertCircle className="h-5 w-5 text-yellow-600" />
                <p className="text-sm text-yellow-700">
                  Backend configuration required. Please set up IBM Quantum API credentials.
                </p>
              </div>
            </div>

            {/* IBM Quantum API Key */}
            <div className="space-y-2">
              <Label htmlFor="ibm-api-key">IBM Quantum API Key</Label>
              <Input 
                id="ibm-api-key"
                type="password"
                placeholder="Enter your IBM Quantum API key"
                className="font-mono"
              />
            </div>

            {/* Backend Selection */}
            <div className="space-y-2">
              <Label>Quantum Backend</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select backend" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ibm_sherbrooke">IBM Sherbrooke</SelectItem>
                  <SelectItem value="ibm_brisbane">IBM Brisbane</SelectItem>
                  <SelectItem value="ibm_kyoto">IBM Kyoto</SelectItem>
                  <SelectItem value="ibm_quebec">IBM Quebec</SelectItem>
                  <SelectItem value="simulator_stabilizer">Stabilizer Simulator</SelectItem>
                  <SelectItem value="simulator_statevector">Statevector Simulator</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Target Bitcoin Address */}
            <div className="space-y-2">
              <Label htmlFor="target-address">Target Address</Label>
              <Input 
                id="target-address"
                placeholder="Enter Bitcoin address"
                className="font-mono"
              />
            </div>

            {/* Number of Shots */}
            <div className="space-y-2">
              <Label htmlFor="shots">Number of Shots</Label>
              <Input 
                id="shots"
                type="number"
                defaultValue="8192"
                min="1"
                max="100000"
                className="font-mono"
              />
              <p className="text-xs text-gray-500">Number of times to run the circuit (1-100,000)</p>
            </div>

            {/* Number of Qubits */}
            <div className="space-y-2">
              <Label>Number of Qubits</Label>
              <Slider 
                defaultValue={[18]} 
                max={20} 
                min={1} 
                step={1}
                className="py-4"
              />
              <div className="flex justify-between text-sm text-gray-500">
                <span>1</span>
                <span>20</span>
              </div>
            </div>

            {/* Optimization Level */}
            <div className="space-y-2">
              <Label>Optimization Level</Label>
              <Select defaultValue="3">
                <SelectTrigger>
                  <SelectValue placeholder="Select optimization level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0">Level 0 (No optimization)</SelectItem>
                  <SelectItem value="1">Level 1 (Light optimization)</SelectItem>
                  <SelectItem value="2">Level 2 (Medium optimization)</SelectItem>
                  <SelectItem value="3">Level 3 (Heavy optimization)</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-gray-500">Circuit optimization level (higher = better but slower)</p>
            </div>

            {/* Initialize Button */}
            <div className="pt-4">
              <Button 
                className="w-full" 
                onClick={handleInitialize}
                disabled={isConfiguring}
              >
                {isConfiguring ? 'Configuring...' : 'Initialize Circuit'}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default ControlPanel;
