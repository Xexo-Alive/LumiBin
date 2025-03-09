import React, { useState } from "react";
import { uploadImage } from "../api/api";

const ImageUpload: React.FC = () => {
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    interface UploadResult {
        image_url: string;
        latitude: number;
        longitude: number;
    }

    // Handle file selection
    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files[0]) {
            const selectedFile = event.target.files[0];
            setFile(selectedFile);
            setPreview(URL.createObjectURL(selectedFile)); // Show preview
        }
    };

    // Handle file upload
    const handleUpload = async () => {
        if (!file) {
            alert("❌ Please select an image first!");
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const result = await uploadImage(file);
            setUploadResult(result);
        } catch {
            setError("❌ Upload failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-6 border rounded-xl shadow-lg w-96 mx-auto mt-10 bg-white">
            <h2 className="text-xl font-bold text-center">Upload Waste Image</h2>

            {/* File input */}
            <input type="file" onChange={handleFileChange} className="mt-4 w-full" />

            {/* Image Preview */}
            {preview && (
                <div className="mt-4">
                    <p className="text-sm text-gray-600">Preview:</p>
                    <img src={preview} alt="Preview" className="w-full h-auto rounded-lg shadow-md" />
                </div>
            )}

            {/* Upload Button */}
            <button
                onClick={handleUpload}
                className={`mt-4 px-4 py-2 w-full rounded-md text-white ${
                    loading ? "bg-gray-400 cursor-not-allowed" : "bg-green-500 hover:bg-green-600"
                }`}
                disabled={loading}
            >
                {loading ? "Uploading..." : "Upload"}
            </button>

            {/* Error Message */}
            {error && <p className="mt-3 text-red-500 text-center">{error}</p>}

            {/* Upload Result */}
            {uploadResult && (
                <div className="mt-4 p-3 bg-gray-100 rounded-lg">
                    <h3 className="text-lg font-semibold">✅ Upload Successful</h3>
                    <img src={uploadResult.image_url} alt="Uploaded" className="w-full h-auto rounded-lg shadow-md mt-2" />
                    <p><strong>📍 Location:</strong> {uploadResult.latitude}, {uploadResult.longitude}</p>
                    <a href={uploadResult.image_url} target="_blank" rel="noopener noreferrer" className="text-blue-500">View Image</a>
                </div>
            )}
        </div>
    );
};

export default ImageUpload;
