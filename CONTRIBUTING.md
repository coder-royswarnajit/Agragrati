# Contributing to Agragrati

Thank you for your interest in contributing to Agragrati! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/agragrati/issues)
2. If not, create a new issue with:
  - Clear, descriptive title
  - Steps to reproduce
  - Expected vs actual behavior
  - Screenshots if applicable
  - Environment details (OS, browser, Node/Python version)

### Suggesting Features

1. Check existing issues for similar suggestions
2. Create a new issue with:
  - Clear description of the feature
  - Use case and benefits
  - Possible implementation approach

### Pull Requests

1. **Fork the repository**

2. **Create a feature branch**
  ```bash
  git checkout -b feature/your-feature-name
  ```

3. **Make your changes**
  - Follow the code style guidelines
  - Add/update tests if applicable
  - Update documentation if needed

4. **Commit with descriptive messages**
  ```bash
  git commit -m "feat: add your feature description"
  ```

5. **Push to your fork**
  ```bash
  git push origin feature/your-feature-name
  ```

6. **Open a Pull Request**
  - Provide a clear description
  - Reference any related issues
  - Include screenshots for UI changes

## Development Setup

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed setup instructions.

### Quick Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/agragrati.git
cd agragrati

# Backend
cd backend
python -m venv venv
source venv/bin/activate # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

## Code Style

### TypeScript/React

- Use functional components with hooks
- Use TypeScript for type safety
- Follow ESLint configuration
- Use Tailwind CSS for styling
- Add Framer Motion animations for new components

**Example component:**
```tsx
import { motion } from "framer-motion";
import { fadeInUp } from "@/lib/animations";

interface MyComponentProps {
 title: string;
 onClick: () => void;
}

const MyComponent = ({ title, onClick }: MyComponentProps) => {
 return (
  <motion.div
   variants={fadeInUp}
   initial="initial"
   animate="animate"
   className="p-4 rounded-lg bg-card"
  >
   <h2 className="text-lg font-semibold">{title}</h2>
   <button onClick={onClick}>Click me</button>
  </motion.div>
 );
};

export default MyComponent;
```

### Python

- Follow PEP 8 style guide
- Use type hints
- Document functions with docstrings
- Use Pydantic models for request/response validation

**Example endpoint:**
```python
class MyRequest(BaseModel):
  data: str
  optional_field: Optional[str] = None

class MyResponse(BaseModel):
  result: str
  success: bool

@app.post("/my-endpoint", response_model=MyResponse)
async def my_endpoint(request: MyRequest) -> MyResponse:
  """
  Process the request and return result.
  
  Args:
    request: The request data
    
  Returns:
    MyResponse with processed result
  """
  result = process(request.data)
  return MyResponse(result=result, success=True)
```

## Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style (formatting, no logic change) |
| `refactor` | Code refactoring |
| `perf` | Performance improvement |
| `test` | Adding/updating tests |
| `chore` | Maintenance tasks |

**Examples:**
```
feat: add resume export to PDF
fix: resolve job search pagination issue
docs: update API documentation
style: format code with prettier
refactor: extract job search logic to hook
perf: optimize resume parsing
test: add tests for cover letter generation
chore: update dependencies
```

## Project Structure

```
Agragrati/
├── frontend/     # React frontend
│  ├── src/
│  │  ├── pages/  # Route pages
│  │  ├── components/
│  │  ├── hooks/
│  │  ├── lib/
│  │  └── store/
│  └── public/
├── backend/      # FastAPI backend
│  └── main.py
├── job_search.py   # Core AI logic
└── docs/       # Documentation
```

## Areas for Contribution

### Good First Issues

- Documentation improvements
- UI/UX enhancements
- Bug fixes
- Test coverage

### Feature Ideas

- Resume templates
- Interview recording
- Job application reminders
- Email notifications
- Multi-language support
- Resume version history
- AI chat assistant

### Technical Improvements

- Unit tests
- E2E tests
- Performance optimization
- Accessibility improvements
- Mobile app (React Native)

## Questions?

- Open a [Discussion](https://github.com/yourusername/agragrati/discussions)
- Check existing [Issues](https://github.com/yourusername/agragrati/issues)
- Review [Documentation](README.md)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Agragrati! 
