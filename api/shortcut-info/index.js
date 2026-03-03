const fetch = require('node-fetch');

async function handler(req, res) {

  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'GET' && req.method !== 'POST') {
    console.log(`Method not allowed: ${req.method}`);
    return res.status(405).json({ success: false, error: 'Method not allowed' });
  }

  let url;
  if (req.method === 'GET') {
    url = req.query.url;
  } else if (req.method === 'POST') {
    try {
      const body = typeof req.body === 'object' ? req.body : JSON.parse(req.body);
      url = body.url;
    } catch (error) {
      console.log(`JSON parse failed: ${error.message}`);
      return res.status(400).json({ success: false, error: 'Invalid JSON in request body' });
    }
  }

  if (!url) {
    console.log('Missing url parameter');
    return res.status(400).json({ success: false, error: 'Missing "url" parameter' });
  }

  url = url.split('#')[0].replace(/\/+$/, '');
  const originalUrl = url;

  let linkType = '';
  let links = {
    iCloudLink: null,
    routineHubLink: null,
    routineHubDirectLink: null
  };
  let shortcutId;

  if (url.startsWith('https://routinehub.co/shortcut/')) {
    linkType = 'RoutineHub Link';
    links.routineHubLink = originalUrl;

    const rhMatch = url.match(/\/shortcut\/(\d+)/);
    if (!rhMatch) {
      console.log(`Invalid RoutineHub URL format: ${url}`);
      return res.status(400).json({ success: false, error: 'Invalid RoutineHub shortcut URL' });
    }
    shortcutId = rhMatch[1];

    try {
      const apiResponse = await fetch(`https://routinehub.co/api/v1/shortcuts/${shortcutId}/versions/latest`, { headers: { 'User-Agent': 'Mozilla/5.0 (compatible; ShortcutResolver/1.0)' } });
      if (!apiResponse.ok) {
        console.log(`RoutineHub API returned ${apiResponse.status} for shortcut ${shortcutId}`);
        return res.status(404).json({
          success: false,
          error: 'RoutineHub shortcut not found'
        });
      }
      const apiData = await apiResponse.json();
      url = apiData.URL;
      links.iCloudLink = url;
      links.routineHubDirectLink = `https://routinehub.co/download/${apiData.id}`;
    } catch (error) {
      console.log(`RoutineHub API fetch failed: ${error.message}`);
      return res.status(502).json({ success: false, error: 'Failed to fetch RoutineHub metadata' });
    }
  }
  else if (url.startsWith('https://routinehub.co/download/')) {
    linkType = 'RoutineHub Direct Download Link';
    links.routineHubDirectLink = originalUrl;

    try {
      const redirectResponse = await fetch(url, {
        method: 'HEAD',
        redirect: 'follow',
        headers: { 'User-Agent': 'Mozilla/5.0 (compatible; ShortcutResolver/1.0)' }
      });

      const finalUrl = redirectResponse.url;

      if (!finalUrl || !finalUrl.includes('icloud.com/shortcuts')) {
        console.log(`RoutineHub redirect did not resolve to iCloud: ${finalUrl}`);
        return res.status(400).json({
          success: false,
          error: 'Final redirected URL is not a valid iCloud shortcut'
        });
      }
      url = finalUrl;
      links.iCloudLink = url;

    } catch (error) {
      console.log(`RoutineHub redirect failed: ${error.message}`);
      return res.status(502).json({ success: false, error: 'Failed to resolve RoutineHub redirect' });
    }
  }
  else if (url.includes('icloud.com/shortcuts')) {
    linkType = 'iCloud Link';
    links.iCloudLink = originalUrl;
  }

  const match = url.match(/\/shortcuts\/([a-f0-9]{32})/i);
  if (!match) {
    console.log(`Could not extract shortcut ID from URL: ${url}`);
    return res.status(400).json({ success: false, error: 'Invalid shortcut URL' });
  }

  const id = match[1].toLowerCase();
  const apiUrl = `https://www.icloud.com/shortcuts/api/records/${id}`;

  try {
    const response = await fetch(apiUrl);
    if (!response.ok) {
      console.log(`iCloud API returned ${response.status} for shortcut ${id}`);
      return res.status(404).json({ success: false, error: 'Shortcut not found' });
    }

    let data;
    try {
      data = await response.json();
    } catch (error) {
      console.log(`iCloud API response parse failed: ${error.message}`);
      return res.status(502).json({ success: false, error: 'Invalid response from iCloud API' });
    }

    let record;
    if (data.records && data.records[id]) {
      record = data.records[id];
    } else if (data.recordName && data.recordName.replace(/-/g, '').toLowerCase() === id) {
      record = data;
    } else {
      console.log(`Record data missing for shortcut ${id}`);
      return res.status(404).json({ success: false, error: 'Record data missing' });
    }

    const fields = record.fields || {};
    const dateOfSharing = record.modified || {};

    const name = fields.name?.value;
    const timestamp = dateOfSharing.timestamp;

    const fileSize = fields.signedShortcut?.value?.size;
    const fileMb = fileSize ? Number((fileSize / (1024 * 1024)).toFixed(2)) : null;
    const fileKb = fileSize ? Number((fileSize / 1024).toFixed(2)) : null;
    const rawFileLink = fields.signedShortcut?.value?.downloadURL;

    const fileUrl = rawFileLink
      ? rawFileLink.replace(/\$\{f\}/g, `${encodeURIComponent(name || 'Shortcut')}.shortcut`)
      : null;

    const plistSize = fields.shortcut?.value?.size;
    const plistMb = plistSize ? Number((plistSize / (1024 * 1024)).toFixed(2)) : null;
    const plistKb = plistSize ? Number((plistSize / 1024).toFixed(2)) : null;
    const rawPlistLink = fields.shortcut?.value?.downloadURL;

    const plistUrl = rawPlistLink
      ? rawPlistLink.replace(/\$\{f\}/g, `${encodeURIComponent(name || 'Shortcut')}.plist`)
      : null;

    const iconColor = fields.icon_color?.value;
    const iconGlyph = fields.icon_glyph?.value;
    const iconSize = fields.icon?.value?.size;
    const imageMb = iconSize ? Number((iconSize / (1024 * 1024)).toFixed(2)) : null;
    const imageKb = iconSize ? Number((iconSize / 1024).toFixed(2)) : null;
    const rawDownloadUrl = fields.icon?.value?.downloadURL;

    const downloadUrl = rawDownloadUrl
      ? rawDownloadUrl.replace(/\$\{f\}/g, `${encodeURIComponent(name || 'Icon')}.png`)
      : null;

    const formatDates = (ts) => {
      if (!ts) return null;
      const d = new Date(ts);
      if (isNaN(d.getTime())) return null;
      return {
        readable: d.toLocaleString('en-US', {
          timeZone: 'UTC',
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        }) + ' (GMT)',
        asInShortcuts: d.toLocaleDateString('en-US', {
          timeZone: 'UTC',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        }).replace(',', ''),
        iso8601: d.toISOString(),
        rfc2822: d.toUTCString(),
        timestamp: ts
      };
    };

    const result = {
      success: true,
      inputType: linkType,
      shortcutLinks: links,
      shortcutData: {
        name,
        dateOfSharing: formatDates(timestamp),
        icon: {
          colorId: iconColor,
          glyphId: iconGlyph,
          size: {
            mb: imageMb,
            kb: imageKb,
            bit: iconSize
          },
          downloadUrl
        },
        signedShortcutFile: {
          isSigned: true,
          size: {
            mb: fileMb,
            kb: fileKb,
            bit: fileSize
          },
          downloadUrl: fileUrl
        },
        plistShortcutFile: {
          size: {
            mb: plistMb,
            kb: plistKb,
            bit: plistSize
          },
          downloadUrl: plistUrl
        }
      }
    };

    res.setHeader('Content-Type', 'application/json');
    return res.status(200).json(result);
  } catch (error) {
    console.log(`Error: ${error.name}`);
    console.log(`Message: ${error.message}`);
    console.log(`Stack: ${error.stack?.split('\n')[1]?.trim()}`);
    return res.status(500).json({ success: false, error: 'Internal server error' });
  }
}

module.exports = handler;