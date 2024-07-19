# Notes API

## Project Overview

This is a RESTful API for managing notes. It allows users to create, read, update, delete, share, and search for notes. The API is built using Django and Django REST Framework, and it supports user authentication and authorization.

## Choice of Framework/DB/Tools

### Framework

- **Django**: A high-level Python web framework that encourages rapid development and clean, pragmatic design.
- **Django REST Framework**: A powerful and flexible toolkit for building Web APIs in Django.

### Database

- **PostgreSQL**: Chosen for its robustness and advanced features, including full-text search capabilities.

### Authentication

- **Access-based Authentication**: Implemented using Django REST Framework's built-in access authentication system for secure user authentication.

### Search

- **PostgreSQL Full-Text Search**: Used to efficiently search for notes based on keywords.

### Testing

- **Django Test Framework**: Utilized to ensure the reliability and correctness of the API endpoints.

### Deployment

- **Render**: A cloud platform for deploying and hosting applications.

<strong>OVERALL I AM MOST COMFORTABLE USNG DFR</strong>

## Instructions

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/chinemeremeze/notes.git
   cd notes
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**

   ```bash
   source venv/bin/activate
   ```

4. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Apply Migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create a Superuser (for admin access)**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

### Running Tests

1. **Ensure the Development Server is Stopped**

2. **Run Tests**
   ```bash
   python manage.py test
   ```

## API Documentation

- **Postman Collection**: A Postman collection for testing the API is available at: [Postman Collection](https://example.com)

## License

This project is licensed under the MIT License - see the LICENSE file for details
