const BASE_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:5000"; // Ensure backend URL is correct

// ✅ Upload Image to Flask Backend
export const uploadImage = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(`${BASE_URL}/upload`, {
            method: "POST",
            body: formData
        });

        return await response.json();
    } catch (error) {
        console.error("❌ Upload failed:", error);
        return null;
    }
};