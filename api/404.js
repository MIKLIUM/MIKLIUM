async function handler(req, res) {
  res.status(404).json({ success: false, error: "Not Found" });
};
module.exports = handler;