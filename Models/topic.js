const { DataTypes } = require('sequelize');
const sequelize = require('../Config/database-config');
const User = require('./user');

const Topic = sequelize.define('Topic', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false,
  },
  description: {
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
  }
}, {
    tableName: "topics",
    timestamps: true
});

Topic.belongsTo(User, { foreignKey: 'authorId' });

module.exports = Topic;