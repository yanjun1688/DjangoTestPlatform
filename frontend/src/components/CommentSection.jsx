import { useState, useEffect } from 'react';
import { Card, Button, Avatar, Space, Divider, message, Input, Tooltip, Popconfirm } from 'antd';
import { UserOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import PropTypes from 'prop-types';
import api from '../utils/api';
import ErrorHandler from '../utils/errorHandler';
import MentionInput from './MentionInput';
import './CommentSection.css';

const { TextArea } = Input;

const CommentItem = ({ comment, onReply, onEdit, onDelete, currentUser, level = 0 }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(comment.content);
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [replyContent, setReplyContent] = useState('');
  const [loading, setLoading] = useState(false);

  const handleEdit = async () => {
    if (!editContent.trim()) {
      message.warning('评论内容不能为空');
      return;
    }

    setLoading(true);
    try {
      await api.put(`/api/comments/${comment.id}/`, {
        content: editContent
      });
      setIsEditing(false);
      onEdit();
      ErrorHandler.showSuccess('评论编辑成功');
    } catch (error) {
      ErrorHandler.handleApiError(error, '编辑评论失败');
    } finally {
      setLoading(false);
    }
  };

  const handleReply = async () => {
    if (!replyContent.trim()) {
      message.warning('回复内容不能为空');
      return;
    }

    setLoading(true);
    try {
      await onReply(comment.id, replyContent);
      setShowReplyForm(false);
      setReplyContent('');
      ErrorHandler.showSuccess('回复成功');
    } catch (error) {
      ErrorHandler.handleApiError(error, '回复失败');
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString('zh-CN');
  };

  const canEdit = currentUser && currentUser.id === comment.author.id;
  const canDelete = currentUser && (currentUser.id === comment.author.id || currentUser.is_staff);

  return (
    <div className={`comment-item ${level > 0 ? 'comment-reply' : ''}`} style={{ marginLeft: level * 20 }}>
      <Card size="small" className="comment-card">
        <div className="comment-header">
          <Space>
            <Avatar
              size="small"
              icon={<UserOutlined />}
              src={comment.author.avatar}
            />
            <span className="comment-author">
              {comment.author.first_name || comment.author.username}
            </span>
            <span className="comment-time">{formatTimestamp(comment.timestamp)}</span>
            {comment.updated_at !== comment.timestamp && (
              <span className="comment-edited">(已编辑)</span>
            )}
          </Space>

          <Space>
            {canEdit && (
              <Tooltip title="编辑">
                <Button
                  type="text"
                  size="small"
                  icon={<EditOutlined />}
                  onClick={() => setIsEditing(true)}
                />
              </Tooltip>
            )}
            {canDelete && (
              <Popconfirm
                title="确定删除这条评论吗？"
                onConfirm={() => onDelete(comment.id)}
                okText="确定"
                cancelText="取消"
              >
                <Tooltip title="删除">
                  <Button
                    type="text"
                    size="small"
                    icon={<DeleteOutlined />}
                    danger
                  />
                </Tooltip>
              </Popconfirm>
            )}
          </Space>
        </div>

        <div className="comment-content">
          {isEditing ? (
            <div className="comment-edit-form">
              <MentionInput
                value={editContent}
                onChange={setEditContent}
                placeholder="编辑评论..."
                rows={3}
              />
              <div className="comment-edit-actions">
                <Space>
                  <Button
                    type="primary"
                    size="small"
                    loading={loading}
                    onClick={handleEdit}
                  >
                    保存
                  </Button>
                  <Button
                    size="small"
                    onClick={() => {
                      setIsEditing(false);
                      setEditContent(comment.content);
                    }}
                  >
                    取消
                  </Button>
                </Space>
              </div>
            </div>
          ) : (
            <div 
              className="comment-text"
              dangerouslySetInnerHTML={{ 
                __html: comment.content.replace(/@(\w+)/g, '<span class="mention">@$1</span>') 
              }}
            />
          )}
        </div>

        {!isEditing && level === 0 && (
          <div className="comment-actions">
            <Button
              type="text"
              size="small"
              onClick={() => setShowReplyForm(!showReplyForm)}
            >
              回复
            </Button>
          </div>
        )}

        {showReplyForm && (
          <div className="reply-form">
            <MentionInput
              value={replyContent}
              onChange={setReplyContent}
              placeholder={`回复 @${comment.author.username}...`}
              rows={2}
            />
            <div className="reply-actions">
              <Space>
                <Button
                  type="primary"
                  size="small"
                  loading={loading}
                  onClick={handleReply}
                >
                  回复
                </Button>
                <Button
                  size="small"
                  onClick={() => {
                    setShowReplyForm(false);
                    setReplyContent('');
                  }}
                >
                  取消
                </Button>
              </Space>
            </div>
          </div>
        )}
      </Card>

      {/* 渲染回复 */}
      {comment.replies && comment.replies.length > 0 && (
        <div className="comment-replies">
          {comment.replies.map(reply => (
            <CommentItem
              key={reply.id}
              comment={reply}
              onReply={onReply}
              onEdit={onEdit}
              onDelete={onDelete}
              currentUser={currentUser}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const CommentSection = ({ targetType, targetId, currentUser }) => {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newComment, setNewComment] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (targetType && targetId) {
      fetchComments();
    }
  }, [targetType, targetId]);

  const fetchComments = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/comments/', {
        params: {
          target_type: targetType,
          target_id: targetId,
        }
      });
      setComments(response.data.results || []);
    } catch (error) {
      ErrorHandler.handleApiError(error, '获取评论失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitComment = async () => {
    if (!newComment.trim()) {
      message.warning('评论内容不能为空');
      return;
    }

    setSubmitting(true);
    try {
      await api.post('/api/comments/create/', {
        content: newComment,
        target_type: targetType,
        target_id: targetId,
      });
      setNewComment('');
      await fetchComments();
      ErrorHandler.showSuccess('评论发布成功');
    } catch (error) {
      ErrorHandler.handleApiError(error, '发布评论失败');
    } finally {
      setSubmitting(false);
    }
  };

  const handleReply = async (parentCommentId, content) => {
    try {
      await api.post('/api/comments/create/', {
        content,
        target_type: targetType,
        target_id: targetId,
        parent_comment_id: parentCommentId,
      });
      await fetchComments();
    } catch (error) {
      throw error;
    }
  };

  const handleDelete = async (commentId) => {
    try {
      await api.delete(`/api/comments/${commentId}/`);
      await fetchComments();
      ErrorHandler.showSuccess('评论删除成功');
    } catch (error) {
      ErrorHandler.handleApiError(error, '删除评论失败');
    }
  };

  if (!currentUser) {
    return (
      <Card title="讨论区" className="comment-section">
        <div className="login-prompt">
          请先登录后参与讨论
        </div>
      </Card>
    );
  }

  return (
    <Card title="讨论区" className="comment-section" loading={loading}>
      {/* 新评论表单 */}
      <div className="new-comment-form">
        <MentionInput
          value={newComment}
          onChange={setNewComment}
          placeholder="写下你的想法..."
          rows={3}
        />
        <div className="new-comment-actions">
          <Button
            type="primary"
            loading={submitting}
            onClick={handleSubmitComment}
            disabled={!newComment.trim()}
          >
            发布评论
          </Button>
        </div>
      </div>

      <Divider />

      {/* 评论列表 */}
      <div className="comments-list">
        {comments.length === 0 ? (
          <div className="no-comments">
            还没有评论，来发表第一个吧！
          </div>
        ) : (
          comments.map(comment => (
            <CommentItem
              key={comment.id}
              comment={comment}
              onReply={handleReply}
              onEdit={fetchComments}
              onDelete={handleDelete}
              currentUser={currentUser}
            />
          ))
        )}
      </div>
    </Card>
  );
};

CommentSection.propTypes = {
  targetType: PropTypes.oneOf(['testcase', 'testreport']).isRequired,
  targetId: PropTypes.number.isRequired,
  currentUser: PropTypes.object
};

CommentItem.propTypes = {
  comment: PropTypes.object.isRequired,
  onReply: PropTypes.func.isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
  currentUser: PropTypes.object,
  level: PropTypes.number
};

export default CommentSection;