// const express = require('express')

// const app = express();

// const PORT = 3500;

// app.get('/',(req,res) =>{
//   res.send('Hello World!')
// })

// app.listen(PORT,()=>{
//   console.log(`Server Running on ${PORT}`)
// })
const express = require('express');
const { spawn } = require('child_process');
const cors = require('cors');
const app = express();
const server = require('http').Server(app);
const io = require('socket.io')(server, {
  cors: {
    origin: 'http://localhost:3000',
    methods: ['GET', 'POST'],
    allowedHeaders: ['Content-Type', 'Authorization'],
  },
});

const PORT = 3500;

app.use(express.json());
app.use(cors());

// app.use((req, res, next) => {
//   res.header('Access-Control-Allow-Origin', 'http://localhost:3000'); // Replace with your React app's origin
//   res.header('Access-Control-Allow-Methods', 'GET, POST');
//   res.header('Access-Control-Allow-Headers', 'Content-Type');
//   next();
// });

app.get('/', (req, res) => {
  res.send('Hello Backend!');
});

io.on('connection', (socket) => {
  let yourResultArray = [];
  socket.on('startScript', (data) => {
    const { input } = data;

    const python = spawn('python', ['script.py', '-st', input]);

    python.stdout.on('data', (data) => {
      const progress = parseInt(data.toString());
      socket.emit('progress', { progress });
    });

    python.on('close', (code) => {
      // Send the result back to the client
      socket.emit('result', { result: yourResultArray });
    });
  });
});

server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});