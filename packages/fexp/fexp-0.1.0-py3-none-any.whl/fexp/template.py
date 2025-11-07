html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>fexp</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; padding: 20px; background: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { padding: 12px; border-bottom: 1px solid #e0e0e0; display: flex; justify-content: space-between; align-items: center; }
        .breadcrumbs { font-size: 18px; color: #333; font-weight: 500; }
        .breadcrumbs a { color: #007bff; text-decoration: none; }
        .upload-btn { background: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }
        .upload-btn:hover { background: #0056b3; }
        .list { font-size: 14px; padding-bottom: 10px; }
        .item { padding: 12px 15px; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; text-decoration: none; }
        .item:hover { background: #f8f9fa; }
        .item-name { display: flex; align-items: center; gap: 8px; flex: 1; }
        .icon { width: 20px; text-align: center; }
        .item-info { font-size: 12px; color: #999; display: flex; gap: 15px; }
        .dir { color: #007bff; font-weight: 500; }
        .file { color: #333; }
        .loading { text-align: center; padding: 40px; color: #999; }
        input[type="file"] { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="breadcrumbs" id="breadcrumbs"></div>
            <button class="upload-btn" onclick="document.getElementById('fileInput').click()">Upload File</button>
            <input type="file" id="fileInput" onchange="uploadFile(this.files[0])">
        </div>
        <div class="list" id="fileList">
            <div class="loading">Loading...</div>
        </div>
    </div>

    <script>
        const currentPath = location.pathname;
        const parts = currentPath.split('/').filter(p => p.length > 0);
        const breadcrumbs = document.getElementById('breadcrumbs');

        breadcrumbs.innerHTML = '';
        const rootLink = document.createElement('a');
        rootLink.href = '/';
        rootLink.textContent = 'root';
        breadcrumbs.appendChild(rootLink);

        let accumulatedPath = '';
        parts.forEach((part, i) => {
            accumulatedPath += '/' + part;
            breadcrumbs.appendChild(document.createTextNode(' / '));
            if (i < parts.length - 1) {
                const link = document.createElement('a');
                link.href = accumulatedPath;
                link.textContent = part;
                breadcrumbs.appendChild(link);
            } else {
                const span = document.createElement('span');
                span.textContent = part;
                breadcrumbs.appendChild(span);
            }
        });

        async function loadDirectory() {
            try {
                const res = await fetch(currentPath + '?json=1');
                const data = await res.json();
                renderItems(data.items);
            } catch (e) {
                document.getElementById('fileList').innerHTML = '<div class="loading">Failed to load.</div>';
            }
        }

        function renderItems(items) {
            const list = document.getElementById('fileList');
            list.innerHTML = '';

            if (currentPath !== '/') {
                const parent = document.createElement('a');
                parent.className = 'item';
                parent.setAttribute('href', currentPath.split('/').slice(0, -1).join('/') || '/');
                parent.innerHTML = `<div class="item-name dir"><span class="icon">📁</span>..</div>`;
                parent.onclick = () => location.href = currentPath.split('/').slice(0, -1).join('/') || '/';
                list.appendChild(parent);
            }

            items.forEach(item => {
                const div = document.createElement('a');
                div.className = 'item';
                div.setAttribute('href', `${currentPath.replace(/\/$/, '')}/${item.name}`);
                if (item.type == 'file') {
                    div.setAttribute('target', '_blank');
                }

                const icon = item.type === 'dir' ? '📁' : '📄';
                const nameClass = item.type === 'dir' ? 'dir' : 'file';
                const size = item.type === 'file' ? formatSize(item.size) : '';
                const time = new Date(item.mtime * 1000).toLocaleString();

                div.innerHTML = `
                    <div class="item-name ${nameClass}">
                        <span class="icon">${icon}</span>
                        <span>${item.name}</span>
                    </div>
                    <div class="item-info">
                        ${size ? `<span>${size}</span>` : ''}
                        <span>${time}</span>
                    </div>
                `;

                list.appendChild(div);
            });
        }

        function formatSize(bytes) {
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KiB';
            if (bytes < 1024 * 1024 * 1024) return (bytes / 1024 / 1024).toFixed(1) + ' MiB';
            return (bytes / 1024 / 1024 / 1024).toFixed(1) + ' GiB';
        }

        async function uploadFile(file) {
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            try {
                const res = await fetch(currentPath, {
                    method: 'POST',
                    body: formData
                });
                const result = await res.json();
                if (res.ok) {
                    alert('Upload Success');
                    loadDirectory();
                } else {
                    alert('Upload Failed: ' + result.error);
                }
            } catch (e) {
                alert('Upload Failed: ' + e.message);
            }

            document.getElementById('fileInput').value = '';
        }

        loadDirectory();
    </script>
</body>
</html>
"""
