"use client";
import React, { useRef, useEffect, useState, useCallback } from 'react';
import * as tf from '@tensorflow/tfjs';
import * as cocossd from '@tensorflow-models/coco-ssd';
import { useStore } from '../store/useStore';
import { Camera as CameraIcon, AlertCircle, RefreshCw } from 'lucide-react';
import { LoadingSpinner } from './LoadingSpinner';
import { Notification } from './Notification';
import { saveAs } from 'file-saver';

const GARBAGE_ITEMS = ['bottle', 'cup', 'bowl', 'can', 'box', 'plastic', 'paper'];
const POINTS_PER_ITEM = 10;

const RECYCLING_TIPS = [
  "Did you know? Recycling one aluminum can saves enough energy to run a TV for 3 hours!",
  "Plastic bottles can take up to 450 years to decompose in landfills.",
  "Glass can be recycled endlessly without losing quality or purity!",
  "Paper can be recycled 5 to 7 times before the fibers become too short.",
  "Recycling helps reduce greenhouse gas emissions and saves energy!"
];

const VIRTUAL_ITEMS = [
  { type: 'bottle', points: 10, position: { x: 100, y: 200 } },
  { type: 'can', points: 15, position: { x: 300, y: 150 } },
  { type: 'paper', points: 5, position: { x: 200, y: 300 } },
];

export const CameraComponent: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [model, setModel] = useState<cocossd.ObjectDetection | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCameraError, setCameraError] = useState(false);
  const [position, setPosition] = useState<GeolocationPosition | null>(null);
  const [notification, setNotification] = useState<string | null>(null);
  const [isVideoReady, setIsVideoReady] = useState(false);
  const [bottleDetected, setBottleDetected] = useState(false);
  const { addPoints, addDetectedItem, updateDailyChallenge } = useStore();

  const showNotification = useCallback((message: string) => {
    const randomTip = RECYCLING_TIPS[Math.floor(Math.random() * RECYCLING_TIPS.length)];
    setNotification(`${message}\n\nTip: ${randomTip}`);
  }, []);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsVideoReady(false);
  }, []);

  const setupCamera = useCallback(async () => {
    if (!videoRef.current) return;

    try {
      stopCamera();
      setCameraError(false);

      const constraints = {
        video: {
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;
      videoRef.current.srcObject = stream;
      
      await new Promise<void>((resolve) => {
        if (!videoRef.current) return;
        videoRef.current.onloadedmetadata = () => {
          if (videoRef.current) {
            videoRef.current.play();
            resolve();
          }
        };
      });

      setIsVideoReady(true);
      showNotification("Camera initialized successfully!");
    } catch (err) {
      console.error('Error accessing camera:', err);
      setCameraError(true);
      showNotification("Camera access failed. Please check permissions and try again.");
    }
  }, [stopCamera, showNotification]);

  const retryCamera = useCallback(async () => {
    setIsLoading(true);
    await setupCamera();
    setIsLoading(false);
  }, [setupCamera]);

  const captureFrame = useCallback(() => {
    if (!canvasRef.current || !videoRef.current) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (blob) {
        saveAs(blob, 'captured_frame.png');
      }
    }, 'image/png');
  }, []);

  const detectObjects = useCallback(async () => {
    if (!model || !videoRef.current || !position || !canvasRef.current || !isVideoReady) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
    }

    try {
      const predictions = await model.detect(video);
      
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      const scaleX = canvas.width / 400;
      const scaleY = canvas.height / 400;
      
      VIRTUAL_ITEMS.forEach(item => {
        const x = item.position.x * scaleX;
        const y = item.position.y * scaleY;
        
        ctx.fillStyle = 'rgba(255, 179, 107, 0.5)';
        ctx.beginPath();
        ctx.arc(x, y, 20 * Math.min(scaleX, scaleY), 0, 2 * Math.PI);
        ctx.fill();
        ctx.fillStyle = '#634832';
        ctx.font = `${14 * Math.min(scaleX, scaleY)}px Arial`;
        ctx.fillText(item.type, x - 20 * scaleX, y - 25 * scaleY);
      });

      predictions.forEach((prediction) => {
        if (GARBAGE_ITEMS.includes(prediction.class.toLowerCase())) {
          const [x, y, width, height] = prediction.bbox;
          
          ctx.strokeStyle = '#A67F5C';
          ctx.lineWidth = 2;
          ctx.strokeRect(x, y, width, height);
          
          ctx.fillStyle = '#634832';
          ctx.font = '16px Arial';
          ctx.fillText(
            `${prediction.class} (${Math.round(prediction.score * 100)}%)`,
            x,
            y > 20 ? y - 5 : y + height + 20
          );

          addPoints(POINTS_PER_ITEM);
          addDetectedItem(
            prediction.class,
            position.coords.latitude,
            position.coords.longitude
          );
          showNotification(`Found ${prediction.class}! +${POINTS_PER_ITEM} points`);

          if (prediction.class.toLowerCase() === 'bottle' && !bottleDetected) {
            setBottleDetected(true);
            captureFrame();
          }
        }
      });
    } catch (err) {
      console.error('Error during object detection:', err);
    }
  }, [model, isVideoReady, position, addPoints, addDetectedItem, bottleDetected, captureFrame, showNotification]);

  useEffect(() => {
    const loadModel = async () => {
      try {
        await tf.ready();
        const loadedModel = await cocossd.load();
        setModel(loadedModel);
        setIsLoading(false);
        await setupCamera();
      } catch (err) {
        console.error('Error loading model:', err);
        showNotification("Error loading AI model. Please refresh the page.");
        setIsLoading(false);
      }
    };

    loadModel();

    if (navigator.geolocation) {
      navigator.geolocation.watchPosition(
        (pos) => setPosition(pos),
        (err) => console.error('Error getting location:', err),
        { enableHighAccuracy: true }
      );
    }

    updateDailyChallenge();

    return () => {
      stopCamera();
    };
  }, [setupCamera, stopCamera, showNotification, updateDailyChallenge]);

  useEffect(() => {
    let detectionInterval: NodeJS.Timeout;

    if (!isLoading && isVideoReady) {
      detectionInterval = setInterval(detectObjects, 1000);
    }

    return () => {
      if (detectionInterval) {
        clearInterval(detectionInterval);
      }
    };
  }, [isLoading, isVideoReady, detectObjects]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 bg-cream">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="relative bg-cream rounded-lg overflow-hidden">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="w-full rounded-lg shadow-lg"
      />
      <canvas
        ref={canvasRef}
        className="absolute top-0 left-0 w-full h-full"
      />
      
      <div className="absolute top-4 right-4 flex gap-2">
        <button
          className="bg-cream p-2 rounded-full shadow-lg cursor-pointer hover:bg-sand transition-colors"
          onClick={retryCamera}
          title="Retry Camera"
        >
          <RefreshCw className="w-6 h-6 text-sepia" />
        </button>
        <button
          className="bg-cream p-2 rounded-full shadow-lg cursor-pointer hover:bg-sand transition-colors"
          onClick={captureFrame}
          title="Capture Frame"
        >
          <CameraIcon className="w-6 h-6 text-sepia" />
        </button>
      </div>
      
      {!position && (
        <div className="absolute top-4 left-4 bg-sand bg-opacity-90 p-2 rounded-lg shadow flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-brown" />
          <span className="text-sm text-brown">Waiting for location...</span>
        </div>
      )}

      {isCameraError && (
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-sand bg-opacity-90 p-4 rounded-lg shadow-lg text-center">
          <AlertCircle className="w-8 h-8 text-brown mx-auto mb-2" />
          <p className="text-brown mb-2">Camera access failed</p>
          <button
            onClick={retryCamera}
            className="bg-sepia text-cream px-4 py-2 rounded-lg hover:bg-brown transition-colors flex items-center gap-2 mx-auto"
          >
            <RefreshCw className="w-4 h-4" />
            Retry Camera
          </button>
        </div>
      )}

      {notification && (
        <Notification
          message={notification}
          type="success"
          onClose={() => setNotification(null)}
        />
      )}
    </div>
  );
};