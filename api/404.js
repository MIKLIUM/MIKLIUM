async function handler(req, res) {
  res.status(404).json({ success: false, error: "Not Found. List and documentation of available MIKLIUM APIs: https://github.com/MIKLIUM/MIKLIUM/blob/main/APIDOCS.md" });
};
module.exports = handler;