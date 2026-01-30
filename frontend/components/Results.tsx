'use client';

import React from 'react';
import { CheckCircle, AlertCircle } from 'lucide-react';

interface Course {
    raw_line: string;
    grade: string;
    credit: number;
    points: number;
}

interface AnalysisResultProps {
    data: {
        filename: string;
        extracted_scale: Record<string, number>;
        scale_source_max_detected: number;
        courses_found: number;
        courses: Course[];
        raw_gpa: number;
        final_gpa_5_scale: number;
    };
    onReset: () => void;
}

export const Results: React.FC<AnalysisResultProps> = ({ data, onReset }) => {
    return (
        <div className="space-y-8 animate-fade-in">
            <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
                <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-8 text-white text-center">
                    <h2 className="text-3xl font-bold mb-2">Calculated GPA</h2>
                    <div className="text-6xl font-extrabold tracking-tight">
                        {data.final_gpa_5_scale.toFixed(2)}
                        <span className="text-2xl font-normal text-blue-200 ml-2">/ 5.0</span>
                    </div>
                    <p className="mt-4 text-blue-100">
                        Based on {data.courses_found} courses found in {data.filename}
                    </p>
                </div>

                <div className="p-8 grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                            <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                            Extraction Details
                        </h3>
                        <dl className="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
                            <div className="sm:col-span-1">
                                <dt className="text-sm font-medium text-gray-500">Source Scale Max</dt>
                                <dd className="mt-1 text-sm text-gray-900">{data.scale_source_max_detected.toFixed(1)}</dd>
                            </div>
                            <div className="sm:col-span-1">
                                <dt className="text-sm font-medium text-gray-500">Raw GPA (Source)</dt>
                                <dd className="mt-1 text-sm text-gray-900">{data.raw_gpa.toFixed(2)}</dd>
                            </div>
                        </dl>

                        <div className="mt-6">
                            <h4 className="text-sm font-medium text-gray-900 mb-2">Grading Scale Used</h4>
                            <div className="bg-gray-50 rounded-lg p-3 text-xs font-mono h-32 overflow-y-auto border border-gray-200">
                                {Object.entries(data.extracted_scale).length > 0 ? (
                                    <div className="grid grid-cols-2 gap-2">
                                        {Object.entries(data.extracted_scale).map(([k, v]) => (
                                            <div key={k}>{k}: {v}</div>
                                        ))}
                                    </div>
                                ) : (
                                    <span className="text-amber-600 flex items-center">
                                        <AlertCircle className="w-4 h-4 mr-1" />
                                        Default parsing scale used (no explicit scale found)
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>

                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Courses Detected</h3>
                        <div className="bg-gray-50 rounded-lg border border-gray-200 overflow-hidden h-64 overflow-y-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-100">
                                    <tr>
                                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Line Match</th>
                                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Grade</th>
                                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Credit</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {data.courses.map((course, idx) => (
                                        <tr key={idx} className="hover:bg-gray-50">
                                            <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500 truncate max-w-[150px]" title={course.raw_line}>
                                                {course.raw_line}
                                            </td>
                                            <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900">
                                                {course.grade}
                                            </td>
                                            <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500">
                                                {course.credit}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div className="bg-gray-50 px-8 py-4 border-t border-gray-200 flex justify-end">
                    <button
                        onClick={onReset}
                        className="text-sm font-medium text-blue-600 hover:text-blue-500"
                    >
                        Upload Another PDF
                    </button>
                </div>
            </div>
        </div>
    );
};
