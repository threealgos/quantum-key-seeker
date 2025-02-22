
import React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

interface ResultsDisplayProps {
  isLoading?: boolean;
  results?: Record<string, number>;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ isLoading, results }) => {
  return (
    <Card className="p-6 bg-white/80 backdrop-blur-lg border border-gray-200">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Results</h3>
          <Button variant="outline" size="sm" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing
              </>
            ) : (
              'Export Results'
            )}
          </Button>
        </div>
        <div className="h-[200px] w-full bg-gray-50 rounded-lg border border-gray-100 flex items-center justify-center">
          {isLoading ? (
            <div className="flex flex-col items-center space-y-2">
              <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              <p className="text-sm text-gray-400">Processing quantum computation...</p>
            </div>
          ) : (
            <p className="text-gray-400">Results will appear here</p>
          )}
        </div>
      </div>
    </Card>
  );
};

export default ResultsDisplay;
