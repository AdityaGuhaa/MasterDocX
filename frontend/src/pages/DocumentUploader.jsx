// Copyright (c) 2026 Aditya Guha
// SPDX-License-Identifier: MIT

import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { FiUploadCloud, FiFileText, FiX, FiLock, FiAlertCircle, FiCheckCircle } from 'react-icons/fi';

const formatSize = (bytes) => {
  if (bytes < 1024) return `${bytes} bytes`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const DocumentUploader = () => {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const navigate = useNavigate();

  const chooseFile = (picked) => {
    if (picked) {
      setFile(picked);
      setUploadResult(null);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      chooseFile(e.target.files[0]);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      chooseFile(e.dataTransfer.files[0]);
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

      if (response.data.status === 'error') {
        setUploadResult({ error: response.data.message });
        return;
      }

      setUploadResult(response.data);

      // Open the viewer after a successful upload (or if already processed)
      if (response.data.status === 'success' || response.data.status === 'already_processed') {
        setTimeout(() => {
          navigate(`/viewer/${encodeURIComponent(response.data.doc_id)}`);
        }, 1200);
      }
    } catch (error) {
      setUploadResult({ error: error.response?.data?.detail || 'Upload failed. Is the backend running?' });
    } finally {
      setIsUploading(false);
    }
  };

  const succeeded = uploadResult && !uploadResult.error;

  return (
    <div className="uploader">
      <section className="hero">
        <h1 className="rise">
          Your documents.
          <br />
          <span className="gradient">Understood.</span>
        </h1>
        <p className="rise rise-1">
          Ask questions, get summaries, and see the ideas inside any PDF, Word document or text file.
        </p>
      </section>

      <form className="upload-panel card rise rise-2" onSubmit={handleSubmit}>
        <label
          htmlFor="file-input"
          className={`dropzone ${dragActive ? 'is-dragging' : ''}`}
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
        >
          <span className="dropzone-icon">
            <FiUploadCloud size={26} />
          </span>
          <span className="dropzone-title">{dragActive ? 'Drop to add' : 'Drop a document here'}</span>
          <span className="dropzone-hint">
            or <span style={{ color: 'var(--accent)' }}>browse your files</span>
          </span>
          <input
            type="file"
            id="file-input"
            className="file-input"
            onChange={handleFileChange}
            accept=".pdf,.docx,.txt"
          />
        </label>

        {file && (
          <div className="file-chip fade">
            <span className="file-chip-icon">
              <FiFileText size={20} />
            </span>
            <div className="file-chip-body">
              <div className="file-chip-name">{file.name}</div>
              <div className="file-chip-meta">{formatSize(file.size)}</div>
            </div>
            {!isUploading && !succeeded && (
              <button
                type="button"
                className="file-chip-remove"
                onClick={() => setFile(null)}
                aria-label="Remove file"
              >
                <FiX size={16} />
              </button>
            )}
          </div>
        )}

        <div className="upload-actions">
          <button type="submit" className="btn btn-primary btn-block" disabled={!file || isUploading || succeeded}>
            {isUploading ? (
              <>
                <span className="spinner" /> Reading your document…
              </>
            ) : succeeded ? (
              'Opening…'
            ) : (
              'Continue'
            )}
          </button>
        </div>

        {uploadResult?.error && (
          <div className="notice notice-error fade">
            <FiAlertCircle size={18} />
            <span>{uploadResult.error}</span>
          </div>
        )}

        {succeeded && (
          <div className="notice notice-success fade">
            <FiCheckCircle size={18} />
            <span>
              {uploadResult.status === 'already_processed'
                ? 'You’ve added this document before. Opening it now.'
                : `Ready. Split into ${uploadResult.metadata?.chunk_count} section${uploadResult.metadata?.chunk_count === 1 ? '' : 's'} for search.`}
            </span>
          </div>
        )}
      </form>

      <div className="formats rise rise-3">
        <span className="format-pill">PDF</span>
        <span className="format-pill">DOCX</span>
        <span className="format-pill">TXT</span>
      </div>
      <p className="privacy-note rise rise-3">
        <FiLock size={12} /> Processed on this computer. Nothing is uploaded to the cloud.
      </p>
    </div>
  );
};

export default DocumentUploader;
