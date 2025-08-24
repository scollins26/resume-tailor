# Resume Tailor - AI-Powered Resume Optimization

An intelligent resume tailoring service that uses AI to optimize resumes for specific job descriptions, helping them pass through automated screening systems (ATS) and AI resume review systems.

## Features

- **AI-Powered Analysis**: Uses OpenAI's GPT-4 to analyze job descriptions and extract key requirements
- **Smart Resume Tailoring**: Automatically optimizes resume content to match job requirements
- **Keyword Analysis**: Identifies matching and missing keywords from job descriptions
- **File Support**: Supports PDF, DOCX, and TXT resume formats
- **Confidence Scoring**: Provides a confidence score indicating how well the resume matches the job
- **Detailed Suggestions**: Offers specific, actionable improvement recommendations
- **Modern Web Interface**: Beautiful, responsive UI with drag-and-drop file upload
- **Section-by-Section Analysis**: Detailed breakdown of resume sections and improvements

## Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd resume-tailor
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Run the application**
   ```bash
   uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the application**
   - Web Interface: http://localhost:8000/static/index.html
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Usage

### Web Interface

1. Open http://localhost:8000/static/index.html in your browser
2. Drag and drop your resume file (PDF, DOCX, or TXT) or click to browse
3. Paste the job description in the text area
4. Optionally fill in target role, industry, and experience level
5. Click "Analyze Resume" to start the AI analysis
6. Review the results in the interactive tabs:
   - **Tailored Resume**: View and download the optimized resume
   - **Keyword Analysis**: See which keywords were found and which are missing
   - **Suggestions**: Get specific improvement recommendations

### API Endpoints

#### POST `/resume/analyze`
Analyze resume text with job description.

**Request Body:**
```json
{
  "resume_text": "Your resume content...",
  "job_description": "Job description content...",
  "target_role": "Software Engineer",
  "industry": "Technology",
  "experience_level": "mid"
}
```

#### POST `/resume/analyze-file`
Upload and analyze a resume file.

**Form Data:**
- `resume_file`: Resume file (PDF, DOCX, TXT)
- `job_description`: Job description text
- `target_role`: Target role (optional)
- `industry`: Industry (optional)
- `experience_level`: Experience level (optional)

#### POST `/resume/detailed-analysis`
Get detailed section-by-section analysis.

#### GET `/resume/keywords`
Extract keywords from a job description.

## API Response Format

```json
{
  "original_resume": "Original resume text",
  "tailored_resume": "Optimized resume text",
  "keyword_matches": {
    "python": 3,
    "machine learning": 2
  },
  "missing_keywords": ["docker", "kubernetes"],
  "suggestions": [
    "Add Docker experience to your skills section",
    "Include specific metrics for your achievements"
  ],
  "confidence_score": 0.75,
  "analysis_summary": "Analysis summary..."
}
```

## Architecture

```
resume-tailor/
├── src/
│   └── app/
│       ├── main.py              # FastAPI application entry point
│       ├── models.py            # Pydantic models for API
│       ├── routers/
│       │   └── resume_router.py # API endpoints
│       ├── services/
│       │   ├── ai_service.py    # OpenAI integration
│       │   └── file_service.py  # File processing
│       └── static/
│           ├── index.html       # Web interface
│           └── script.js        # Frontend JavaScript
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## Key Components

### AI Service (`ai_service.py`)
- **Keyword Extraction**: Analyzes job descriptions to identify important skills and requirements
- **Resume Tailoring**: Optimizes resume content to match job requirements
- **Confidence Scoring**: Calculates how well the resume matches the job
- **Suggestion Generation**: Provides specific improvement recommendations

### File Service (`file_service.py`)
- **Multi-format Support**: Handles PDF, DOCX, and TXT files
- **Text Extraction**: Extracts clean text from various file formats
- **File Validation**: Validates file size and format

### Web Interface
- **Modern UI**: Built with Tailwind CSS and Font Awesome
- **Drag-and-Drop**: Intuitive file upload experience
- **Real-time Analysis**: Live feedback and progress indicators
- **Interactive Results**: Tabbed interface for different analysis views

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `LOG_LEVEL`: Logging level (default: INFO)

### API Configuration

The application uses FastAPI with the following features:
- CORS middleware for cross-origin requests
- Automatic API documentation at `/docs`
- Static file serving for the web interface
- Request/response validation with Pydantic

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Code Style
The project follows PEP 8 style guidelines. Use a linter like `flake8` or `black` for code formatting.

### Adding New Features

1. **New API Endpoints**: Add to `src/app/routers/resume_router.py`
2. **New Services**: Create in `src/app/services/`
3. **New Models**: Add to `src/app/models.py`
4. **Frontend Changes**: Modify `src/app/static/` files

## Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY .env .

EXPOSE 8000
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations

1. **Environment Variables**: Use proper environment variable management
2. **API Key Security**: Secure your OpenAI API key
3. **CORS Configuration**: Configure CORS for your production domain
4. **Rate Limiting**: Implement rate limiting for API endpoints
5. **Monitoring**: Add logging and monitoring for production use

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the code comments for implementation details

## Roadmap

- [ ] Support for more file formats (RTF, ODT)
- [ ] Resume template generation
- [ ] Industry-specific optimization
- [ ] Batch processing for multiple resumes
- [ ] Integration with job boards
- [ ] Advanced analytics and reporting
- [ ] Multi-language support

