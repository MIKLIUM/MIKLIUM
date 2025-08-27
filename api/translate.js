const fetch = require("node-fetch");

const MYMEMORY_BASE = "https://api.mymemory.translated.net/get";

module.exports = async function handler(req, res) {
  try {
    let text, from, to;

    if (req.method === "GET") {
      text = req.query.q || "";
      from = req.query.from || "auto";
      to = req.query.to || "en";
    } else if (req.method === "POST") {
      const body = req.body || {};
      text = body.q || body.text || "";
      from = body.from || "auto";
      to = body.to || "en";
    } else {
      return res.status(405).json({ success: false, error: "Method not allowed" });
    }

    if (!text) {
      return res.status(400).json({ success: false, error: "Missing text (q)" });
    }

    const url = `${MYMEMORY_BASE}?q=${encodeURIComponent(text)}&langpair=${from}|${to}`;
    const response = await fetch(url);
    const data = await response.json();

    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
    res.setHeader("Content-Type", "application/json");

    if (req.method === "OPTIONS") {
      return res.status(204).end();
    }

    res.status(200).json({
      success: true,
      original: text,
      translated: data?.responseData?.translatedText || "",
      from,
      to
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
};
