module.exports = async function handler(req, res) {
  try {
    if (req.method === "GET") {
        res.status(200).json({
          test: "test"
        });
    } 
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};