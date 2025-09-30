const axios = require('axios');
const cheerio = require('cheerio');

function isLowValue(text) {
  if (!text || text.length < 20) return true;
  const badPhrases = [
    'Loading...',
    'Creating an answer',
    'AI-generated answer',
    'We weren’t able to create a summary',
    'Refresh your page'
  ];
  return badPhrases.some(phrase => text.includes(phrase));
}

function isQualityContent(text) {
  if (!text) return false;
  const words = text.trim().split(/\s+/);
  const wordCount = words.length;
  if (wordCount < 15) return false;
  const upperCaseCount = (text.match(/[A-Z]/g) || []).length;
  const upperCaseRatio = upperCaseCount / wordCount;
  return upperCaseRatio < 0.4 && wordCount > 100;
}

function cleanHtmlText(html) {
  if (!html) return '';
  const $ = cheerio.load(html);
  $('script, style, nav, footer, header, .advertisement, .ads, noscript, iframe').remove();
  $('*').each((i, elem) => {
    $(elem).removeAttr('class').removeAttr('id').removeAttr('style');
  });
  return $('body').text().trim().replace(/\s+/g, ' ');
}

async function fetchWithFallback(url, maxSymbols = 5000, maxRetries = 2) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await axios.get(url, {
        timeout: 8000,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
      });
      const cleaned = cleanHtmlText(response.data);
      if (isQualityContent(cleaned)) {
        return cleaned.substring(0, maxSymbols);
      }
    } catch (error) {
      if (i === maxRetries - 1) throw error;
    }
  }
  throw new Error('Content not qualified');
}

async function handler(request, response) {
  let search = [];
  let maxSmallSnippets = 5;
  let maxLargeSnippets = 2;
  let maxLargeSnippetSymbols = 4500;

  try {
    if (request.method === 'GET') {
      const url = request.url;
      const queryStart = url.indexOf('?');
      if (queryStart !== -1) {
        const queryString = url.substring(queryStart + 1);
        const params = new URLSearchParams(queryString);
        const searchParam = params.get('search');
        search = searchParam ? searchParam.split('~').map(s => s.trim()).filter(Boolean) : [];
        const maxSmall = parseInt(params.get('maxSmallSnippets'), 10);
        const maxLarge = parseInt(params.get('maxLargeSnippets'), 10);
        const maxSymbols = parseInt(params.get('maxLargeSnippetSymbols'), 10);
        if (!isNaN(maxSmall) && maxSmall >= 0) maxSmallSnippets = maxSmall;
        if (!isNaN(maxLarge) && maxLarge >= 0) maxLargeSnippets = maxLarge;
        if (!isNaN(maxSymbols) && maxSymbols > 0) maxLargeSnippetSymbols = maxSymbols;
      }
    } else if (request.method === 'POST') {
      let body = '';
      for await (const chunk of request) {
        body += chunk.toString();
      }
      let parsed;
      try {
        parsed = JSON.parse(body);
      } catch (e) {
        response.writeHead(200, { 'Content-Type': 'application/json' });
        response.end(JSON.stringify({ success: false, error: 'Invalid JSON' }));
        return;
      }
      search = Array.isArray(parsed.search) ? parsed.search : [];
      if (typeof parsed.maxSmallSnippets === 'number' && parsed.maxSmallSnippets >= 0) maxSmallSnippets = parsed.maxSmallSnippets;
      if (typeof parsed.maxLargeSnippets === 'number' && parsed.maxLargeSnippets >= 0) maxLargeSnippets = parsed.maxLargeSnippets;
      if (typeof parsed.maxLargeSnippetSymbols === 'number' && parsed.maxLargeSnippetSymbols > 0) maxLargeSnippetSymbols = parsed.maxLargeSnippetSymbols;
    } else {
      response.writeHead(405, { 'Content-Type': 'application/json' });
      response.end(JSON.stringify({ success: false, error: 'Method not allowed' }));
      return;
    }

    if (!Array.isArray(search) || search.length === 0) {
      response.writeHead(200, { 'Content-Type': 'application/json' });
      response.end(JSON.stringify({ success: false, error: 'Invalid or missing "search" parameter' }));
      return;
    }

    const results = [];
    const processedDomains = new Set();

    for (const query of search.slice(0, 5)) {
      const queryDomains = new Set();
      let queryShortCount = 0;
      let queryLongCount = 0;

      try {
        const formattedQuery = encodeURIComponent(query.trim());
        const searchUrl = `https://search.yahoo.com/search?p=${formattedQuery}`;

        const resp = await axios.get(searchUrl, {
          headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
          },
          timeout: 10000
        });

        const html = resp.data;
        const elements = html.split('<div class="compText');

        for (const element of elements.slice(1)) {
          if (queryShortCount >= maxSmallSnippets && queryLongCount >= maxLargeSnippets) {
            break;
          }

          const snippetEnd = element.indexOf('</div>');
          if (snippetEnd === -1) continue;
          const snippetHtml = element.substring(0, snippetEnd);
          const snippetRaw = cleanHtmlText(snippetHtml);
          const snippet = snippetRaw.split('>')[1]?.trim() || snippetRaw.trim();

          let realUrl = null;
          const rkSplits = element.split('/RK=2/');
          if (rkSplits.length > 1) {
            const firstPart = rkSplits[0];
            const equalsSplits = firstPart.split('=');
            if (equalsSplits.length > 1) {
              const encodedLink = equalsSplits[equalsSplits.length - 1];
              try {
                const decoded = decodeURIComponent(encodedLink);
                realUrl = decoded.split('#')[0].split('?')[0];
                new URL(realUrl);
              } catch (e) {
                realUrl = null;
              }
            }
          }

          if (maxSmallSnippets > 0 && queryShortCount < maxSmallSnippets) {
            if (realUrl && snippet && !isLowValue(snippet) && snippet.length > 30) {
              results.push({
                url: realUrl,
                snippet,
                type: 'short',
                symbols: snippet.length,
                query: query
              });
              queryShortCount++;
            }
          }

          if (maxLargeSnippets > 0 && queryLongCount < maxLargeSnippets && realUrl) {
            const urlObj = new URL(realUrl);
            const domain = `${urlObj.protocol}//${urlObj.hostname}`;
            if (!processedDomains.has(domain) && !queryDomains.has(domain)) {
              queryDomains.add(domain);
              processedDomains.add(domain);
              try {
                const fullContent = await fetchWithFallback(realUrl, maxLargeSnippetSymbols);
                results.push({
                  url: realUrl,
                  snippet: fullContent,
                  type: 'long',
                  symbols: fullContent.length,
                  query: query
                });
                queryLongCount++;
              } catch (e) {}
            }
          }
        }
      } catch (e) {
        continue;
      }
    }

    if (results.length === 0) {
      response.writeHead(200, { 'Content-Type': 'application/json' });
      response.end(JSON.stringify({
        success: false,
        error: 'No valid results found for the given queries'
      }));
    } else {
      response.writeHead(200, { 'Content-Type': 'application/json' });
      response.end(JSON.stringify({
        results,
        success: true
      }));
    }
  } catch (error) {
    console.error('Handler error:', error.message || error);
    response.writeHead(200, { 'Content-Type': 'application/json' });
    response.end(JSON.stringify({
      success: false,
      error: error.message || 'An unexpected error occurred'
    }));
  }
}

module.exports = handler;