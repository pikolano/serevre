const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
app.use(cors());

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*", // Разрешаем все домены
    methods: ["GET", "POST"]
  }
});

// Хранилище реакций: { "oneevent1": { like: 0, thanks: 0, ... } }
const reactions = {};

io.on('connection', (socket) => {
  console.log('Новый пользователь:', socket.id);

  // Присоединение к каналу (oneevent1)
  socket.on('join', (channel) => {
    socket.join(channel);
    
    // Инициализация реакций для канала
    if (!reactions[channel]) {
      reactions[channel] = {
        like: 0,
        thanks: 0,
        lag: 0,
        scary: 0
      };
    }

    // Отправляем текущие реакции
    socket.emit('reactions', reactions[channel]);
  });

  // Обработка реакции
  socket.on('reaction', ({ channel, type }) => {
    if (reactions[channel] && reactions[channel][type] !== undefined) {
      reactions[channel][type]++;
      // Отправляем обновление всем в канале
      io.to(channel).emit('reactions', reactions[channel]);
    }
  });

  socket.on('disconnect', () => {
    console.log('Отключен:', socket.id);
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Сервер запущен на порту ${PORT}`);
});
