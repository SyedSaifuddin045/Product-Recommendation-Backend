const express = require('express')

const app = express();

const PORT = 3500;

app.get('/',(req,res) =>{
  res.send('Hello World!')
})

app.listen(PORT,()=>{
  console.log(`Server Running on ${PORT}`)
})
