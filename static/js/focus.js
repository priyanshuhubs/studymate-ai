/**
 * focus.js
 * --------
 * Browser port of Smart-Study-Focus (EAR + head-facing attention check)
 * using MediaPipe FaceLandmarker so it works both locally and live on Render.
 */
import { FaceLandmarker, FilesetResolver } from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14";

const video = document.getElementById("focusVideo");
const placeholder = document.getElementById("cameraPlaceholder");
const statusBadge = document.getElementById("focusStatusBadge");
const modeSelect = document.getElementById("focusModeSelect");
const goalInput = document.getElementById("focusGoalMinutes");
const focusedDisplay = document.getElementById("focusedTimeDisplay");
const totalDisplay = document.getElementById("totalTimeDisplay");
const startBtn = document.getElementById("startFocusBtn");
const stopBtn = document.getElementById("stopFocusBtn");
const saveMsg = document.getElementById("focusSaveMsg");

let faceLandmarker = null;
let stream = null;
let running = false;
let focusedSeconds = 0;
let totalSeconds = 0;
let currentStatus = "Focused";
let eyesClosedSince = null;
let timerInterval = null;

function formatTime(sec) {
  const m = String(Math.floor(sec / 60)).padStart(2, "0");
  const s = String(sec % 60).padStart(2, "0");
  return `${m}:${s}`;
}

function setBadge(text, colorClass) {
  statusBadge.textContent = text;
  statusBadge.className = `badge ${colorClass}`;
}

async function initFaceModel() {
  if (faceLandmarker) return;
  setBadge("Loading AI Model...", "badge-priority-medium");
  const vision = await FilesetResolver.forVisionTasks(
    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm"
  );
  faceLandmarker = await FaceLandmarker.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath:
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
    },
    runningMode: "VIDEO",
    numFaces: 1,
  });
}

function dist(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

function detectLoop() {
  if (!running || modeSelect.value !== "Camera Focus") return;

  if (video.readyState >= 2 && faceLandmarker) {
    const result = faceLandmarker.detectForVideo(video, performance.now());
    if (result.faceLandmarks && result.faceLandmarks.length > 0) {
      const lm = result.faceLandmarks[0];
      // Same landmark indices as s6focus_cam.py: 159, 145 (vertical), 33, 133 (horizontal), 263 (right eye)
      const ear = dist(lm[159], lm[145]) / (dist(lm[33], lm[133]) || 1);
      const horizontalDiff = Math.abs(lm[33].x - lm[263].x);

      if (ear <= 0.22) {
        if (!eyesClosedSince) eyesClosedSince = Date.now();
        const closedSec = (Date.now() - eyesClosedSince) / 1000;
        if (closedSec > 1.0) {
          currentStatus = "Eyes Closed";
          setBadge(`Eyes Closed (${closedSec.toFixed(1)}s)`, "badge-priority-high");
        }
      } else {
        eyesClosedSince = null;
        if (horizontalDiff > 0.13) {
          currentStatus = "Focused";
          setBadge("Focused", "badge-priority-low");
        } else {
          currentStatus = "Not Focused";
          setBadge("Not Focused", "badge-priority-medium");
        }
      }
    } else {
      currentStatus = "No Face Detected";
      setBadge("No Face Detected", "badge-priority-high");
    }
  }
  requestAnimationFrame(detectLoop);
}

startBtn.addEventListener("click", async () => {
  focusedSeconds = 0;
  totalSeconds = 0;
  focusedDisplay.textContent = "00:00";
  totalDisplay.textContent = "00:00";
  saveMsg.textContent = "";

  if (modeSelect.value === "Camera Focus") {
    try {
      await initFaceModel();
      stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video.srcObject = stream;
      placeholder.style.display = "none";
      running = true;
      requestAnimationFrame(detectLoop);
    } catch (err) {
      modeSelect.value = "Timer Only";
      currentStatus = "Focused";
      setBadge("Timer Only (No Camera)", "badge-priority-medium");
      running = true;
    }
  } else {
    currentStatus = "Focused";
    setBadge("Timer Active", "badge-priority-low");
    running = true;
  }

  startBtn.disabled = true;
  stopBtn.disabled = false;

  timerInterval = setInterval(() => {
    totalSeconds += 1;
    if (modeSelect.value === "Timer Only" || currentStatus === "Focused") {
      focusedSeconds += 1;
    }
    focusedDisplay.textContent = formatTime(focusedSeconds);
    totalDisplay.textContent = formatTime(totalSeconds);
  }, 1000);
});

stopBtn.addEventListener("click", async () => {
  running = false;
  clearInterval(timerInterval);
  if (stream) {
    stream.getTracks().forEach((t) => t.stop());
    video.srcObject = null;
  }
  placeholder.style.display = "block";
  setBadge("Session Saved", "badge-type");
  startBtn.disabled = false;
  stopBtn.disabled = true;

  await fetch("/api/focus/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      mode: modeSelect.value,
      goal_minutes: Number(goalInput.value || 25),
      focused_seconds: focusedSeconds,
      total_seconds: totalSeconds,
    }),
  });
  saveMsg.textContent = "Focus session saved! Refresh to see it in your history below.";
});