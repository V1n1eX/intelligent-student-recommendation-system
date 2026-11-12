# Intelligent Student Recommendation System

## Project title
Intelligent Student Recommendation System

## Project overview
This project is an academic recommendation platform designed to help students at DMI St. John the Baptist University discover suitable programmes and learning resources based on academic background, interests, and career goals. The system uses a transparent content-based recommendation approach combining TF-IDF vectorisation, cosine similarity, and weighted structured feature matching.

## Problem statement
Students often struggle to identify programmes and learning resources that match their academic profile, personal interests, and future career objectives. This platform addresses the challenge by generating explainable recommendations from a structured catalogue.

## Objectives
- Help students at DMI St. John the Baptist University explore suitable academic programmes.
- Recommend relevant learning resources for self-study.
- Provide explainable match reasoning.
- Support editable catalogue data without modifying Python logic.
- Demonstrate a complete Django-based academic application with testing and a static GitHub Pages portfolio.

## Features
- Student registration and secure authentication.
- Profile setup and editing.
- DMI St. John the Baptist University programme and resource catalogue.
- Weighted recommendation engine with explainability.
- Recommendation history tracking.
- Dashboard with key metrics.
- Admin management interface.
- Portfolio website for GitHub Pages.

## Technology stack
- Python 3.13
- Django 5.0.7
- SQLite for development
- Pandas, NumPy, scikit-learn
- HTML5, CSS3, Bootstrap 5, vanilla JavaScript
- Chart.js for dashboard visuals

## System architecture
The application follows a layered architecture: user authentication, student profile management, catalogue models, recommendation engine, and views/templates. The recommendation logic remains separated from the Django views and can operate on any editable catalogue data.

## Recommendation methodology
The recommendation engine creates a student profile summary using academic background, subjects, grades, interests, study style, and career goals. It then compares this profile against programme and resource items using:

1. TF-IDF vectorisation over combined text fields.
2. Cosine similarity between profile and catalogue entries.
3. Weighted matching on interest overlap, subject alignment, career alignment, qualification compatibility, and study preference compatibility.

## Mathematical scoring formula
The final score is computed as:

Final Score = (0.25 × Interest Similarity) + (0.25 × Academic Alignment) + (0.20 × Career Alignment) + (0.20 × Qualification Compatibility) + (0.10 × Study Preference Match)

The score is then multiplied by 100 and capped to a 0–100 range. The text similarity from TF-IDF and cosine similarity is used as an additional contextual signal during recommendation generation and explanation.

## Database design
The models include `StudentProfile`, `StudentInterest`, `AcademicProgramme`, `LearningResource`, and `RecommendationHistory` with validation and admin access.

## Installation instructions
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_catalogue
python manage.py runserver
```

## Environment configuration
Development defaults to `DEBUG=True` and generates a temporary secret key at startup. For deployment, set `DJANGO_SECRET_KEY` to a securely generated value, set `DEBUG=False`, and set `ALLOWED_HOSTS` to a comma-separated list of the deployment hostnames. The `.env.example` file documents the expected variables; Django reads these values from the process environment.

## Virtual environment setup
Use the included `.venv` directory and activate it before running Django commands.

## Running migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Catalogue seeding
```bash
python manage.py seed_catalogue
```

## Starting the development server
```bash
python manage.py runserver
```

## Testing instructions
```bash
python manage.py check
python manage.py test
```

## Application screenshots
Screenshots can be added to the `results/` folder and linked from the portfolio once available.

## Limitations
- The catalogue is designed for demonstration and should be reviewed before use in a real admissions context.
- No real labelled student behavioural dataset is present, so the system is designed as a transparent, explainable prototype rather than a production prediction model.
- Recommendation quality depends on well-maintained catalogue metadata.

## Future improvements
- Add real admission criteria validation and predictive modelling.
- Integrate student feedback loops.
- Support external data sources and institutional integrations.
- Add recommendation A/B testing and dashboard analytics.

## Author information
This project was developed as a complete academic software engineering assignment.

## Portfolio URL
The three-page static portfolio is in the `portfolio/` directory. The included GitHub Actions workflow deploys that directory to GitHub Pages on pushes to `main`. Enable GitHub Pages with **GitHub Actions** as the build and deployment source in repository Settings before rerunning the workflow.

## GitHub repository URL
https://github.com/V1n1eX/intelligent-student-recommendation-system
