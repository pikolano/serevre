const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
app.use(cors());

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*", // Разрешить все домены (можно указать конкретные)
    methods: ["GET", "POST"]
  }
});

// Хранилище реакций (в реальном проекте лучше использовать БД)
const reactions = {
  like: 0,
  thanks: 0,
  lag: 0,
  scary: 0
};

io.on('connection', (socket) => {
  console.log('Новый пользователь подключен:', socket.id);

  // Отправляем текущие реакции новому пользователю
  socket.emit('reactions_update', reactions);

  // Обработка реакции
  socket.on('send_reaction', (type) => {
    if (reactions[type] !== undefined) {
      reactions[type]++;
      io.emit('reactions_update', reactions); // Обновляем у всех
    }
  });

  socket.on('disconnect', () => {
    console.log('Пользователь отключен:', socket.id);
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Сервер запущен на порту ${PORT}`);
});
