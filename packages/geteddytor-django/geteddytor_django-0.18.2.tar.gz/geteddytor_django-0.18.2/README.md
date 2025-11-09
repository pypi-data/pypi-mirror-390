
# Django Eddytor

A Django wrapper for the Eddytor rich text editor, bringing **Notion-style editing** to your Django applications with a clean, Pythonic API.

![Django Eddytor](https://img.shields.io/badge/Django-Eddytor-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Django](https://img.shields.io/badge/Django-3.2%2B-green)

---

## ✨ Features

- 🎨 **Notion-style Editor** - Modern, intuitive editing experience
- ⚡ **Slash Commands** - Quick access to formatting and blocks (`/heading`, `/table`, `/image`, etc.)
- 🤖 **AI Rewrite Integration** - Connect your AI API for content enhancement
- 📊 **Rich Content Blocks** - Tables, charts, callouts, code blocks, and more
- 🖼️ **Media Support** - Images and videos with Base64 or API upload
- 📑 **Table of Contents** - Auto-generated document navigation
- 🔗 **Integrations** - Import from Confluence and Azure DevOps
- 🎭 **Theme Support** - Automatic light/dark mode detection
- 📝 **Django Forms Ready** - Seamless integration with Django forms
- 🐍 **Pythonic Configuration** - No JavaScript needed, configure everything in Python

---

## 📦 Installation

### 1. Install the Package

```bash
# Via pip (when published)
pip install django-eddytor

# Or install from source
git clone [Official github source]
cd django-eddytor
pip install -e .
```

### 2. Add to Django Settings

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'django_eddytor',
]
```

### 3. Configure Static Files

```python
# settings.py
STATIC_URL = '/static/'

# For production deployment only
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### 4. Collect Static Files (Production Only)

```bash
# Only needed when deploying to production
python manage.py collectstatic
```

> **Note:** During development with `DEBUG = True`, Django automatically serves static files. You don't need to run `collectstatic`.

---

## 🚀 Quick Start

### Minimal Example

Create a form with Eddytor in just a few lines:

```python
# forms.py
from django import forms
from django_eddytor.widgets import EddytorWidget

class ArticleForm(forms.Form):
    content = forms.CharField(
        widget=EddytorWidget(
            config={
                "placeholder": {
                    "content": "Start writing or type / for commands..."
                }
            }
        )
    )
```

```python
# views.py
from django.shortcuts import render, redirect
from .forms import ArticleForm

def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            # Save your content here
            return redirect('success')
    else:
        form = ArticleForm()
    
    return render(request, 'article_form.html', {'form': form})
```

```html
<!-- article_form.html -->
{% load static %}
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Create Article</title>
</head>
<body>
    <h1>Create New Article</h1>
    <form method="post">
        {% csrf_token %}
        {{ form.content }}
        <button type="submit">Save Article</button>
    </form>
</body>
</html>
```

That's it! You now have a fully functional Notion-style editor. 🎉

---

## 📚 Configuration Guide

All configuration is done through Python dictionaries - no JavaScript required!

### Title & Subtitle

Add a document title with an optional subtitle:

```python
widget = EddytorWidget(
    config={
        "title": {
            "enabled": True,
            "initialValue": "My Document",
            "placeholder": "Enter title here...",
            "editable": True,
            "className": "document-title",
            "subtitle": {
                "enabled": True,
                "text": "Last updated today",
                "className": "text-gray-500",
                "editable": False
            }
        }
    }
)
```

**Options:**

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `enabled` | boolean | `False` | Enable title field |
| `initialValue` | string | `''` | Pre-filled title text |
| `placeholder` | string | `'Untitled Document'` | Placeholder text |
| `editable` | boolean | `True` | Allow editing |
| `className` | string | `''` | CSS class for styling |
| `subtitle.enabled` | boolean | `False` | Show subtitle |
| `subtitle.text` | string | `''` | Subtitle content |

---

### Theme Configuration

Automatic theme switching based on HTML attributes:

```python
config = {
    "themeConfig": {
        "observeElement": "html",           # Element to observe
        "attribute": "class",               # Attribute to watch
        "darkValue": "dark",                # Value indicating dark mode
        "lightValue": "",                   # Value indicating light mode
        "default": "light"                  # Default theme
    }
}
```

**Example with data attributes:**

```python
config = {
    "themeConfig": {
        "observeElement": "html",
        "attribute": "data-theme",
        "darkValue": "dark",
        "lightValue": "light",
        "default": "light"
    }
}
```

---

### Placeholder Text

Customize the empty editor placeholder:

```python
config = {
    "placeholder": {
        "text": "Type / for commands or click + to open menu",
        "className": "editor-placeholder",
        "showForEmptyBlocks": True,
        "showOnFocus": True
    }
}
```

---

### Form Integration

Generate a hidden textarea for form submission:

```python
config = {
    "textarea": {
        "generate": True,       # Auto-generate textarea
        "name": "content"       # Form field name
    }
}
```

The widget automatically syncs the editor content with the textarea on form submission.

---

### AI Rewrite

Enable AI-powered content enhancement:

```python
config = {
    "aiRewrite": {
        "enabled": True,
        "apiEndpoint": "/api/ai/rewrite/",
        "apiMethod": "POST",
        "headers": {
            "Content-Type": "application/json"
        },
        "requestTransform": {
            "tone": "professional",
            "readingLevel": "grade-8",
            "maxTokens": 500
        },
        "responseTransform": True  # Use default response handler
    }
}
```

**Backend Implementation:**

```python
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt  # Use proper authentication in production
def ai_rewrite(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        content = data.get("text") or data.get("content")
        tone = data.get("tone", "professional")
        
        # Process with your AI service (OpenAI, Anthropic, etc.)
        rewritten = your_ai_service.rewrite(
            content, 
            tone=tone,
            reading_level=data.get("readingLevel")
        )
        
        return JsonResponse({"rewritten_text": rewritten})
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
```

**Expected API Response:**

```json
{
  "rewritten_text": "<p>Your rewritten content here...</p>"
}
```

---

### Image Upload

**Base64 Mode (Default - Good for Development):**

```python
config = {
    "image": {
        "upload": {
            "mode": "base64"  # Stores images as inline data
        }
    }
}
```

**API Upload Mode (Recommended for Production):**

```python
config = {
    "image": {
        "upload": {
            "mode": "api",
            "endpoint": "/api/upload/image/",
            "field": "file",
            "method": "POST",
            "headers": {
                "X-CSRFToken": "{{ csrf_token }}"
            },
            "responseKey": "url"  # Key in response containing image URL
        }
    }
}
```

**Backend Implementation:**

```python
# views.py
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@login_required
@require_POST
def upload_image(request):
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({"error": "No file provided"}, status=400)
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        return JsonResponse({"error": "Invalid file type"}, status=400)
    
    # Validate file size (5MB limit)
    if file.size > 5 * 1024 * 1024:
        return JsonResponse({"error": "File too large"}, status=400)
    
    # Save file
    filename = default_storage.save(f'images/{file.name}', file)
    url = default_storage.url(filename)
    
    return JsonResponse({"url": url})
```

**URL Configuration:**

```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/upload/image/', views.upload_image, name='upload_image'),
]
```

---

### Video Upload

**URL Only (Default):**

```python
config = {
    "video": {
        "upload": {
            "mode": "url"  # User enters video URL
        }
    }
}
```

**API Upload:**

```python
config = {
    "video": {
        "upload": {
            "mode": "api",
            "endpoint": "/api/upload/video/",
            "method": "POST",
            "responseKey": "url"
        }
    }
}
```

**Both URL and Upload:**

```python
config = {
    "video": {
        "upload": {
            "mode": "both",  # Allow both URL input and file upload
            "endpoint": "/api/upload/video/",
            "method": "POST",
            "responseKey": "url"
        }
    }
}
```

---

### Table of Contents (TOC)

Enable automatic table of contents generation:

**HTML Structure:**

```html
<!-- your_template.html -->
<div id="editor-wrapper">
    <div class="toc-block" style="height: 100%;">
        <div style="display: none;">
            <a class="toc-item" href="#intro" target="_self">Introduction</a>
            <a class="toc-item" href="#guide" target="_self">User Guide</a>
            <a class="toc-item" href="#api" target="_self">API Reference</a>
        </div>
        <form method="post" style="height: 100%;">
            {% csrf_token %}
            {{ form.content }}
            <button type="submit">Save</button>
        </form>
    </div>
</div>
```

**Widget Configuration:**

```python
widget = EddytorWidget(
    config={
        "editorId": "editor-wrapper",  # Must match parent container ID
        "toc": {
            "enable": True,
            "toc_items": [
                {"url": "#intro", "text": "Introduction"},
                {"url": "#guide", "text": "User Guide"},
                {"url": "#api", "text": "API Reference"}
            ]
        }
    }
)
```

**Requirements:**

- ✅ Parent container must have an `id` attribute
- ✅ Must have a sibling `.toc-block` element
- ✅ TOC items must have valid `href` attributes
- ✅ Use `/toc` slash command to insert TOC in document

---

### Confluence Import

Import content from Confluence pages:

```python
config = {
    "confluence": {
        "enabled": True,
        "dummyMode": False,  # Set to True for testing without backend
        "statusEndpoint": "/api/integrations/confluence/status/",
        "importEndpoint": "/api/confluence/import/",
        "buildImportRequest": {
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "bodyField": "pageUrl"  # Field name for the Confluence URL
        },
        "importResponseTransform": True  # Use default response handler
    },
    "settingsUrl": "/settings/integrations/"  # Redirect for configuration
}
```

**Backend Implementation:**

```python
# views.py
import requests
from django.http import JsonResponse
import json

def confluence_import(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        page_url = data.get('pageUrl')
        
        if not page_url:
            return JsonResponse({"error": "No page URL provided"}, status=400)
        
        # Fetch from Confluence API
        # You'll need Confluence API credentials
        confluence_response = requests.get(
            page_url,
            auth=('username', 'api_token'),
            headers={'Accept': 'application/json'}
        )
        
        confluence_data = confluence_response.json()
        html_content = confluence_data.get('body', {}).get('storage', {}).get('value', '')
        title = confluence_data.get('title', 'Untitled')
        
        return JsonResponse({
            "html": html_content,
            "title": title
        })
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
```

**Expected Response:**

```json
{
  "html": "<p>Confluence page content...</p>",
  "title": "Page Title"
}
```

---

### Azure DevOps Import

Import work items from Azure DevOps queries:

```python
config = {
    "azureDevOps": {
        "enabled": True,
        "dummyMode": False,
        "statusEndpoint": "/api/integrations/azuredevops/status/",
        "importEndpoint": "/api/azuredevops/import/",
        "buildQueryImportRequest": {
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "bodyField": "queryUrl"  # Field name for the query URL
        },
        "queryImportResponseTransform": True
    },
    "settingsUrl": "/settings/integrations/"
}
```

**Backend Implementation:**

```python
# views.py
def azure_import(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        query_url = data.get('queryUrl')
        
        if not query_url:
            return JsonResponse({"error": "No query URL provided"}, status=400)
        
        # Parse Azure DevOps URL
        # Extract organization, project, query ID
        
        # Fetch work items from Azure DevOps API
        azure_response = requests.post(
            f'https://dev.azure.com/{organization}/{project}/_apis/wit/wiql/{query_id}',
            headers={
                'Authorization': f'Basic {base64_encoded_pat}',
                'Content-Type': 'application/json'
            },
            params={'api-version': '6.0'}
        )
        
        work_items = azure_response.json()
        
        # Convert work items to HTML table
        html_content = convert_work_items_to_html(work_items)
        
        return JsonResponse({"html": html_content})
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
```

**Expected Response:**

```json
{
  "html": "<table>...work items...</table>"
}
```

---
