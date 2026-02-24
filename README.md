# Map Approval System

A web application for automated building plan approval using AI-powered analysis.

## Features

- Upload building plan PDFs
- AI-powered extraction of building parameters
- Automated rule verification against building codes
- Approval/rejection decision making
- User-friendly web interface

## Setup

### Local Development

1. Clone the repository:
```bash
git clone <your-repo-url>
cd map_approval_codebase1
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export GEMINI_API_KEY=your_gemini_api_key_here
export FLASK_DEBUG=true  # For development only
```

4. Run the application:
```bash
python run_app.py
```

The application will be available at `http://localhost:5000`

### Production Deployment

For deployment on platforms like Render:

1. Set the following environment variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `PORT`: Port number (usually set automatically by hosting platform)
   - `FLASK_DEBUG`: Set to "false" for production

2. The application will automatically detect the environment and configure itself accordingly.

## System Requirements

- Python 3.8+
- PDF processing capabilities (poppler-utils on Linux systems)
- Internet connection for AI model access

## API Keys

This application requires a Google Gemini API key for AI-powered analysis. Get one from:
https://ai.google.dev/

## File Structure

- `run_app.py`: Main application entry point
- `web/`: Web application code (Flask routes, templates)
- `src/`: Core extraction and processing logic
- `requirements.txt`: Python dependencies

## How It Works

1. **Upload**: Users upload building plan PDFs through the web interface
2. **Processing**: PDFs are converted to images and processed
3. **Extraction**: AI models extract building parameters (rooms, dimensions, etc.)
4. **Validation**: Extracted data is validated against building codes
5. **Decision**: System generates approval/rejection decision with detailed feedback

## Contributing

1. Follow the existing code structure
2. Update requirements.txt if adding new dependencies
3. Test thoroughly before submitting changes

## License

[Add your license information here]