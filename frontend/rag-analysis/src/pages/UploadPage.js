import React, { useState } from "react";
import "./UploadPage.css";
import { useNavigate } from "react-router-dom";
import uploadIcon from "../assets/file_img.png";
import loadingGIF from "../assets/cheems_loading.gif";
import bgImage from "../assets/bg_upload.jpg"; // Import background image

const UploadPage = () => {
    const navigate = useNavigate();
    const [selectedFile, setSelectedFile] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleFileChange = (event) => {
        const file = event.target.files[0];

        if (file && validateFileType(file)) {
            setSelectedFile(file);
        } else {
            alert("Only PDF and Word documents are allowed!");
        }
    };

    const validateFileType = (file) => {
        const allowedExtensions = [".pdf", ".docx"];
        return allowedExtensions.some((ext) =>
            file.name.toLowerCase().endsWith(ext)
        );
    };

    const handleDragOver = (event) => {
        event.preventDefault();
    };

    const handleDrop = (event) => {
        event.preventDefault();
        const file = event.dataTransfer.files[0];
        if (file && validateFileType(file)) {
            setSelectedFile(file);
        } else {
            alert("Only PDF and Word documents are allowed");
        }
    };

    const handleUploadClick = async () => {
        if (!selectedFile) {
            alert("Please select a file first");
            return;
        }

        const formData = new FormData();
        formData.append("file", selectedFile);
        setIsLoading(true);

        const BACKEND_URL = "https://rag-analysis.onrender.com";

        try {
            const response = await fetch(`${BACKEND_URL}/upload/`, {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                alert(`Upload Successful`);
                navigate("/analysis");
            } else {
                setSelectedFile(null);
                alert(`Upload Failed: ${data.detail || "Unknown error"}`);
            }
        } catch (error) {
            console.error("Upload error:", error);
            alert("Failed to upload the file. Please try again");
        } finally {
            setIsLoading(false);
        }
    };

    const handleRemoveFile = (event) => {
        event.stopPropagation();
        setSelectedFile(null);
        document.getElementById("fileInput").value = "";
    };

    const uploadContainerStyle = {
        backgroundImage: `url(${bgImage})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
    };

    return (
        <div className="upload-container" style={uploadContainerStyle}>
            <h2>Upload the files here for processing</h2>
            <div
                className="upload-box"
                onClick={() => document.getElementById("fileInput").click()}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
            >
                <img src={uploadIcon} alt="Upload" className="upload-icon" />
                <p className="upload-text">
                    {selectedFile
                        ? `Selected: ${selectedFile.name}`
                        : "Drag & drop a file or click to upload a file"}
                </p>

                <input
                    type="file"
                    id="fileInput"
                    className="file-input"
                    onChange={handleFileChange}
                    accept=".pdf, .docx"
                />
                {selectedFile && (
                    <button
                        className="remove-button"
                        onClick={handleRemoveFile}
                    >
                        Remove File
                    </button>
                )}
            </div>
            <button
                className="upload-button"
                onClick={handleUploadClick}
                disabled={isLoading}
            >
                {isLoading ? "Uploading..." : "Upload"}
            </button>
            {isLoading && (
                <div className="loading-overlay">
                    <img
                        src={loadingGIF}
                        alt="Loading..."
                        className="loading-spinner"
                    />
                    <p>Processing File, Please Wait...</p>
                </div>
            )}
        </div>
    );
};

export default UploadPage;
