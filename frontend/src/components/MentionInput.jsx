import { useState, useRef, useEffect } from 'react';
import { Input, List, Card } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import PropTypes from 'prop-types';
import api from '../utils/api';
import './MentionInput.css';

const { TextArea } = Input;

const MentionInput = ({ value, onChange, placeholder, rows = 4, disabled = false }) => {
  const [searchText, setSearchText] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [cursorPosition, setCursorPosition] = useState(0);
  const [mentionStart, setMentionStart] = useState(-1);
  const [selectedIndex, setSelectedIndex] = useState(0);
  
  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);

  // 搜索用户
  const searchUsers = async (query) => {
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }

    try {
      const response = await api.get('/api/comments/users/search/', {
        params: { q: query }
      });
      setSearchResults(response.data || []);
    } catch (error) {
      setSearchResults([]);
    }
  };

  // 处理输入变化
  const handleInputChange = (e) => {
    const newValue = e.target.value;
    const newCursorPosition = e.target.selectionStart;
    
    onChange(newValue);
    setCursorPosition(newCursorPosition);

    // 检查是否在输入@提及
    const beforeCursor = newValue.substring(0, newCursorPosition);
    const mentionMatch = beforeCursor.match(/@(\w*)$/);
    
    if (mentionMatch) {
      const start = newCursorPosition - mentionMatch[0].length;
      const query = mentionMatch[1];
      
      setMentionStart(start);
      setSearchText(query);
      setShowSuggestions(true);
      setSelectedIndex(0);
      searchUsers(query);
    } else {
      setShowSuggestions(false);
      setSearchResults([]);
      setMentionStart(-1);
    }
  };

  // 处理键盘事件
  const handleKeyDown = (e) => {
    if (!showSuggestions || searchResults.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((prev) => 
          prev < searchResults.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) => 
          prev > 0 ? prev - 1 : searchResults.length - 1
        );
        break;
      case 'Enter':
      case 'Tab':
        e.preventDefault();
        if (searchResults[selectedIndex]) {
          insertMention(searchResults[selectedIndex]);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        break;
    }
  };

  // 插入@提及
  const insertMention = (user) => {
    const beforeMention = value.substring(0, mentionStart);
    const afterCursor = value.substring(cursorPosition);
    const mention = `@${user.username} `;
    
    const newValue = beforeMention + mention + afterCursor;
    const newCursorPosition = mentionStart + mention.length;
    
    onChange(newValue);
    setShowSuggestions(false);
    setSearchResults([]);
    setMentionStart(-1);

    // 设置光标位置
    setTimeout(() => {
      if (inputRef.current) {
        inputRef.current.setSelectionRange(newCursorPosition, newCursorPosition);
        inputRef.current.focus();
      }
    }, 0);
  };

  // 处理鼠标点击选择
  const handleSuggestionClick = (user) => {
    insertMention(user);
  };

  // 滚动到选中项
  useEffect(() => {
    if (suggestionsRef.current && showSuggestions) {
      const selectedItem = suggestionsRef.current.querySelector(`.suggestion-item:nth-child(${selectedIndex + 1})`);
      if (selectedItem) {
        selectedItem.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [selectedIndex, showSuggestions]);

  return (
    <div className="mention-input-container">
      <TextArea
        ref={inputRef}
        value={value}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        rows={rows}
        disabled={disabled}
        className="mention-textarea"
      />
      
      {showSuggestions && searchResults.length > 0 && (
        <Card 
          className="mention-suggestions"
          ref={suggestionsRef}
          size="small"
        >
          <List
            size="small"
            dataSource={searchResults}
            renderItem={(user, index) => (
              <List.Item
                className={`suggestion-item ${index === selectedIndex ? 'selected' : ''}`}
                onClick={() => handleSuggestionClick(user)}
              >
                <List.Item.Meta
                  avatar={<UserOutlined />}
                  title={user.display_name}
                  description={`@${user.username}`}
                />
              </List.Item>
            )}
          />
        </Card>
      )}
    </div>
  );
};

MentionInput.propTypes = {
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  rows: PropTypes.number,
  disabled: PropTypes.bool
};

export default MentionInput;