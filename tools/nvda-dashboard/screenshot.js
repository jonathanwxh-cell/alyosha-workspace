const http = require('http');
const fs = require('fs');
const path = require('path');

const server = http.createServer((req, res) => {
    let filePath = req.url === '/' ? '/index.html' : req.url;
    const fullPath = path.join(__dirname, filePath);
    const ext = path.extname(fullPath);
    const contentTypes = {
        '.html': 'text/html',
        '.json': 'application/json',
        '.js': 'text/javascript',
        '.css': 'text/css'
    };
    
    fs.readFile(fullPath, (err, content) => {
        if (err) {
            res.writeHead(404);
            res.end('Not found');
        } else {
            res.writeHead(200, { 'Content-Type': contentTypes[ext] || 'text/plain' });
            res.end(content);
        }
    });
});

server.listen(8888, () => {
    console.log('Server on 8888');
    setTimeout(() => {
        console.log('Ready');
        process.exit(0);
    }, 100);
});
