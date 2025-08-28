module.exports = async function handler(req, res) {
  try {
    if (req.method === "GET") {
        res.status(200).json({
          hello: "world"
        });
    }
};