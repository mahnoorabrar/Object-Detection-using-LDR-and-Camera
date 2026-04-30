# Object Detection using LDR & Camera

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python&style=for-the-badge">
  <img src="https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv&style=for-the-badge">
  <img src="https://img.shields.io/badge/Arduino-Hardware-orange?logo=arduino&style=for-the-badge">

</p>

<p align="left">
  <b>Adaptive Real-Time Object Detection using LDR + OpenCV</b><br>
  <i>Smart vision system that adjusts camera settings based on ambient light</i>
</p>

---

## Overview
This project presents a **hybrid intelligent vision system** that combines:

- 🔌 **Hardware sensing (LDR + Arduino)**
- 💻 **Software processing (Python + OpenCV)**

The system dynamically adjusts camera exposure based on ambient light and performs **real-time green object & LED detection**, ensuring stable performance in varying lighting conditions.

---

## System Setup

### Step 1: Hardware Initialization
- Connect **LDR sensor with Arduino**
- Ensure proper analog input configuration

### Step 2: Run Arduino Code
Upload the following file to Arduino:

👉 https://github.com/mahnoorabrar/Object-Detection-using-LDR-and-Camera/blob/main/ldrled.ino

---

### Step 3: Run Python Code
Execute the Python detection system:

👉 https://github.com/mahnoorabrar/Object-Detection-using-LDR-and-Camera/blob/main/ldrled.py

---

## Project Preview

### 🔆 Light ON Condition
<p align="center">
  <img src="https://raw.githubusercontent.com/mahnoorabrar/Object-Detection-using-LDR-and-Camera/main/lightonimage1.png" width="45%">
  <img src="https://raw.githubusercontent.com/mahnoorabrar/Object-Detection-using-LDR-and-Camera/main/lightonimage2.png" width="45%">
</p>

---

### 🌙 Light OFF Condition
<p align="center">
  <img src="https://raw.githubusercontent.com/mahnoorabrar/Object-Detection-using-LDR-and-Camera/main/lightoffimage1.png" width="45%">
  <img src="https://raw.githubusercontent.com/mahnoorabrar/Object-Detection-using-LDR-and-Camera/main/lightoffimage2.png" width="45%">
</p>

---

## ⚙️ How It Works

### 🔄 System Workflow

```mermaid
flowchart LR
A[🌞 LDR Sensor] -->|Analog Signal| B[🔌 Arduino]
B -->|Serial Data| C[💻 Python Program]
C --> D[📷 Camera Capture]
D --> E[🎛️ Adaptive Exposure Control]
E --> F[🧠 OpenCV Processing]
F --> G[🟩 Object Detection]
G --> H[🖥️ Live Output]
