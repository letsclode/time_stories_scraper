const http = require('http');
const https = require('https');
const url = require('url');

const server = http.createServer((req, res) => {
  if (req.url === '/api/latest_stories' && req.method === 'GET') {
    const requestUrl = 'https://time.com/';
    fetchHTML(requestUrl)
      .then((htmlContent) => {
        const latestStories = extractLatestStories(htmlContent);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(latestStories));
      })
      .catch((error) => {
        console.error(error);
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('Internal Server Error');
      });
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not Found');
  }
});

const PORT = 8000;
server.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

function fetchHTML(requestUrl) {
  return new Promise((resolve, reject) => {
    const protocol = requestUrl.startsWith('https') ? https : http;

    protocol.get(requestUrl, (response) => {
      let data = '';

      response.on('data', (chunk) => {
        data += chunk;
      });

      response.on('end', () => {
        resolve(data);
      });
    }).on('error', (error) => {
      reject(error);
    });
  });
}

function extractLatestStories(htmlContent) {
  const latestStories = [];

  const regex = /<li class="latest-stories__item">.*?<a href="(.*?)">.*?<h3 class="latest-stories__item-headline">(.*?)<\/h3>/gs;
  let match;

  while ((match = regex.exec(htmlContent)) !== null) {
    const link = match[1];
    const title = match[2].trim();
    latestStories.push({ link, title });
  }

  return latestStories;
}
