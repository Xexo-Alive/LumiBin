# Lumibin  
Illuminating Urban Waste Management with AI-Powered Geo-Tracking and Gamification.


----



## 🌟 Overview  
Lumibin is a cutting-edge solution for tackling urban waste problems. Using **advanced AI technologies**, **real-time geo-tagging**, and community **gamification mechanics**, Lumibin transforms waste management into an efficient, scalable, and collaborative process.  

This system detects litter automatically, pinpoints its location using GPS, and alerts municipal authorities for immediate action. To foster community engagement, it also incorporates a leaderboard system to reward users for identifying waste hotspots.


----



## 🚀 Features  
- **AI-Powered Waste Detection**: Real-time detection of litter using a YOLOv8 Medium model.  
- **Geo-Tagging for Precision**: GPS integration to mark the exact location of detected waste.  
- **Automated Reporting**: Instant alerts sent to municipal authorities for efficient cleanup.  
- **Gamified Engagement**: A leaderboard and points system encourage public participation in urban waste management.  


----



## 🛠️ Technologies Used  
- **AI/ML Model**: YOLOv8 Medium (PyTorch) optimized to ONNX for fast and efficient inference.  
- **Backend**: Flask framework for API integration between components.  
- **Frontend**: Interactive web-based UI featuring geotagged waste maps and live leaderboard rankings.  
- **Geo-Tracking**: Advanced GPS-based location services for precise waste tagging.  
- **Database**: Handles user data, geo-coordinates, waste status updates, and leaderboard scores.  
- **Gamification Logic**: Innovative algorithms to calculate detection points and rank users effectively.
- **Cloud-Ready**: Engineered for future integration with cloud solutions to scale operations.



----



## 🌍 Problem It Solves  
Cities across the globe are struggling with inefficient waste management due to delayed reporting, limited human resources, and inadequate technological systems.  

**Lumibin** provides a smart, scalable solution by:  
1. Automatically identifying waste through AI-powered image recognition.  
2. Mapping hotspots using GPS technology for quicker municipal response.  
3. Engaging citizens in waste management efforts via gamification.  


----



## ❓ Challenges We Faced  
1. **AI Model Optimization**: Deploying YOLOv8 with ONNX required fine-tuning for speed and accuracy.  
2. **Seamless Frontend-Backend Integration**: Coordinating Flask API data with frontend displays like maps and leaderboards.  
3. **Geo-Tracking Precision**: Addressing variations in GPS accuracy during the testing phase.  
4. **Gamification Design**: Balancing fun and fair point systems for community engagement.  


----



## 🧑‍💻 How to Run Locally  

### Prerequisites  
- Python 3.8 or higher  
- Flask  
- ONNX runtime  
- Node.js (optional, for frontend development)


----



### Installation Steps  
1. Clone the repository:  
   ```bash
   git clone https://github.com/<Xexo_Alive>/Lumibin.git
   cd Lumibin
2.Set up the backend:
  ```bash
  cd backend
  pip install -r requirements.txt
  python app.py
