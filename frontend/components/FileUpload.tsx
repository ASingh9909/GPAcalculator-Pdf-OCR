'use client';

import React, { useRef, useState } from 'react';
import { Upload, FileText, Loader2 } from 'lucide-react';
import clsx from 'clsx';

interface FileUploadProps {
    onUpload: (file: File) => void;
    isUploading: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUpload, isUploading }) => {
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleFile = (file: File) => {
        if (file.type === 'application/pdf') {
            onUpload(file);
        } else {
            alert('Please upload a PDF file.');
        }
    };

    return (
        <div
            className={clsx(
                "border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors duration-200",
                isDragging ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-blue-400 hover:bg-gray-50",
                isUploading && "opacity-50 cursor-not-allowed"
            )}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => !isUploading && fileInputRef.current?.click()}
        >
            <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                accept=".pdf"
                onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
            />
            <div className="flex flex-col items-center justify-center space-y-4">
                {isUploading ? (
                    <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
                ) : (
                    <Upload className="w-12 h-12 text-gray-400" />
                )}
                <div>
                    <h3 className="text-lg font-medium text-gray-900">
                        {isUploading ? "Processing PDF..." : "Upload your Transcript PDF"}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">
                        Drag and drop or click to browse
                    </p>
                </div>
            </div>
        </div>
    );
};
