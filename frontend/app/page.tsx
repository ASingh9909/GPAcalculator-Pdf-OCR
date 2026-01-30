'use client';

import React, { useState } from 'react';
import axios from 'axios';
import { FileUpload } from '@/components/FileUpload';
import { Results } from '@/components/Results';
import { FileText } from 'lucide-react';

export default function Home() {
  const [result, setResult] = useState<any>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      // Assuming backend is on port 8000
      const response = await axios.post('http://127.0.0.1:8000/calculate-gpa', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResult(response.data);
    } catch (err: any) {
      console.error(err);
      setError("Failed to process PDF. Please ensure backend is running.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center space-y-4">
          <div className="inline-flex items-center justify-center p-3 bg-blue-100 rounded-full mb-4">
            <FileText className="w-8 h-8 text-blue-600" />
          </div>
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight sm:text-5xl">
            PDF GPA Calculator
          </h1>
          <p className="max-w-2xl mx-auto text-lg text-gray-500">
            Upload your transcript PDF. We'll extract your grades, find the grading scale, and calculate your GPA on a 5.0 scale automatically.
          </p>
        </div>

        <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          {!result ? (
            <FileUpload onUpload={handleUpload} isUploading={isUploading} />
          ) : (
            <Results data={result} onReset={() => setResult(null)} />
          )}
        </div>

        <div className="text-center text-xs text-gray-400 mt-12">
          Built with FastAPI & Next.js
        </div>
      </div>
    </main>
  );
}
