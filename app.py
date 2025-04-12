import os
import mimetypes
from flask import Flask, send_from_directory, render_template_string

app = Flask(__name__)


DIRECTORY = "media_files"
@app.route('/')
@app.route('/<path:path>/')
def file_list(path=""):
    requested_dir = os.path.join(DIRECTORY, path) if path else DIRECTORY
    
    # Security check
    if not os.path.exists(requested_dir) or not os.path.isdir(requested_dir):
        return "Directory not found or is not accessible"
        
    # Get file list
    files = []
    dirs = []
    
    for item in os.listdir(requested_dir):
        item_path = os.path.join(requested_dir, item)
        item_rel_path = os.path.join(path, item) if path else item
        
        if os.path.isdir(item_path):
            dirs.append((item, item_rel_path))
        else:
            mime_type = mimetypes.guess_type(item_path)[0] or "application/octet-stream"
            icon = get_icon_for_mime(mime_type)
            size = os.path.getsize(item_path)
            size_str = format_size(size)
            
            files.append((item, item_rel_path, icon, size_str))
    

    dirs.sort()
    files.sort()
    

    parent_link = ""
    if path:
        parent_dir = os.path.dirname(path)
        parent_link = f'<div class="directory-item"><a href="/{parent_dir}"><span class="icon">📂</span><span class="name">..</span></a></div>'
    

    dir_links = []
    for name, dir_path in dirs:
        dir_links.append(f'<div class="directory-item"><a href="/{dir_path}/"><span class="icon">📁</span><span class="name">{name}</span></a></div>')
    

    file_links = []
    for name, file_path, icon, size in files:
        file_links.append(f'''
        <div class="file-item">
            <a href="/download/{file_path}" class="file-link">
                <span class="icon">{icon}</span>
                <span class="name">{name}</span>
                <span class="size">{size}</span>
            </a>
        </div>
        ''')
    

    breadcrumbs = create_breadcrumbs(path)
    

    template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>File Explorer</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }
            .header { background-color: #2c3e50; color: white; padding: 15px; text-align: center; }
            .breadcrumb { padding: 10px; background-color: #ecf0f1; border-bottom: 1px solid #ddd; }
            .breadcrumb a { color: #3498db; text-decoration: none; margin: 0 5px; }
            .container { max-width: 1000px; margin: 0 auto; padding: 20px; background: white; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }
            .file-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); grid-gap: 15px; }
            .file-item, .directory-item { border: 1px solid #ddd; border-radius: 5px; padding: 10px; text-align: center; }
            .directory-item { background-color: #f0f7ff; }
            .file-item:hover, .directory-item:hover { background-color: #f9f9f9; }
            .icon { font-size: 24px; display: block; margin-bottom: 5px; }
            .name { display: block; word-break: break-word; margin-bottom: 5px; }
            .size { display: block; font-size: 12px; color: #777; }
            a { text-decoration: none; color: #333; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>File Explorer</h1>
        </div>
        <div class="breadcrumb">
            {{ breadcrumbs | safe }}
        </div>
        <div class="container">
            <div class="file-grid">
                {{ parent_link | safe }}
                {% for link in dir_links %}
                    {{ link | safe }}
                {% endfor %}
                {% for link in file_links %}
                    {{ link | safe }}
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(template, 
                                breadcrumbs=breadcrumbs,
                                parent_link=parent_link,
                                dir_links=dir_links,
                                file_links=file_links)

@app.route('/download/<path:filepath>')
def download_file(filepath):
    mime_type = mimetypes.guess_type(filepath)[0]
    if mime_type and mime_type.startswith(('image/', 'video/', 'audio/')):
        return send_from_directory(DIRECTORY, filepath, as_attachment=False)
    return send_from_directory(DIRECTORY, filepath, as_attachment=True)

def get_icon_for_mime(mime_type):
    if not mime_type:
        return "📄"
    
    if mime_type.startswith("image/"):
        return "🖼️"
    elif mime_type.startswith("video/"):
        return "🎬"
    elif mime_type.startswith("audio/"):
        return "🎵"
    elif mime_type.startswith("text/"):
        return "📝"
    elif "pdf" in mime_type:
        return "📑"
    else:
        return "📄"

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def create_breadcrumbs(path):
    if not path:
        return '<a href="/">Home</a>'
    
    parts = path.split(os.sep)
    crumbs = ['<a href="/">Home</a>']
    
    current_path = ""
    for part in parts:
        if part:
            current_path = os.path.join(current_path, part)
            crumbs.append(f'<a href="/{current_path}/">{part}</a>')
    
    return ' / '.join(crumbs)

if __name__ == "__main__":
    mimetypes.init()
    app.run()
