const http = require('http');
const fs = require('fs');
const path = require('path');

const server = http.createServer((req, res) => {
    let filePath = '.' + req.url.split('?')[0];


    if (filePath === './') {
        filePath = `./index.html`;
    }

    const extname = path.extname(filePath);
    let contentType = 'text/html';

    switch (extname) {
        case '.js':
            contentType = 'text/javascript';
            break;
        case '.css':
            contentType = 'text/css';
            break;
        case '.jpeg':
        case '.jpg':
            contentType = 'image/jpeg';
            break;
    }

    fs.readFile(filePath, (err, content) => {
        if (err) {
            if (err.code === 'ENOENT') {
                // Если файл не найден, возвращаем код 404 (Not Found)
                res.writeHead(404);
                res.end('404 Not Found');
            } else {
                // Если произошла другая ошибка, возвращаем код 500 (Internal Server Error)
                res.writeHead(500);
                res.end('500 Internal Server Error: ' + err.code);
            }
        } else {
            // Успешно найденный файл, отправляем его клиенту с соответствующим contentType
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content, 'utf-8');
        }
    });
});

const PORT = process.env.PORT || 3000;

server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});