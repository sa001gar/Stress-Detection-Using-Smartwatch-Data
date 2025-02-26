import React, { useState } from 'react';
import { Upload, FileUp, Loader2, AlertCircle } from 'lucide-react';

interface PredictionResult {
  Person_Name: string;
  ID: string;
  Age: string;
  Stress_Level: string;
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [results, setResults] = useState<PredictionResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const uploadFile = async () => {
    if (!file) {
      setError("Please select a CSV file.");
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/upload/", {
        method: "POST",
        body: formData
      });

      const data = await response.json();

      if (data.data && Array.isArray(data.data)) {
        setResults(data.data);
      } else {
        setError(data.detail || "Unknown error occurred");
      }
    } catch (err) {
      setError("Failed to upload file. Please check if the server is running.");
    } finally {
      setLoading(false);
    }
  };

  const getStressLevelColor = (level: string) => {
    const numLevel = parseInt(level);
    if (isNaN(numLevel)) return "bg-gray-100";
    
    if (numLevel <= 3) return "bg-green-100 text-green-800";
    if (numLevel <= 6) return "bg-yellow-100 text-yellow-800";
    return "bg-red-100 text-red-800";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-10">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Stress Level Prediction</h1>
            <p className="text-gray-600">Upload a CSV file to predict stress levels</p>
          </div>

          {/* Upload Section */}
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <div className="flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-lg p-8 mb-4 transition-all hover:border-blue-400">
              <Upload className="w-12 h-12 text-gray-400 mb-2" />
              <p className="text-sm text-gray-500 mb-4">
                {file ? file.name : "Drag and drop your CSV file here, or click to browse"}
              </p>
              <label className="relative inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 cursor-pointer transition-colors">
                <FileUp className="w-4 h-4 mr-2" />
                <span>Select CSV File</span>
                <input
                  type="file"
                  id="csvFile"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="sr-only"
                />
              </label>
            </div>

            <div className="flex justify-center">
              <button
                onClick={uploadFile}
                disabled={loading || !file}
                className={`inline-flex items-center px-6 py-3 rounded-md text-white transition-colors ${
                  loading || !file
                    ? "bg-gray-400 cursor-not-allowed"
                    : "bg-indigo-600 hover:bg-indigo-700"
                }`}
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4 mr-2" />
                    Upload and Predict
                  </>
                )}
              </button>
            </div>

            {error && (
              <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md flex items-start">
                <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}
          </div>

          {/* Results Section */}
          {results.length > 0 && (
            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-800">Prediction Results</h2>
                <p className="text-sm text-gray-500">
                  Showing {results.length} prediction{results.length !== 1 ? "s" : ""}
                </p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Person Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Age
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Stress Level
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {results.map((row, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {row.Person_Name || "N/A"}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {row.ID || "N/A"}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {row.Age || "N/A"}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStressLevelColor(row.Stress_Level)}`}>
                            {row.Stress_Level || "N/A"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;