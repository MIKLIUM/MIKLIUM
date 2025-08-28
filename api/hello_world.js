module.exports = async function handler(req, res) {
  try {
    if (req.method === "GET") {
        res.status(200).json({
          hello: "world"
        });
    } 
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
// fifth attempt lol