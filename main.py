const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
app.use(cors());

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Хранилище реакций по каналам
const channelReactions = {};

io.on('connection', (socket) => {
  console.log('Новое подключение:', socket.id);

  // Обработка присоединения к каналу
  socket.on('join_channel', (channel) => {
    socket.join(channel);
    
    // Инициализируем реакции для канала, если их нет
    if (!channelReactions[channel]) {
      channelReactions[channel] = {
        like: 0,
        thanks: 0,
        lag: 0,
        scary: 0
      };
    }
    
    // Отправляем текущие реакции новому пользователю
    socket.emit('reactions_init', channelReactions[channel]);
  });

  // Обработка реакции
  socket.on('send_reaction', ({ channel, type }) => {
    if (channelReactions[channel] && channelReactions[channel][type] !== undefined) {
      channelReactions[channel][type]++;
      
      // Отправляем обновление всем в канале
      io.to(channel).emit('reaction_update', {
        type,
        count: channelReactions[channel][type]
      });
    }
  });

  socket.on('disconnect', () => {
    console.log('Отключение:', socket.id);
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Сервер запущен на порту ${PORT}`);
});
