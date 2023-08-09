const express = require('express')
const http = require('http')
const { PythonShell } = require('python-shell')
const cors = require('cors')
const { Server } = require('socket.io')
const fs = require('fs')

const app = express();
app.use(cors())
const server = http.createServer(app)
const io = new Server(server, {
  cors: {
    origin: ["http://localhost:3000","https://product-recommendation-frontend.vercel.app/"],
    methods: ["GET", "POST", "PUT"],
    allowedHeaders: ['Content-Type', 'Authorization']
  }
})

const PORT = 3500;

app.get('/', (req, res) => {
  res.send('Hello World!')
})

server.listen(PORT, () => {
  console.log(`Server Running on ${PORT}`)
})

io.on('connection', (socket) => {
  console.log('Client connected');

  socket.on('GetFilter', (input) => {
    const pyshell = new PythonShell('GetFilters.py', {
      mode: 'json',
      args: ['-st', input]
    });

    pyshell.on('json', (jsonString) => {
      const filterJson = JSON.parse(jsonString);
      console.log(filterJson)
      socket.emit('filterResult', filterJson);
    });

    pyshell.end((err) => {
      if (err) {
        console.error(err);
        socket.emit('filterError', 'An error occurred');
      }
    });
  });


  socket.on('StartScript', (input) => {
    const pyshell = new PythonShell('ScrapeAmazon.py', { mode: 'text', pythonOptions: ['-u'], args: ['-st', input] })
    console.log("Started running pyhton script")
    pyshell.on('message', (message) => {
      console.log("Message :" + message)
      socket.emit('progress', message);
    });
    pyshell.end(function (err) {
      if (err) {
        console.log("Error Occured :" + err)
      }
      else {
        console.log('Script Execution Finished');

        const filePath = `${input}.json`;

        fs.readFile(filePath, 'utf-8', (err, data) => {
          if (err) {
            console.log("Error reading JSON file: " + err);
          } else {
            socket.emit('json', data, (acknowledgment) => {
              if (acknowledgment == 'success') {
                // After sending the data, delete the file
                fs.unlink(filePath, (deleteErr) => {
                  if (deleteErr) {
                    console.log("Error deleting file: " + deleteErr);
                  } else {
                    console.log("File deleted successfully.");
                  }
                });
              }
            });
          }
        });
      }
    });

  })
  socket.on('disconnect', () => {
    console.log('Client disconnected');
  });
});
