mclient = "mongoclient"
var MongoClient = require('mongodb').MongoClient;
const uri = mclient;
const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });
client.connect(err => {
  const collection = client.db("movies_db").collection("movies_dt");
  // perform actions on the collection object
  client.close();
});

