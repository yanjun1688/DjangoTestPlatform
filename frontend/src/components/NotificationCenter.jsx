import { useState, useEffect } from 'react';
import { 
  Badge, Button, Dropdown, List, Avatar, Space, Typography, 
  Empty, Spin, Divider, Tooltip, Card 
} from 'antd';
import { 
  BellOutlined, 
  UserOutlined, 
  CheckOutlined, 
  DeleteOutlined,
  EyeOutlined 
} from '@ant-design/icons';
import PropTypes from 'prop-types';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import ErrorHandler from '../utils/errorHandler';
import './NotificationCenter.css';

const { Text } = Typography;

const NotificationItem = ({ notification, onMarkRead, onNavigate }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    if (!notification.read) {
      onMarkRead([notification.id]);
    }
    if (notification.target_url) {
      onNavigate();
      navigate(notification.target_url);
    }
  };

  const getVerbText = (verb) => {
    const verbMap = {
      'mentioned': '提及了你',
      'replied': '回复了你的评论',
      'commented': '评论了',
      'test_completed': '测试完成',
      'test_failed': '测试失败',
    };
    return verbMap[verb] || verb;
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInSeconds = Math.floor((now - time) / 1000);
    
    if (diffInSeconds < 60) return '刚刚';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}分钟前`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}小时前`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}天前`;
    
    return time.toLocaleDateString('zh-CN');
  };

  return (
    <List.Item
      className={`notification-item ${!notification.read ? 'unread' : ''}`}
      onClick={handleClick}
    >
      <List.Item.Meta
        avatar={
          <Avatar
            size="small"
            icon={<UserOutlined />}
            src={notification.actor.avatar}
          />
        }
        title={
          <div className="notification-title">
            <span className="actor-name">
              {notification.actor.first_name || notification.actor.username}
            </span>
            <span className="verb-text">{getVerbText(notification.verb)}</span>
            {!notification.read && <div className="unread-dot" />}
          </div>
        }
        description={
          <div className="notification-description">
            <div className="target-name">{notification.target_name}</div>
            {notification.action_content && (
              <div className="action-content">
                "{notification.action_content}"
              </div>
            )}
            <div className="notification-time">
              {formatTimeAgo(notification.timestamp)}
            </div>
          </div>
        }
      />
    </List.Item>
  );
};

const NotificationCenter = ({ currentUser }) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [visible, setVisible] = useState(false);
  const [filter, setFilter] = useState('all'); // 'all', 'unread'

  useEffect(() => {
    if (currentUser) {
      fetchNotificationSummary();
      // 每30秒更新一次通知摘要
      const interval = setInterval(fetchNotificationSummary, 30000);
      return () => clearInterval(interval);
    }
  }, [currentUser]);

  const fetchNotificationSummary = async () => {
    try {
      const response = await api.get('/api/comments/notifications/summary/');
      setUnreadCount(response.data.unread_count);
    } catch (error) {
      // 静默处理错误，避免频繁提示
      console.error('Failed to fetch notification summary:', error);
    }
  };

  const fetchNotifications = async (readFilter = filter) => {
    setLoading(true);
    try {
      const params = {};
      if (readFilter === 'unread') {
        params.read = 'false';
      }
      
      const response = await api.get('/api/comments/notifications/', { params });
      setNotifications(response.data.results || []);
    } catch (error) {
      ErrorHandler.handleApiError(error, '获取通知失败');
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationIds = []) => {
    try {
      await api.post('/api/comments/notifications/mark-read/', {
        notification_ids: notificationIds
      });
      
      // 更新本地状态
      if (notificationIds.length === 0) {
        // 标记所有为已读
        setNotifications(prev => 
          prev.map(n => ({ ...n, read: true }))
        );
        setUnreadCount(0);
      } else {
        // 标记指定通知为已读
        setNotifications(prev =>
          prev.map(n => 
            notificationIds.includes(n.id) ? { ...n, read: true } : n
          )
        );
        setUnreadCount(prev => Math.max(0, prev - notificationIds.length));
      }
    } catch (error) {
      ErrorHandler.handleApiError(error, '标记已读失败');
    }
  };

  const handleVisibleChange = (visible) => {
    setVisible(visible);
    if (visible) {
      fetchNotifications();
    }
  };

  const handleFilterChange = (newFilter) => {
    setFilter(newFilter);
    fetchNotifications(newFilter);
  };

  const notificationMenu = (
    <Card className="notification-dropdown" title={
      <div className="notification-header">
        <span>通知</span>
        <Space>
          <Button
            type="text"
            size="small"
            className={filter === 'all' ? 'active' : ''}
            onClick={() => handleFilterChange('all')}
          >
            全部
          </Button>
          <Button
            type="text"
            size="small"
            className={filter === 'unread' ? 'active' : ''}
            onClick={() => handleFilterChange('unread')}
          >
            未读 {unreadCount > 0 && `(${unreadCount})`}
          </Button>
        </Space>
      </div>
    }>
      <div className="notification-content">
        {loading ? (
          <div className="loading-container">
            <Spin size="small" />
          </div>
        ) : notifications.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={filter === 'unread' ? '没有未读通知' : '没有通知'}
          />
        ) : (
          <>
            <List
              className="notification-list"
              dataSource={notifications}
              renderItem={(notification) => (
                <NotificationItem
                  key={notification.id}
                  notification={notification}
                  onMarkRead={markAsRead}
                  onNavigate={() => setVisible(false)}
                />
              )}
            />
            
            {unreadCount > 0 && (
              <>
                <Divider />
                <div className="notification-actions">
                  <Button
                    type="text"
                    size="small"
                    icon={<CheckOutlined />}
                    onClick={() => markAsRead()}
                  >
                    全部标记为已读
                  </Button>
                </div>
              </>
            )}
          </>
        )}
      </div>
    </Card>
  );

  if (!currentUser) {
    return null;
  }

  return (
    <Dropdown
      overlay={notificationMenu}
      placement="bottomRight"
      trigger={['click']}
      visible={visible}
      onVisibleChange={handleVisibleChange}
      overlayClassName="notification-dropdown-overlay"
    >
      <Tooltip title="通知">
        <Badge count={unreadCount} size="small" offset={[-2, 2]}>
          <Button
            type="text"
            icon={<BellOutlined />}
            className="notification-bell"
          />
        </Badge>
      </Tooltip>
    </Dropdown>
  );
};

NotificationCenter.propTypes = {
  currentUser: PropTypes.object
};

NotificationItem.propTypes = {
  notification: PropTypes.object.isRequired,
  onMarkRead: PropTypes.func.isRequired,
  onNavigate: PropTypes.func.isRequired
};

export default NotificationCenter;