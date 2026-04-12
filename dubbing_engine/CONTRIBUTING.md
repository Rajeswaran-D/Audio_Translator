# Contributing to Audio Translator & Dubbing Engine

Thank you for your interest in contributing to this project! This guide explains how to make effective contributions through pull requests.

---

## 🚀 Getting Started

### 1. Fork the Repository
Click the "Fork" button on GitHub to create your own copy of the project.

### 2. Clone Your Fork
```bash
git clone https://github.com/your-username/Audio_Translator.git
cd Audio_Translator/dubbing_engine
```

### 3. Add Upstream Remote
```bash
git remote add upstream https://github.com/original-owner/Audio_Translator.git
git fetch upstream
```

### 4. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-fix-name
```

**Branch Naming Convention:**
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code restructuring
- `perf/description` - Performance improvements
- `test/description` - Test additions

---

## 💻 Development Workflow

### 1. Set Up Development Environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Make Your Changes
- Keep commits small and focused
- Follow code style conventions (see below)
- Update relevant documentation
- Add tests for new features

### 3. Test Your Changes
```bash
# Run locally
python main.py

# Test specific endpoints
curl -X POST http://localhost:8000/translate \
  -F "file=@test_audio.wav" \
  -F "target_lang=ta"
```

### 4. Commit Your Changes
```bash
git add .
git commit -m "feat: add lyrics editing feature"
```

**Commit Message Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Code style (formatting, semicolons, etc.)
- `refactor:` - Code refactoring without feature/fix
- `perf:` - Performance improvement
- `test:` - Test additions/updates
- `chore:` - Dependency updates, build config

**Examples:**
```bash
git commit -m "feat(lyrics): add segment-level editing capability

- Implemented /edit-segment/{job_id} endpoint
- Added text input validation
- Ensure translated text updates segment metadata"

git commit -m "fix(vocal-separator): handle missing WAV files

- Update file lookup logic for WAV/MP3 fallback
- Add better error messaging for missing files"

git commit -m "docs: update README with deployment instructions"
```

### 5. Keep Your Branch Updated
```bash
git fetch upstream
git rebase upstream/main
```

### 6. Push to Your Fork
```bash
git push origin feature/your-feature-name
```

---

## 📋 Creating a Pull Request

### PR Title
Follow commit message format:
```
feat(module): short description
fix(module): short description
docs: short description
```

**Examples:**
- `feat(tts): add voice profile caching`
- `fix(stt): handle concurrent requests`
- `docs: add API documentation`

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Breaking change

## Related Issues
Closes #123

## Testing
Describe testing performed:
- [ ] Manual testing on local environment
- [ ] Tested with audio file: [description]
- [ ] Tested endpoints: [list]

## Checklist
- [ ] Code follows project style guidelines
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] No security issues introduced
```

### PR Content Requirements

**Code Changes:**
- [ ] Clear, purposeful commits
- [ ] No debugging code or console.log
- [ ] No API keys or credentials in code
- [ ] Follows existing code style
- [ ] Comments for complex sections
- [ ] Error handling included

**Documentation:**
- [ ] README updated (if applicable)
- [ ] API docs updated (if applicable)
- [ ] Code comments for complex logic
- [ ] Examples provided for new features

**Testing:**
- [ ] Feature manually tested locally
- [ ] Edge cases considered
- [ ] Error scenarios handled
- [ ] No performance degradation

---

## 📐 Code Style Guidelines

### Python (Backend)

```python
# Use type hints
def process_audio(file_path: str, lang: str) -> Dict[str, Any]:
    """Process audio file and return results.
    
    Args:
        file_path: Path to audio file
        lang: Target language code
        
    Returns:
        Dictionary with processing results
    """
    pass

# Use meaningful variable names
processed_segments = []  # Good
segs = []  # Avoid

# Use f-strings
message = f"Processing {filename} to {target_lang}"  # Good
message = "Processing " + filename + " to " + target_lang  # Avoid

# Add error handling
try:
    audio = load_audio(path)
except FileNotFoundError as e:
    print(f"Error: Audio file not found: {e}")
    raise

# Add docstrings
def translate_text(text: str, source: str, target: str) -> str:
    """Translate text using Google Translate API.
    
    Args:
        text: Text to translate
        source: Source language code
        target: Target language code
        
    Returns:
        Translated text string
        
    Raises:
        ValueError: If language codes are invalid
        ConnectionError: If API request fails
    """
    pass
```

### JavaScript (Frontend)

```javascript
// Use meaningful function names
function loadLyricsEditor(jobId, segments) {
    // Implementation
}

// Use const by default
const processingStatus = "complete";

// Use arrow functions
segments.forEach(seg => {
    displaySegment(seg);
});

// Add comments for complex logic
// Calculate time offset accounting for silence
const offset = segment.start - previousEnd;

// Use proper error handling
try {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
} catch (error) {
    console.error("Request failed:", error);
}
```

### HTML/CSS

```html
<!-- Use semantic HTML -->
<section class="lyrics-editor-section">
    <h3>Edit Lyrics</h3>
    <textarea id="translated-0"></textarea>
</section>

<!-- Use meaningful class names -->
<button class="save-btn">Save</button>  <!-- Good -->
<button class="btn1">Save</button>      <!-- Avoid -->
```

```css
/* Use consistent naming (kebab-case) */
.lyrics-editor-section { }
.save-btn { }

/* Group related rules */
.tab-btn {
    padding: 0.75rem;
    border: none;
}

.tab-btn:hover {
    background: #ccc;
}

.tab-btn.active {
    border-bottom: 3px solid blue;
}
```

---

## 🧪 Testing Requirements

### For Feature Additions
1. **Manual Testing**
   - Test on local environment
   - Try normal cases and edge cases
   - Verify error handling

2. **Audio Testing**
   - Test with different audio formats (MP3, WAV, FLAC)
   - Test different durations (short clips, long files)
   - Test different languages

3. **API Testing**
   - Test valid requests and responses
   - Test error conditions
   - Check response codes and messages

**Example Test:**
```bash
# Test new feature
curl -X POST http://localhost:8000/edit-segment/job123 \
  -H "Content-Type: application/json" \
  -d '{
    "segment_id": 0,
    "new_translated_text": "வணக்கம்"
  }'

# Verify response
# Expected: {"status": "success", "message": "Segment updated"}
```

### For Bug Fixes
1. Describe the bug with reproduction steps
2. Verify fix resolves the issue
3. Test edge cases that may have similar issues

---

## 🔍 Code Review Checklist

Reviewers will check:

- [ ] Clear commit messages and PR description
- [ ] Code follows style guidelines
- [ ] No unnecessary dependencies added
- [ ] Error handling is appropriate
- [ ] Documentation is updated
- [ ] No breaking changes (or justified)
- [ ] No security vulnerabilities
- [ ] Performance impact is acceptable
- [ ] Code is testable and maintainable

---

## 📝 Documentation Updates

When making changes that affect users:

### Update README.md if:
- [ ] New feature added
- [ ] Installation process changes
- [ ] Configuration changes
- [ ] API changes

### Add comments if:
- [ ] Complex algorithm implemented
- [ ] Non-obvious behavior needed
- [ ] Potential performance impact

### Update API docs if:
- [ ] New endpoint added
- [ ] Endpoint behavior changes
- [ ] Request/response format changes

**Example Documentation:**
```markdown
### New Feature: Segment Caching

**Description:** Cache frequently used segments to improve performance

**Configuration:**
```python
CACHE_SEGMENTS = True
CACHE_TIMEOUT = 3600  # seconds
```

**Usage:**
Similar segments are automatically cached after generation.

**Performance Impact:** 
- 30% reduction in TTS computation for repeated segments
- ~50MB additional memory per 1000 cached segments
```

---

## 🚫 What NOT to Do

1. **Don't commit:**
   - API keys, passwords, credentials
   - Large model files (>100MB)
   - Generated audio files
   - Node modules or venv
   - IDE-specific settings

2. **Don't make:**
   - Unrelated changes in one PR
   - Formatting-only changes (mix with feature changes)
   - Major refactorings without discussion
   - Breaking changes without justification

3. **Don't ignore:**
   - PR review comments
   - CI/CD check failures
   - Type hints or docstrings
   - Error handling

---

## 🔄 After PR Submission

### Address Review Comments
1. Make requested changes
2. Commit with meaningful messages
3. Push updates to your branch
4. GitHub will auto-update PR

### Merge Conflicts
```bash
# Update from upstream
git fetch upstream
git rebase upstream/main

# Resolve conflicts (edit conflicted files)
git add .
git rebase --continue

# Force push to your fork
git push origin feature/name --force-with-lease
```

### After Merge
- Delete your feature branch
- Update local main branch
- Continue with next feature

---

## 📞 Questions or Need Help?

- **Discussion**: Open a GitHub Discussion
- **Issue**: Create an issue for bugs/features
- **Email**: Contact project maintainer

---

## 🎓 Learning Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Python PEP 8](https://www.python.org/dev/peps/pep-0008/)

---

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

**Happy Contributing! 🚀**
