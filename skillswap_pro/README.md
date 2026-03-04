# SkillSwap Pro

A Django-powered marketplace where users can offer and request skill exchanges.  
It demonstrates basic functionality including user signup/login, posting skills, sending swap requests, notifications, chat, and rating system.

## Features

- User authentication (signup, login, logout)
- Profiles with skill listings
- Browse marketplace and search for skills
- Send/accept/decline swap requests
- Leave ratings after a completed swap
- Notification system for requests and ratings
- **Lesson simulator** where tutors can schedule teaching sessions and learners can join

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.11+ (or whichever version you are using)
- `pip` (installed with Python)

### Installation

1. **Clone the repository** (or copy the files into a new folder):
   ```sh
   git clone https://github.com/Kobbe-bryant/skillswap_pro.git
   cd skillswap_pro
   ```

2. **Create a virtual environment** (optional but recommended):
   ```sh
   python -m venv .venv
   # on Windows
   .\.venv\Scripts\activate
   # on macOS/Linux
   # source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Apply database migrations**:
   ```sh
   python manage.py migrate
   ```

5. **Create a superuser (for admin access)**:
   ```sh
   python manage.py createsuperuser
   ```

6. **Run the development server**:
   ```sh
   python manage.py runserver
   ```
   Navigate to `http://127.0.0.1:8000/` in your browser.

### Configuration

- Settings are located in `skillswap_pro/settings.py`.  
- Static files are in `static/`, templates in `templates/`, media uploads in `media/`.

## Running Tests

No automated tests are included at this time.  You can manually verify functionality through the web interface.

## Simulator / Lesson Feature

Tutors can now create lessons tied to a skill, schedule them and invite learners. Lessons support uploading a material file and specifying a video URL (YouTube/embed link).

Learners browse available lessons, join them (which notifies the tutor), and then access a basic "simulator" page where the materials and video are displayed.  Only the tutor or joined learners may view the simulator.

Lesson creation is restricted so that users may only create lessons for skills they currently offer.

This serves as a foundation for a richer interactive experience including real-time collaboration in future updates.

## Pushing to GitHub

1. **Initialize a git repository (if not already)**:
   ```sh
   cd c:\Users\kobe9\OneDrive\Desktop\SKILLSWAP\skillswap_pro
   git init
   git add .
   git commit -m "Initial commit of SkillSwap Pro"
   ```

2. **Create a new GitHub repository** on GitHub.com (e.g. `skillswap_pro`).

3. **Add the remote and push**:
   ```sh
   git remote add origin https://github.com/<your-username>/skillswap_pro.git
   git branch -M main
   git push -u origin main
   ```

4. For subsequent changes:
   ```sh
   git add .
   git commit -m "Describe your changes"
   git push
   ```

> 🔒 **Note:** Do not commit sensitive data.  Add `db.sqlite3`, `.venv`, and other local files to `.gitignore` if they aren’t already ignored.

## Contributing

Feel free to fork and open pull requests.  Suggest features, report issues, or submit patches.

## License

This project is released under the MIT License.  See `LICENSE` for details (if you include one).

---

Happy coding! 🎯  