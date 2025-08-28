module.exports = async function handler(req, res) {
  try {
    if (req.method === "GET") {
        res.status(200).json({
          Hello: "MIKLIUM"
        });
    } 
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};