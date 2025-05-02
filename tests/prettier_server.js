const http = require('http');
const prettier = require('prettier');

const server = http.createServer(async (req, res) => {
  if (req.method === 'POST' && req.url === '/format') {
    let body = '';
    
    req.on('data', chunk => {
      body += chunk.toString();
    });

    req.on('end', async () => {
      try {
        const formattedCode = await prettier.format(body, {
          parser: 'babel',
          semi: true,
          singleQuote: true,
          trailingComma: 'es5',
        });

        res.writeHead(200, { 'Content-Type': 'text/plain' });
        res.end(formattedCode);
      } catch (error) {
        res.writeHead(400, { 'Content-Type': 'text/plain' });
        res.end(`Error formatting code: ${error.message}`);
      }
    });
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not Found');
  }
});

const PORT = process.env.PORT || 9696;
server.listen(PORT, () => {
  console.log(`Prettier server running on port ${PORT}`);
});

