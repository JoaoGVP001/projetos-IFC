const { DataTypes } = require('sequelize');
const sequelize = require('../Config/database-config');
const User = require('./user');
const Topic = require('./topic');

const Answer = sequelize.define('Answer', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  },
  text: {
    type: DataTypes.TEXT,
    allowNull: false,
  },
  authorId: {
    type: DataTypes.INTEGER,
    references: {
      model: 'users',
      key: 'id',
    },
    allowNull: false,
  },
  topicId: {
    type: DataTypes.INTEGER,
    references: {
      model: 'topics',
      key: 'id',
    },
    allowNull: false,
  }
}, {
    tableName: "answers",
    timestamps: true
});

Answer.belongsTo(User, { foreignKey: 'authorId' });
Answer.belongsTo(Topic, { foreignKey: 'topicId'})

module.exports = Answer;