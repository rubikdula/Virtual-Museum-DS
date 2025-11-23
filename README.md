# Virtual Museum DS

**Virtual Museum DS** is an immersive, social web platform that combines the engagement of social media with the wonder of a 3D virtual museum. Users can curate their own digital exhibitions, explore procedurally generated galleries, interact with an AI-powered tour guide, and connect with other visitors in real-time.

## 🚀 Features

### 🏛️ 3D Virtual Experience
*   **Immersive Exploration**: Walk through 3D galleries using First-Person or Third-Person views.
*   **Multi-Era Environments**: Switch between Ancient, Medieval, Industrial, Modern, and Future themes with dynamic lighting and ambient audio.
*   **Multiplayer Interaction**: See other users' avatars moving in real-time within the museum (powered by WebSockets).
*   **AI Tour Guide**: A context-aware AI guide (powered by OpenAI) that can give tours, answer questions via chat, and speak using Text-to-Speech (TTS).
*   **Personal Museums**: Users can arrange their collected artifacts in their own customizable 3D space.

### 📱 Social Platform
*   **Social Feed**: Browse artifacts in a vertical, Instagram-style feed.
*   **Interactions**: Like and comment on artifacts.
*   **Notifications**: Real-time alerts for likes, comments, and collection requests.
*   **Leaderboards**: Track top collectors and most popular curators.
*   **User Profiles**: Customizable profiles with avatars and bios.

### 🎨 Curatorship & AI
*   **Upload Artifacts**: Users can upload images, 3D models, or video links.
*   **AI Generation**: Generate unique artifacts (image + metadata) using AI prompts.
*   **Collection System**: Request to add other users' artworks to your personal collection with an approval workflow.
*   **AI Knowledge Expander**: Get detailed historical facts, related inventions, and similar artifact recommendations for any item.

## 🛠️ Tech Stack

*   **Backend**: Python, FastAPI, SQLAlchemy
*   **Database**: SQLite
*   **Frontend**: HTML5, CSS3, JavaScript, Jinja2 Templates
*   **3D Engine**: A-Frame (WebVR)
*   **AI Integration**: OpenAI API (GPT-3.5 Turbo), Pollinations.ai (Image Generation)
*   **Real-time**: WebSockets

## 📦 Installation

Follow these steps to set up the project on your local machine.

### Prerequisites
*   Python 3.8 or higher
*   `pip` (Python package manager)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Virtual-Museum-DS
```

### 2. Create a Virtual Environment (Optional but Recommended)
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory and add your OpenAI API key:
```env
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_for_jwt
```
*(Note: AI features will not work without a valid OpenAI API key)*

### 5. Initialize the Database
The application will automatically create the necessary database tables on the first run. However, if you want to seed the database with some initial artifacts, you can run:
```bash
python seed_artifacts.py
```

## 🏃‍♂️ Running the Application

Start the development server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

Or using Python directly:
```bash
python -m uvicorn app.main:app --reload
```

The application will be available at: **http://127.0.0.1:8000**

## 📖 Usage Guide

1.  **Sign Up/Login**: Create an account to start curating and interacting.
2.  **Home Feed**: View the latest artifacts. Like, comment, or click to view details.
3.  **3D Museum**: Click "Enter 3D Museum" to explore.
    *   **WASD**: Move around.
    *   **Mouse**: Look around.
    *   **Click**: Interact with artifacts.
    *   **Chat Bar**: Ask the AI Guide questions at the bottom of the screen.
4.  **Create**: Use the "Upload" or "Create with AI" buttons to add to the museum.
5.  **My Museum**: Go to your profile to view your personal collection and customize your museum layout.

## 🤝 Contributing

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
