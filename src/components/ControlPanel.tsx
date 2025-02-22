
import React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';

const ControlPanel: React.FC = () => {
  return (
    <Card className="p-6 bg-white/80 backdrop-blur-lg border border-gray-200">
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold mb-4">Control Panel</h3>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="target-address">Target Address</Label>
              <Input 
                id="target-address"
                placeholder="Enter Bitcoin address"
                className="font-mono"
              />
            </div>
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
            <div className="pt-4">
              <Button className="w-full">
                Initialize Circuit
              </Button>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default ControlPanel;
