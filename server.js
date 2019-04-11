const express = require("express");
const mongoose = require("mongoose");
const bodyParser = require("body-parser");
const path = require("path");

const app = express();

// Bodyparser middleware
app.use(
  bodyParser.urlencoded({
    extended: false
  })
);
app.use(bodyParser.json());

// Routes
app.get("/stocks/:id", (req, res) => {
  var { PythonShell } = require("python-shell");
  var pyshell = new PythonShell("testScriptFormattedData.py");

  pyshell.send(JSON.stringify(req.params.id));

  pyshell.on("message", function(message) {
    // received a message sent from the Python script (a simple "print" statement)
    const hmm = JSON.parse(message);
    res.json(message);
  });

  // end the input stream and allow the process to exit
  pyshell.end(function(err) {
    if (err) {
      throw err;
    }

    console.log("finished");
  });
});

// Routes
app.get("/stockinfo/:id/:date", (req, res) => {
  var { PythonShell } = require("python-shell");
  var pyshell = new PythonShell("getStockInfo.py");

  pyshell.send(JSON.stringify(req.params.id));
  pyshell.send(JSON.stringify(req.params.date));

  pyshell.on("message", function(message) {
    // received a message sent from the Python script (a simple "print" statement)
    const hmm = JSON.parse(message);
    res.json(message);
  });

  // end the input stream and allow the process to exit
  pyshell.end(function(err) {
    if (err) {
      throw err;
    }

    console.log("finished");
  });
});

if (process.env.NODE_ENV === "production") {
  //set static folder
  app.use(express.static("client/build"));

  app.get("*", (req, res) => {
    res.sendFile(path.resolve(__dirname, "client", "build", "index.html"));
  });
}

const port = process.env.PORT || 5000;

app.listen(port, () => console.log(`Server up and running on port ${port} !`));
