import { Button, Tooltip } from 'antd';
import { BulbOutlined, BulbFilled } from '@ant-design/icons';
import { useTheme } from './ThemeProvider';

const ThemeToggle = ({ size = 'middle', type = 'text', style = {} }) => {
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <Tooltip title={isDarkMode ? '切换到亮色主题' : '切换到深色主题'}>
      <Button
        type={type}
        size={size}
        icon={isDarkMode ? <BulbFilled /> : <BulbOutlined />}
        onClick={toggleTheme}
        style={{
          color: isDarkMode ? '#faad14' : '#1890ff',
          ...style,
        }}
      />
    </Tooltip>
  );
};

export default ThemeToggle;