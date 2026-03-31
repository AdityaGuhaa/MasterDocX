import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { FaFileUpload, FaCloudUploadAlt } from 'react-icons/fa';

const DocumentUploader = () => {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setIsUploading(true);
    setUploadResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/v1/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadResult(response.data);

      // Navigate to viewer after successful upload
      if (response.data.status === 'success') {
        setTimeout(() => {
          navigate(`/viewer/${response.data.doc_id}`);
        }, 2000);
      }
    } catch (error) {
      setUploadResult({ error: error.response?.data?.detail || 'Upload failed' });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload Document</h2>
      <p>Select a PDF, DOCX, or TXT file to upload and process with AI</p>

      <form onSubmit={handleSubmit}>
        <div
          className={`upload-area ${dragActive ? 'drag-over' : ''}`}
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
        >
          <FaCloudUploadAlt size={48} style={{ marginBottom: '15px', color: '#94a3b8' }} />
          <p>Drag & drop your file here</p>
          <p>or</p>
          <input
            type="file"
            id="file-input"
            className="file-input"
            onChange={handleFileChange}
            accept=".pdf,.docx,.txt"
          />
          <label htmlFor="file-input" className="upload-button">
            Browse Files
          </label>
          {file && (
            <p style={{ marginTop: '15px', fontSize: '14px' }}>
              Selected: {file.name}
            </p>
          )}
        </div>

        <button
          type="submit"
          className="upload-button"
          disabled={!file || isUploading}
          style={{ width: '100%', padding: '12px' }}
        >
          {isUploading ? 'Processing...' : 'Upload and Process'}
        </button>
      </form>

      {uploadResult && (
        <div
          className="upload-result"
          style={{
            marginTop: '20px',
            padding: '15px',
            borderRadius: '4px',
            backgroundColor: uploadResult.error ? '#fee2e2' : '#dcfce7',
            color: uploadResult.error ? '#b91c1c' : '#15803d',
          }}
        >
          <h3>{uploadResult.error ? 'Error' : 'Success'}</h3>
          <p>{uploadResult.error || uploadResult.message}</p>
          {uploadResult.metadata && (
            <div>
              <p>Document ID: {uploadResult.doc_id}</p>
              <p>Chunks Processed: {uploadResult.metadata.chunk_count}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DocumentUploader;