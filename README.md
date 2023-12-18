# FastAPI File Management Project

This is a FastAPI project for file management with user accounts. It includes features like user authentication, file upload/download, directory creation/deletion, and user activity tracking.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/fastapi-file-management.git
   cd fastapi-file-management
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up MongoDB:
   - Create a MongoDB Atlas account and configure the connection string in `main.py`.
   - Update the `SECRET_KEY` and other configurations in `main.py` as needed.

## Usage

1. Run the FastAPI server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. Access the FastAPI Swagger documentation at [http://localhost:8000/docs](http://localhost:8000/docs) for API endpoints and testing.

## API Endpoints

- **Login:** `/token` - Obtain an access token for authentication.
- **Signup:** `/signup` - Create a new user account.
- **Get Directories:** `/directories` - Get a list of directories for the authenticated user.
- **Create Directory:** `/create_directory` - Create a new directory for the authenticated user.
- **Upload File:** `/upload` - Upload a file to the specified path for the authenticated user.
- **Download File:** `/download` - Download a file from the specified path for the authenticated user.
- **Delete File:** `/delete` - Delete a file from the specified path for the authenticated user.
- **Delete Directory:** `/delete_directory` - Delete a directory and its contents for the authenticated user.

## Dependencies

- FastAPI: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- Pydantic: [https://pydantic-docs.helpmanual.io/](https://pydantic-docs.helpmanual.io/)
- Passlib: [https://passlib.readthedocs.io/](https://passlib.readthedocs.io/)
- pymongo: [https://pymongo.readthedocs.io/](https://pymongo.readthedocs.io/)
- uvicorn: [https://www.uvicorn.org/](https://www.uvicorn.org/)

## Author

[Swoyam Siddharth Nayak](https://www.linkedin.com/in/swoyam2609/)