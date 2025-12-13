async function handler(request, response) {
  res.status(404).json({ success: false, error: Not Found });
};
module.exports = handler;