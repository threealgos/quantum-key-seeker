
import { Card } from '@/components/ui/card';
import { Bitcoin, Info } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const DonationCard = () => {
  return (
    <Card className="p-6 bg-white/80 backdrop-blur-lg border border-gray-200">
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-2">
          <Bitcoin className="h-6 w-6 text-orange-500" />
          <h3 className="text-lg font-semibold">Support Quantum Key Seeker</h3>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <Info className="h-4 w-4 text-gray-400" />
              </TooltipTrigger>
              <TooltipContent>
                <p className="w-[200px] text-sm">
                  Your donations help maintain and improve the quantum computing infrastructure
                </p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
        <p className="text-gray-600 max-w-lg mx-auto text-sm">
          This project utilizes quantum computing to solve complex cryptographic problems.
          Your support helps maintain the quantum infrastructure and further development.
        </p>
        <div className="bg-gray-50 p-4 rounded-lg inline-block">
          <code className="font-mono text-sm select-all">
            1NEJcwfcEm7Aax8oJNjRUnY3hEavCjNrai
          </code>
        </div>
        <p className="text-xs text-gray-400">
          Click the address to copy
        </p>
      </div>
    </Card>
  );
};

export default DonationCard;
