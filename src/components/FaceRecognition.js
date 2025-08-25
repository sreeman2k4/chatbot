import React, { useState, useRef, useEffect } from 'react';
import { faceRecognitionService } from '../services/faceRecognitionService';

const FaceRecognition = ({ onLogin, onRegister }) => {
  const [mode, setMode] = useState('login'); // 'login' or 'register'
  const [username, setUsername] = useState('');
  const [faceImage, setFaceImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // 'success' or 'error'
  const [showCamera, setShowCamera] = useState(false);
  const [cameraReady, setCameraReady] = useState(false);
  const [cameraLoading, setCameraLoading] = useState(false);
  const [cameraProgress, setCameraProgress] = useState('');
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  // Camera functions
  const startCamera = async () => {
    // Reset states immediately
    setCameraLoading(true);
    setCameraReady(false);
    setCameraProgress('Starting camera...');
    setMessage('Initializing camera...');
    
    // Try to start camera with multiple fallback strategies
    try {
      await startCameraWithFallback();
    } catch (error) {
      console.error('All camera strategies failed:', error);
      setCameraLoading(false);
      setCameraProgress('');
      setMessage('Camera failed to start. Please use file upload instead.');
      setMessageType('error');
    }
  };
  
  const startCameraWithFallback = async () => {
    const strategies = [
      // Strategy 1: Minimal settings (fastest)
      {
        video: { 
          width: { ideal: 320, max: 640 },
          height: { ideal: 240, max: 480 },
          frameRate: { ideal: 10, max: 15 }
        }
      },
      // Strategy 2: Medium settings
      {
        video: { 
          width: { ideal: 640, max: 1280 },
          height: { ideal: 480, max: 720 },
          frameRate: { ideal: 15, max: 30 }
        }
      },
      // Strategy 3: Basic settings (most compatible)
      {
        video: true
      }
    ];
    
    for (let i = 0; i < strategies.length; i++) {
      try {
        const strategyNames = ['Fast (320x240)', 'Medium (640x480)', 'Basic (any resolution)'];
        setCameraProgress(`Trying ${strategyNames[i]}...`);
        console.log(`Trying camera strategy ${i + 1}...`);
        const stream = await navigator.mediaDevices.getUserMedia(strategies[i]);
        console.log(`Strategy ${i + 1} succeeded!`);
        setCameraProgress('Setting up video...');
        await setupVideoStream(stream);
        return; // Success, exit function
      } catch (error) {
        console.log(`Strategy ${i + 1} failed:`, error);
        if (i === strategies.length - 1) {
          throw error; // All strategies failed
        }
      }
    }
  };
  
  const setupVideoStream = async (stream) => {
    console.log('Setting up video stream...');
    streamRef.current = stream;
    
    if (videoRef.current) {
      console.log('Video ref found, setting up video element...');
      console.log('Stream tracks:', stream.getTracks().map(t => ({ kind: t.kind, enabled: t.enabled, readyState: t.readyState })));
      
      // Ensure stream is active
      if (!stream.active) {
        console.error('Stream is not active!');
        throw new Error('Camera stream is not active');
      }
      
      // Reset video element to ensure clean state
      videoRef.current.srcObject = null;
      videoRef.current.load();
      
      // Wait a moment for reset
      await new Promise(resolve => setTimeout(resolve, 50));
      
      // Set the stream to the video element
      videoRef.current.srcObject = stream;
      
      // Wait a moment for the stream to be set
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Verify the stream was set correctly
      if (!videoRef.current.srcObject) {
        console.error('Failed to set srcObject on video element');
        throw new Error('Failed to set video stream');
      }
      
      console.log('Stream set successfully, verifying...');
      console.log('Video srcObject set:', !!videoRef.current.srcObject);
      
      // Optimize video element for fastest loading
      videoRef.current.preload = 'none';
      videoRef.current.muted = true;
      videoRef.current.playsInline = true;
      videoRef.current.autoplay = true;
      
      console.log('Video element properties set, checking readiness...');
      console.log('Video element after srcObject:', {
        srcObject: !!videoRef.current.srcObject,
        readyState: videoRef.current.readyState,
        videoWidth: videoRef.current.videoWidth,
        videoHeight: videoRef.current.videoHeight
      });
      
      // Try to start video immediately
      try {
        console.log('Attempting immediate video start...');
        
        // Force the video to load the stream
        videoRef.current.load();
        
        // Wait a bit more for the stream to be processed
        await new Promise(resolve => setTimeout(resolve, 200));
        
        // Check if stream is now properly set
        console.log('After load() - Video element state:', {
          srcObject: !!videoRef.current.srcObject,
          readyState: videoRef.current.readyState,
          videoWidth: videoRef.current.videoWidth,
          videoHeight: videoRef.current.videoHeight
        });
        
        if (videoRef.current.srcObject && videoRef.current.readyState >= 2) {
          await videoRef.current.play();
          console.log('Immediate video start succeeded!');
          setCameraReady(true);
          setCameraLoading(false);
          setCameraProgress('');
          setMessage('Camera ready! You can now capture a photo.');
          return;
        } else {
          console.log('Video not ready after load(), using fallback methods');
        }
      } catch (err) {
        console.log('Immediate video start failed, using fallback methods:', err);
      }
      
      // Immediate readiness check
      const checkImmediate = () => {
        const video = videoRef.current;
        if (video && video.readyState >= 2 && video.videoWidth > 0) {
          console.log('Camera ready immediately!');
          setCameraReady(true);
          setCameraLoading(false);
          setCameraProgress('');
          setMessage('Camera ready! You can now capture a photo.');
          return true;
        }
        return false;
      };
      
      // Try immediate check first
      if (checkImmediate()) {
        return;
      }
      
      // Fast event-based detection
      let readyDetected = false;
      
      const markReady = () => {
        if (!readyDetected) {
          readyDetected = true;
          console.log('Camera ready via event!');
          setCameraReady(true);
          setCameraLoading(false);
          setCameraProgress('');
          setMessage('Camera ready! You can now capture a photo.');
        }
      };
      
      // Multiple event listeners for faster detection
      videoRef.current.onloadeddata = () => {
        console.log('Video data loaded');
        if (videoRef.current.readyState >= 2) markReady();
      };
      
      videoRef.current.oncanplay = () => {
        console.log('Video can play');
        markReady();
      };
      
      videoRef.current.onplaying = () => {
        console.log('Video is playing');
        markReady();
      };
      
      // Force video to start playing
      videoRef.current.onloadedmetadata = () => {
        console.log('Video metadata loaded, attempting to play...');
        videoRef.current.play().then(() => {
          console.log('Video play() succeeded');
          markReady();
        }).catch(err => {
          console.log('Video play() failed:', err);
        });
      };
      
      // Aggressive timeout for faster fallback
      setTimeout(() => {
        if (!readyDetected) {
          console.log('Camera ready via aggressive timeout');
          setCameraReady(true);
          setCameraLoading(false);
          setCameraProgress('');
          setMessage('Camera ready! You can now capture a photo.');
        }
      }, 500); // Very aggressive 500ms timeout
    }
    
    console.log('Setting showCamera to true...');
    setShowCamera(true);
    setMessage('');
    
    // Force a re-render and check video element
    setTimeout(() => {
      if (videoRef.current) {
        console.log('Video element after setup:', {
          readyState: videoRef.current.readyState,
          videoWidth: videoRef.current.videoWidth,
          videoHeight: videoRef.current.videoHeight,
          srcObject: !!videoRef.current.srcObject,
          paused: videoRef.current.paused
        });
        
        // If stream is still not set, try to set it again
        if (!videoRef.current.srcObject && streamRef.current) {
          console.log('Stream not set, attempting to set again...');
          videoRef.current.srcObject = streamRef.current;
          videoRef.current.load();
          
          // Wait and check again
          setTimeout(() => {
            if (videoRef.current && videoRef.current.srcObject) {
              console.log('Stream set successfully on retry');
              videoRef.current.play().then(() => {
                console.log('Video start succeeded on retry');
                setCameraReady(true);
                setCameraLoading(false);
                setCameraProgress('');
                setMessage('Camera ready! You can now capture a photo.');
              }).catch(err => {
                console.log('Video start failed on retry:', err);
              });
            }
          }, 300);
        }
        
        // Try to manually start the video if it's not playing
        if (videoRef.current.paused && videoRef.current.readyState >= 2) {
          console.log('Attempting to manually start video...');
          videoRef.current.play().then(() => {
            console.log('Manual video start succeeded');
            // Set camera ready manually
            setCameraReady(true);
            setCameraLoading(false);
            setCameraProgress('');
            setMessage('Camera ready! You can now capture a photo.');
          }).catch(err => {
            console.log('Manual video start failed:', err);
          });
        }
      }
    }, 100);
  };
    

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setShowCamera(false);
    setCameraReady(false);
    setCameraLoading(false);
    setCameraProgress('');
  };

    const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      // Enhanced video readiness check
      const video = videoRef.current;
      console.log('Video state:', {
        readyState: video.readyState,
        videoWidth: video.videoWidth,
        videoHeight: video.videoHeight,
        paused: video.paused,
        ended: video.ended,
        currentTime: video.currentTime
      });
      
      // Check if video is ready (readyState 4 = HAVE_ENOUGH_DATA)
      if (video.readyState < 4 || video.videoWidth === 0 || video.videoHeight === 0) {
        console.log('Video not ready yet. ReadyState:', video.readyState, 'Dimensions:', video.videoWidth, 'x', video.videoHeight);
        setMessage('Camera not ready. Please wait a moment and try again.');
        setMessageType('error');
        return;
      }
      
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      
      // Set canvas size to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      console.log('Canvas size set to:', canvas.width, 'x', canvas.height);
      
      // Draw video frame to canvas
      context.drawImage(video, 0, 0);
      console.log('Video frame drawn to canvas');
      
      // Use toDataURL instead of toBlob for better compatibility
      try {
        console.log('Converting canvas to data URL...');
        const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
        console.log('Data URL created successfully');
        
        // Convert data URL to blob
        const base64Data = dataUrl.split(',')[1];
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: 'image/jpeg' });
        console.log('Blob created from data URL:', blob);
        
        // Create file object
        let file;
        try {
          file = new File([blob], 'face-photo.jpg', { type: 'image/jpeg' });
          console.log('File object created:', file);
        } catch (fileError) {
          console.error('Error creating File object:', fileError);
          // Fallback: create a simple object with blob
          file = {
            name: 'face-photo.jpg',
            type: 'image/jpeg',
            size: blob.size,
            lastModified: Date.now(),
            // Add a method to get the blob
            arrayBuffer: () => blob.arrayBuffer(),
            stream: () => blob.stream(),
            text: () => blob.text()
          };
        }
        
        setFaceImage(file);
        setPreviewUrl(dataUrl); // Use data URL directly for preview
        console.log('Photo captured successfully');
        stopCamera();
        
      } catch (error) {
        console.error('Error capturing photo:', error);
        setMessage('Error capturing photo. Please try again.');
        setMessageType('error');
      }
    } else {
      console.error('Video or canvas ref not available');
      setMessage('Camera not ready. Please try again.');
      setMessageType('error');
    }
  };

  // File upload functions
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      setFaceImage(file);
      setPreviewUrl(URL.createObjectURL(file));
      setMessage('');
    } else {
      setMessage('Please select a valid image file.');
      setMessageType('error');
    }
  };

  // Form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!faceImage) {
      setMessage('Please capture or upload a face image.');
      setMessageType('error');
      return;
    }

    if (mode === 'register' && !username.trim()) {
      setMessage('Please enter a username.');
      setMessageType('error');
      return;
    }

    setIsLoading(true);
    setMessage('');

    try {
      if (mode === 'register') {
        const result = await faceRecognitionService.registerFace(username, faceImage);
        if (result.success) {
          setMessage(result.message);
          setMessageType('success');
          if (onRegister) onRegister(result.username);
        } else {
          setMessage(result.message);
          setMessageType('error');
        }
      } else {
        const result = await faceRecognitionService.loginWithFace(faceImage);
        if (result.success) {
          setMessage(result.message);
          setMessageType('success');
          if (onLogin) onLogin(result.username);
        } else {
          setMessage(result.message);
          setMessageType('error');
        }
      }
    } catch (error) {
      setMessage(error.message);
      setMessageType('error');
    } finally {
      setIsLoading(false);
    }
  };

  // Cleanup
  useEffect(() => {
    return () => {
      stopCamera();
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const resetForm = () => {
    setUsername('');
    setFaceImage(null);
    setPreviewUrl('');
    setMessage('');
    setMessageType('');
    stopCamera();
    setCameraReady(false);
    setCameraLoading(false);
    setCameraProgress('');
  };

  return (
    <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-center mb-6 text-gray-800">
        {mode === 'login' ? 'Face Login' : 'Face Registration'}
      </h2>

      {/* Mode Toggle */}
      <div className="flex mb-6 bg-gray-100 rounded-lg p-1">
        <button
          type="button"
          onClick={() => {
            setMode('login');
            resetForm();
          }}
          className={`flex-1 py-2 px-4 rounded-md transition-colors ${
            mode === 'login'
              ? 'bg-blue-500 text-white'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Login
        </button>
        <button
          type="button"
          onClick={() => {
            setMode('register');
            resetForm();
          }}
          className={`flex-1 py-2 px-4 rounded-md transition-colors ${
            mode === 'register'
              ? 'bg-blue-500 text-white'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Register
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Username field (only for registration) */}
        {mode === 'register' && (
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your username"
              required
            />
          </div>
        )}

        {/* Face Image Capture/Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Face Image
          </label>
          
          {/* Camera Controls */}
          <div className="mb-3 space-y-2">
            <button
              type="button"
              onClick={showCamera ? stopCamera : startCamera}
              disabled={cameraLoading}
              className={`w-full py-2 px-4 rounded-md transition-colors ${
                cameraLoading
                  ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                  : showCamera
                    ? 'bg-red-500 text-white hover:bg-red-600'
                    : 'bg-green-500 text-white hover:bg-green-600'
              }`}
            >
              {cameraLoading ? 'Starting Camera...' : (showCamera ? 'Stop Camera' : 'Start Camera')}
            </button>
            
            {/* Camera Progress Indicator */}
            {cameraLoading && cameraProgress && (
              <div className="text-sm text-blue-600 text-center mt-2">
                {cameraProgress}
              </div>
            )}
            
            {showCamera && (
              <button
                type="button"
                onClick={capturePhoto}
                disabled={!cameraReady}
                className={`w-full py-2 px-4 rounded-md transition-colors ${
                  cameraReady
                    ? 'bg-blue-500 text-white hover:bg-blue-600'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                {cameraReady ? 'Capture Photo' : 'Camera Loading...'}
              </button>
            )}
          </div>

          {/* File Upload */}
          <div className="mb-3">
            <input
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Preview */}
          {previewUrl && (
            <div className="mb-3">
              <img
                src={previewUrl}
                alt="Face preview"
                className="w-full h-48 object-cover rounded-md border border-gray-300"
              />
            </div>
          )}

          {/* Camera View */}
          {showCamera && (
            <div className="mb-3">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-48 object-cover rounded-md border border-gray-300"
              />
              <canvas ref={canvasRef} className="hidden" />
            </div>
          )}
        </div>

        {/* Message Display */}
        {message && (
          <div className={`p-3 rounded-md ${
            messageType === 'success' 
              ? 'bg-green-100 text-green-800 border border-green-200' 
              : 'bg-red-100 text-red-800 border border-red-200'
          }`}>
            {message}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || !faceImage}
          className={`w-full py-3 px-4 rounded-md font-medium transition-colors ${
            isLoading || !faceImage
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-500 text-white hover:bg-blue-600'
          }`}
        >
          {isLoading ? 'Processing...' : (mode === 'login' ? 'Login' : 'Register')}
        </button>
      </form>

      {/* Reset Button */}
      <button
        type="button"
        onClick={resetForm}
        className="w-full mt-4 py-2 px-4 text-gray-600 hover:text-gray-800 transition-colors"
      >
        Reset Form
      </button>
    </div>
  );
};

export default FaceRecognition;
