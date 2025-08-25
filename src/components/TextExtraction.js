import React, { useState, useRef } from 'react';
import textExtractionService from '../services/textExtractionService';
import './TextExtraction.css';

const TextExtraction = ({ onBack }) => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [extractedText, setExtractedText] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState('');
    const [ocrOptions, setOcrOptions] = useState({
        engine: 'auto',
        preprocess: true,
        detect_regions: false
    });
    const [extractionResult, setExtractionResult] = useState(null);
    const [availableEngines, setAvailableEngines] = useState([]);
    const [serviceStatus, setServiceStatus] = useState(null);
    
    const fileInputRef = useRef(null);

    // Load service information on component mount
    React.useEffect(() => {
        loadServiceInfo();
    }, []);

    const loadServiceInfo = async () => {
        try {
            const [engines, status] = await Promise.all([
                textExtractionService.getAvailableEngines(),
                textExtractionService.getServiceStatus()
            ]);
            setAvailableEngines(engines.engines || []);
            setServiceStatus(status);
        } catch (error) {
            console.error('Failed to load service info:', error);
        }
    };

    const handleFileSelect = (event) => {
        const file = event.target.files[0];
        if (file) {
            // Validate file type
            if (!file.type.startsWith('image/')) {
                setError('Please select an image file (JPG, PNG, BMP, etc.)');
                return;
            }

            // Validate file size (max 10MB)
            if (file.size > 10 * 1024 * 1024) {
                setError('File size too large. Please select an image smaller than 10MB.');
                return;
            }

            setSelectedFile(file);
            setError('');
            
            // Create preview URL
            const url = URL.createObjectURL(file);
            setPreviewUrl(url);
            
            // Clear previous results
            setExtractedText('');
            setExtractionResult(null);
        }
    };

    const handleExtractText = async () => {
        if (!selectedFile) {
            setError('Please select an image file first.');
            return;
        }

        setIsProcessing(true);
        setError('');
        setExtractedText('');

        try {
            console.log('🚀 Starting text extraction with options:', ocrOptions);
            
            const result = await textExtractionService.extractTextFromFile(selectedFile, ocrOptions);
            
            if (result.success) {
                setExtractedText(result.text);
                setExtractionResult(result);
                console.log('✅ Text extraction completed successfully');
            } else {
                setError(`Text extraction failed: ${result.error}`);
                console.error('❌ Text extraction failed:', result.error);
            }
        } catch (error) {
            setError(`Error: ${error.message}`);
            console.error('❌ Text extraction error:', error);
        } finally {
            setIsProcessing(false);
        }
    };

    const handleClear = () => {
        setSelectedFile(null);
        setPreviewUrl(null);
        setExtractedText('');
        setExtractionResult(null);
        setError('');
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const handleCopyText = () => {
        if (extractedText) {
            navigator.clipboard.writeText(extractedText);
            // You could add a toast notification here
            alert('Text copied to clipboard!');
        }
    };

    const handleDownloadText = () => {
        if (extractedText) {
            const blob = new Blob([extractedText], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `extracted_text_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    };

    return (
                <div className="text-extraction-container">
          <div className="text-extraction-header">
            <div className="header-content">
              <button onClick={onBack} className="back-button">
                ← Back to Chat
              </button>
              <h2>📄 Text Extraction from Images</h2>
              <p>Extract text from printed documents, handwritten notes, and images</p>
            </div>
          </div>

            {/* Service Status */}
            {serviceStatus && (
                <div className="service-status">
                    <h3>🔧 Service Status</h3>
                    <div className="status-grid">
                        <div className="status-item">
                            <span className="status-label">Status:</span>
                            <span className={`status-value ${serviceStatus.status === 'active' ? 'active' : 'inactive'}`}>
                                {serviceStatus.status}
                            </span>
                        </div>
                        <div className="status-item">
                            <span className="status-label">Available Engines:</span>
                            <span className="status-value">
                                {availableEngines.length > 0 ? availableEngines.join(', ') : 'None'}
                            </span>
                        </div>
                    </div>
                </div>
            )}

            {/* File Upload Section */}
            <div className="upload-section">
                <h3>📁 Upload Image</h3>
                <div className="file-input-container">
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        onChange={handleFileSelect}
                        className="file-input"
                        id="image-upload"
                    />
                    <label htmlFor="image-upload" className="file-input-label">
                        📷 Choose Image File
                    </label>
                </div>
                
                {selectedFile && (
                    <div className="file-info">
                        <p><strong>Selected File:</strong> {selectedFile.name}</p>
                        <p><strong>Size:</strong> {(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                        <p><strong>Type:</strong> {selectedFile.type}</p>
                    </div>
                )}
            </div>

            {/* Image Preview */}
            {previewUrl && (
                <div className="preview-section">
                    <h3>🖼️ Image Preview</h3>
                    <div className="image-preview">
                        <img src={previewUrl} alt="Preview" className="preview-image" />
                    </div>
                </div>
            )}

            {/* OCR Options */}
            <div className="ocr-options">
                <h3>⚙️ OCR Options</h3>
                <div className="options-grid">
                    <div className="option-item">
                        <label htmlFor="engine-select">OCR Engine:</label>
                        <select
                            id="engine-select"
                            value={ocrOptions.engine}
                            onChange={(e) => setOcrOptions({...ocrOptions, engine: e.target.value})}
                            className="option-select"
                        >
                            <option value="auto">Auto-select (Recommended)</option>
                            {availableEngines.includes('tesseract') && (
                                <option value="tesseract">Tesseract (Printed Text)</option>
                            )}
                            {availableEngines.includes('easyocr') && (
                                <option value="easyocr">EasyOCR (General)</option>
                            )}
                            {availableEngines.includes('trocr') && (
                                <option value="trocr">TrOCR (Handwritten)</option>
                            )}
                        </select>
                    </div>
                    
                    <div className="option-item">
                        <label htmlFor="preprocess-checkbox">
                            <input
                                type="checkbox"
                                id="preprocess-checkbox"
                                checked={ocrOptions.preprocess}
                                onChange={(e) => setOcrOptions({...ocrOptions, preprocess: e.target.checked})}
                            />
                            Enable Image Preprocessing
                        </label>
                    </div>
                    
                    <div className="option-item">
                        <label htmlFor="detect-regions-checkbox">
                            <input
                                type="checkbox"
                                id="detect-regions-checkbox"
                                checked={ocrOptions.detect_regions}
                                onChange={(e) => setOcrOptions({...ocrOptions, detect_regions: e.target.checked})}
                            />
                            Detect Text Regions
                        </label>
                    </div>
                </div>
            </div>

            {/* Action Buttons */}
            <div className="action-buttons">
                <button
                    onClick={handleExtractText}
                    disabled={!selectedFile || isProcessing}
                    className="extract-button"
                >
                    {isProcessing ? '🔄 Processing...' : '🔍 Extract Text'}
                </button>
                
                <button
                    onClick={handleClear}
                    disabled={!selectedFile}
                    className="clear-button"
                >
                    🗑️ Clear
                </button>
            </div>

            {/* Error Display */}
            {error && (
                <div className="error-message">
                    ❌ {error}
                </div>
            )}

            {/* Extracted Text Display */}
            {extractedText && (
                <div className="extracted-text-section">
                    <div className="text-header">
                        <h3>📝 Extracted Text</h3>
                        <div className="text-actions">
                            <button onClick={handleCopyText} className="action-button">
                                📋 Copy
                            </button>
                            <button onClick={handleDownloadText} className="action-button">
                                💾 Download
                            </button>
                        </div>
                    </div>
                    
                    <div className="text-content">
                        <pre className="extracted-text">{extractedText}</pre>
                    </div>
                </div>
            )}

            {/* Extraction Results Details */}
            {extractionResult && (
                <div className="results-details">
                    <h3>📊 Extraction Details</h3>
                    <div className="details-grid">
                        <div className="detail-item">
                            <span className="detail-label">Engine Used:</span>
                            <span className="detail-value">{extractionResult.engine_used}</span>
                        </div>
                        <div className="detail-item">
                            <span className="detail-label">Confidence:</span>
                            <span className="detail-value">
                                {(extractionResult.confidence * 100).toFixed(1)}%
                            </span>
                        </div>
                        <div className="detail-item">
                            <span className="detail-label">Text Regions:</span>
                            <span className="detail-value">
                                {extractionResult.regions ? extractionResult.regions.length : 0}
                            </span>
                        </div>
                        <div className="detail-item">
                            <span className="detail-label">Processing Time:</span>
                            <span className="detail-value">
                                {extractionResult.timestamp ? new Date(extractionResult.timestamp).toLocaleTimeString() : 'N/A'}
                            </span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TextExtraction;
