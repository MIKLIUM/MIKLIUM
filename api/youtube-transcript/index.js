const cheerio = require('cheerio');

export default async function handler(req, res) {
  try {
    const videoId = extractVideoId(req.query.url);

    if (!videoId) {
      return res.status(400).json({ error: 'Invalid YouTube URL.' });
    }

    const transcriptUrl = `https://youtubetotranscript.com/transcript?v=${videoId}&current_language_code=en`;

    const response = await fetch(transcriptUrl, {
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0'
      }
    });

    if (!response.ok) {
      return res.status(response.status).json({ error: 'Error fetching transcript' });
    }

    const rawTranscript = await response.text();
    const processedData = processTranscript(rawTranscript);

    res.setHeader('Content-Type', 'application/json');
    res.status(200).json(processedData);
  } catch (error) {
    console.error('Error:', error.message);
    if (error.name === 'AbortError') {
      res.status(504).json({ error: 'Request timed out' });
    } else {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
}

function extractVideoId(url) {
  if (!url) return null;

  const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
  const match = url.match(regExp);
  
  return (match && match[2].length === 11) ? match[2] : url;
}

function processTranscript(rawText) {

  const $ = cheerio.load(rawText);

  let channel = 'Unknown channel';
  const channelMeta = $('meta[name="description"]').attr('content');
  if (channelMeta) {
    const channelMatch = channelMeta.match(/by (.*?)(?: available|$)/);
    if (channelMatch) {
      channel = channelMatch[1].trim();
    }
  }

  let title = 'Unknown title';
  const titleTag = $('title').text();
  if (titleTag) {
    const titleMatch = titleTag.match(/Transcript of (.*?)(?: - YouTubeToTranscript\.com|$)/);
    if (titleMatch) {
      title = titleMatch[1].trim();
    }
  }

  let text = '';
  const transcriptSegments = $('.transcript-segment');
  if (transcriptSegments.length > 0) {
    text = transcriptSegments
      .map((i, el) => $(el).text().trim())
      .get()
      .join(' ');
  } else {
    text = 'No transcript available';
  }
  
  return {
    channel,
    title,
    text
  };
}