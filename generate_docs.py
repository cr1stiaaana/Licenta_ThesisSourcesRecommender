#!/usr/bin/env python3
"""
Generate API documentation from OpenAPI spec.

This script:
1. Validates the OpenAPI specification
2. Generates HTML documentation using Redoc
3. Generates Markdown documentation
4. Creates a static documentation site
"""

import json
import yaml
import subprocess
import sys
from pathlib import Path


def validate_openapi_spec(spec_path: str) -> bool:
    """Validate OpenAPI specification."""
    print(f"📋 Validating OpenAPI spec: {spec_path}")
    
    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec = yaml.safe_load(f)
        
        # Basic validation
        required_fields = ['openapi', 'info', 'paths']
        for field in required_fields:
            if field not in spec:
                print(f"❌ Missing required field: {field}")
                return False
        
        print(f"✅ OpenAPI spec is valid")
        print(f"   Version: {spec['openapi']}")
        print(f"   Title: {spec['info']['title']}")
        print(f"   API Version: {spec['info']['version']}")
        print(f"   Endpoints: {len(spec['paths'])}")
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False


def generate_redoc_html(spec_path: str, output_path: str) -> bool:
    """Generate standalone Redoc HTML documentation."""
    print(f"\n📄 Generating Redoc HTML documentation...")
    
    try:
        # Read OpenAPI spec
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec = yaml.safe_load(f)
        
        # Convert to JSON for embedding
        spec_json = json.dumps(spec, indent=2)
        
        # Generate HTML with embedded spec
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{spec['info']['title']} - API Documentation</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
    <redoc spec-url='#'></redoc>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
    <script>
        const spec = {spec_json};
        Redoc.init(spec, {{}}, document.querySelector('redoc'));
    </script>
</body>
</html>"""
        
        # Write HTML file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html_content, encoding='utf-8')
        
        print(f"✅ Redoc HTML generated: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Redoc generation failed: {e}")
        return False


def generate_swagger_ui_html(spec_path: str, output_path: str) -> bool:
    """Generate standalone Swagger UI HTML documentation."""
    print(f"\n📄 Generating Swagger UI HTML documentation...")
    
    try:
        # Read OpenAPI spec
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec = yaml.safe_load(f)
        
        # Convert to JSON for embedding
        spec_json = json.dumps(spec, indent=2)
        
        # Generate HTML with embedded spec
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{spec['info']['title']} - Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
    <style>
        html {{
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }}
        *, *:before, *:after {{
            box-sizing: inherit;
        }}
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const spec = {spec_json};
            
            window.ui = SwaggerUIBundle({{
                spec: spec,
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            }});
        }};
    </script>
</body>
</html>"""
        
        # Write HTML file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html_content, encoding='utf-8')
        
        print(f"✅ Swagger UI HTML generated: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Swagger UI generation failed: {e}")
        return False


def generate_markdown_docs(spec_path: str, output_path: str) -> bool:
    """Generate Markdown documentation from OpenAPI spec."""
    print(f"\n📄 Generating Markdown documentation...")
    
    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec = yaml.safe_load(f)
        
        info = spec['info']
        paths = spec['paths']
        
        # Generate Markdown
        md_content = f"""# {info['title']}

**Version:** {info['version']}

{info.get('description', '')}

## Base URL

```
{spec['servers'][0]['url']}
```

## Endpoints

"""
        
        # Add each endpoint
        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    md_content += f"\n### {method.upper()} {path}\n\n"
                    md_content += f"**Summary:** {details.get('summary', 'N/A')}\n\n"
                    
                    if 'description' in details:
                        md_content += f"{details['description']}\n\n"
                    
                    if 'tags' in details:
                        md_content += f"**Tags:** {', '.join(details['tags'])}\n\n"
                    
                    # Request body
                    if 'requestBody' in details:
                        md_content += "**Request Body:**\n\n"
                        md_content += "```json\n"
                        md_content += "{\n  // See OpenAPI spec for schema\n}\n"
                        md_content += "```\n\n"
                    
                    # Responses
                    if 'responses' in details:
                        md_content += "**Responses:**\n\n"
                        for code, response in details['responses'].items():
                            md_content += f"- `{code}`: {response.get('description', 'N/A')}\n"
                        md_content += "\n"
        
        # Write Markdown file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(md_content, encoding='utf-8')
        
        print(f"✅ Markdown documentation generated: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Markdown generation failed: {e}")
        return False


def create_docs_index(docs_dir: str) -> bool:
    """Create an index.html that links to all documentation formats."""
    print(f"\n📄 Creating documentation index...")
    
    try:
        index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #c7410e;
            padding-bottom: 10px;
        }
        .doc-links {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .doc-card {
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            text-decoration: none;
            color: inherit;
            transition: all 0.3s;
        }
        .doc-card:hover {
            border-color: #c7410e;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .doc-card h2 {
            margin-top: 0;
            color: #c7410e;
        }
        .doc-card p {
            color: #666;
            margin-bottom: 0;
        }
        .footer {
            margin-top: 50px;
            text-align: center;
            color: #999;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <h1>🚀 Hybrid Thesis Recommender - API Documentation</h1>
    <p>Choose your preferred documentation format:</p>
    
    <div class="doc-links">
        <a href="swagger-ui.html" class="doc-card">
            <h2>📘 Swagger UI</h2>
            <p>Interactive API documentation with "Try it out" functionality</p>
        </a>
        
        <a href="redoc.html" class="doc-card">
            <h2>📗 Redoc</h2>
            <p>Clean, responsive API documentation</p>
        </a>
        
        <a href="api-docs.md" class="doc-card">
            <h2>📝 Markdown</h2>
            <p>Lightweight documentation in Markdown format</p>
        </a>
        
        <a href="../openapi.yaml" class="doc-card">
            <h2>⚙️ OpenAPI Spec</h2>
            <p>Raw OpenAPI 3.0 specification (YAML)</p>
        </a>
    </div>
    
    <div class="footer">
        <p>Generated automatically from OpenAPI specification</p>
    </div>
</body>
</html>"""
        
        output_file = Path(docs_dir) / "index.html"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(index_html, encoding='utf-8')
        
        print(f"✅ Documentation index created: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Index creation failed: {e}")
        return False


def main():
    """Main documentation generation workflow."""
    print("🚀 API Documentation Generator\n")
    
    spec_path = "openapi.yaml"
    docs_dir = "docs"
    
    # Step 1: Validate OpenAPI spec
    if not validate_openapi_spec(spec_path):
        sys.exit(1)
    
    # Step 2: Generate Redoc HTML
    if not generate_redoc_html(spec_path, f"{docs_dir}/redoc.html"):
        sys.exit(1)
    
    # Step 3: Generate Swagger UI HTML
    if not generate_swagger_ui_html(spec_path, f"{docs_dir}/swagger-ui.html"):
        sys.exit(1)
    
    # Step 4: Generate Markdown docs
    if not generate_markdown_docs(spec_path, f"{docs_dir}/api-docs.md"):
        sys.exit(1)
    
    # Step 5: Create index page
    if not create_docs_index(docs_dir):
        sys.exit(1)
    
    print("\n✅ Documentation generation complete!")
    print(f"\n📂 Documentation available in: {docs_dir}/")
    print(f"   - Open {docs_dir}/index.html in your browser")
    print(f"   - Or run: python -m http.server 8000 --directory {docs_dir}")


if __name__ == "__main__":
    main()
