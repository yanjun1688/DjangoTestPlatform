import { createContext, useContext, useState, useEffect } from 'react';
import { ConfigProvider, theme } from 'antd';
import PropTypes from 'prop-types';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

const ThemeProvider = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(isDarkMode));
    // 更新body类名以应用全局样式
    document.body.className = isDarkMode ? 'dark-theme' : 'light-theme';
  }, [isDarkMode]);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  const themeConfig = {
    algorithm: isDarkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
    token: {
      colorPrimary: '#1890ff',
      colorSuccess: '#52c41a',
      colorWarning: '#faad14',
      colorError: '#ff4d4f',
      colorInfo: '#1890ff',
      colorLink: '#1890ff',
      colorBgBase: isDarkMode ? '#141414' : '#ffffff',
      colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
      colorBgElevated: isDarkMode ? '#262626' : '#ffffff',
      colorBorder: isDarkMode ? '#434343' : '#d9d9d9',
      colorBorderSecondary: isDarkMode ? '#303030' : '#f0f0f0',
      colorText: isDarkMode ? '#ffffff' : '#000000',
      colorTextSecondary: isDarkMode ? '#a6a6a6' : '#666666',
      colorTextTertiary: isDarkMode ? '#737373' : '#999999',
      colorTextQuaternary: isDarkMode ? '#595959' : '#bfbfbf',
      // 边框半径
      borderRadius: 6,
      borderRadiusLG: 8,
      borderRadiusOuter: 4,
      borderRadiusSM: 4,
      borderRadiusXS: 2,
      // 字体
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif',
      fontSize: 14,
      fontSizeHeading1: 38,
      fontSizeHeading2: 30,
      fontSizeHeading3: 24,
      fontSizeHeading4: 20,
      fontSizeHeading5: 16,
      fontSizeLG: 16,
      fontSizeSM: 12,
      fontSizeXL: 20,
      fontWeightStrong: 600,
      lineHeight: 1.5714285714285714,
      // 间距
      margin: 16,
      marginLG: 24,
      marginMD: 16,
      marginSM: 12,
      marginXL: 32,
      marginXS: 8,
      marginXXS: 4,
      padding: 16,
      paddingLG: 24,
      paddingMD: 16,
      paddingSM: 12,
      paddingXL: 32,
      paddingXS: 8,
      paddingXXS: 4,
      // 控制组件高度
      controlHeight: 32,
      controlHeightLG: 40,
      controlHeightSM: 24,
      controlHeightXS: 16,
      // 动画
      motionDurationFast: '0.1s',
      motionDurationMid: '0.2s',
      motionDurationSlow: '0.3s',
      motionEaseInOut: 'cubic-bezier(0.645, 0.045, 0.355, 1)',
      motionEaseOut: 'cubic-bezier(0.215, 0.61, 0.355, 1)',
    },
    components: {
      Layout: {
        bodyBg: isDarkMode ? '#141414' : '#f5f5f5',
        headerBg: isDarkMode ? '#1f1f1f' : '#ffffff',
        siderBg: isDarkMode ? '#1f1f1f' : '#ffffff',
        triggerBg: isDarkMode ? '#262626' : '#f0f0f0',
      },
      Card: {
        headerBg: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBorderSecondary: isDarkMode ? '#303030' : '#f0f0f0',
      },
      Table: {
        headerBg: isDarkMode ? '#262626' : '#fafafa',
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        rowHoverBg: isDarkMode ? '#262626' : '#f5f5f5',
      },
      Menu: {
        darkItemBg: isDarkMode ? '#1f1f1f' : '#001529',
        darkItemColor: isDarkMode ? '#ffffff' : 'rgba(255, 255, 255, 0.65)',
        darkItemHoverBg: isDarkMode ? '#262626' : '#1890ff',
        darkItemSelectedBg: isDarkMode ? '#1890ff' : '#1890ff',
      },
      Button: {
        colorPrimaryHover: isDarkMode ? '#4096ff' : '#40a9ff',
        colorPrimaryActive: isDarkMode ? '#0958d9' : '#096dd9',
        borderRadius: 6,
        borderRadiusLG: 8,
        borderRadiusSM: 4,
      },
      Input: {
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBorder: isDarkMode ? '#434343' : '#d9d9d9',
        colorBorderHover: isDarkMode ? '#4096ff' : '#40a9ff',
        borderRadius: 6,
      },
      Modal: {
        headerBg: isDarkMode ? '#1f1f1f' : '#ffffff',
        contentBg: isDarkMode ? '#1f1f1f' : '#ffffff',
        footerBg: isDarkMode ? '#1f1f1f' : '#ffffff',
      },
      Drawer: {
        colorBgElevated: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBgMask: isDarkMode ? 'rgba(0, 0, 0, 0.45)' : 'rgba(0, 0, 0, 0.45)',
      },
      Tabs: {
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBorderSecondary: isDarkMode ? '#303030' : '#f0f0f0',
      },
      Message: {
        colorBgElevated: isDarkMode ? '#262626' : '#ffffff',
        colorSuccess: '#52c41a',
        colorError: '#ff4d4f',
        colorWarning: '#faad14',
        colorInfo: '#1890ff',
      },
      Notification: {
        colorBgElevated: isDarkMode ? '#262626' : '#ffffff',
        colorIcon: isDarkMode ? '#ffffff' : '#000000',
        colorIconHover: isDarkMode ? '#4096ff' : '#40a9ff',
      },
      Tooltip: {
        colorBgSpotlight: isDarkMode ? '#434343' : '#ffffff',
        colorTextLightSolid: isDarkMode ? '#ffffff' : '#000000',
      },
      Tag: {
        colorFillSecondary: isDarkMode ? '#262626' : '#f5f5f5',
        colorText: isDarkMode ? '#ffffff' : '#000000',
        colorTextSecondary: isDarkMode ? '#a6a6a6' : '#666666',
      },
      Alert: {
        colorSuccessBg: isDarkMode ? '#162312' : '#f6ffed',
        colorSuccessBorder: isDarkMode ? '#274916' : '#b7eb8f',
        colorInfoBg: isDarkMode ? '#111b2c' : '#e6f7ff',
        colorInfoBorder: isDarkMode ? '#1d2951' : '#91d5ff',
        colorWarningBg: isDarkMode ? '#2b2111' : '#fffbe6',
        colorWarningBorder: isDarkMode ? '#493c18' : '#ffe58f',
        colorErrorBg: isDarkMode ? '#2c1618' : '#fff2f0',
        colorErrorBorder: isDarkMode ? '#4a1a1c' : '#ffb3b3',
      },
      Form: {
        labelColor: isDarkMode ? '#ffffff' : '#000000',
        labelRequiredMarkColor: '#ff4d4f',
        itemMarginBottom: 16,
      },
      Select: {
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBgElevated: isDarkMode ? '#262626' : '#ffffff',
        colorBorder: isDarkMode ? '#434343' : '#d9d9d9',
        borderRadius: 6,
      },
      Switch: {
        colorPrimary: '#1890ff',
        colorPrimaryHover: isDarkMode ? '#4096ff' : '#40a9ff',
        colorTextQuaternary: isDarkMode ? '#434343' : '#d9d9d9',
        colorTextTertiary: isDarkMode ? '#595959' : '#999999',
      },
      Timeline: {
        colorSplit: isDarkMode ? '#434343' : '#f0f0f0',
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
      },
      Steps: {
        colorSplit: isDarkMode ? '#434343' : '#f0f0f0',
        colorFillContent: isDarkMode ? '#262626' : '#f5f5f5',
      },
      Collapse: {
        headerBg: isDarkMode ? '#262626' : '#fafafa',
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBorder: isDarkMode ? '#434343' : '#d9d9d9',
      },
      Tree: {
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBgContainerDisabled: isDarkMode ? '#1f1f1f' : '#f5f5f5',
        nodeHoverBg: isDarkMode ? '#262626' : '#f5f5f5',
        nodeSelectedBg: isDarkMode ? '#1890ff' : '#e6f7ff',
      },
      Dropdown: {
        colorBgElevated: isDarkMode ? '#262626' : '#ffffff',
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBorder: isDarkMode ? '#434343' : '#d9d9d9',
        controlItemBgHover: isDarkMode ? '#303030' : '#f5f5f5',
        controlItemBgActive: isDarkMode ? '#1890ff' : '#e6f7ff',
      },
      Pagination: {
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBgTextHover: isDarkMode ? '#262626' : '#f5f5f5',
        colorBgTextActive: isDarkMode ? '#1890ff' : '#e6f7ff',
        colorPrimary: '#1890ff',
        colorPrimaryHover: isDarkMode ? '#4096ff' : '#40a9ff',
        colorText: isDarkMode ? '#ffffff' : '#000000',
        colorTextDisabled: isDarkMode ? '#595959' : '#bfbfbf',
        borderRadius: 6,
      },
      Popconfirm: {
        colorBgElevated: isDarkMode ? '#262626' : '#ffffff',
        colorText: isDarkMode ? '#ffffff' : '#000000',
        colorTextHeading: isDarkMode ? '#ffffff' : '#000000',
        colorIcon: '#faad14',
        colorIconHover: '#ffc53d',
        borderRadius: 6,
      },
      Popover: {
        colorBgElevated: isDarkMode ? '#262626' : '#ffffff',
        colorText: isDarkMode ? '#ffffff' : '#000000',
        colorTextHeading: isDarkMode ? '#ffffff' : '#000000',
        borderRadius: 6,
      },
      Badge: {
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBorderBg: isDarkMode ? '#262626' : '#f0f0f0',
      },
      Breadcrumb: {
        colorBgTextHover: isDarkMode ? '#262626' : '#f5f5f5',
        colorText: isDarkMode ? '#ffffff' : '#000000',
        colorTextDescription: isDarkMode ? '#a6a6a6' : '#666666',
        linkColor: '#1890ff',
        linkHoverColor: isDarkMode ? '#4096ff' : '#40a9ff',
        separatorColor: isDarkMode ? '#a6a6a6' : '#666666',
      },
      DatePicker: {
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBgElevated: isDarkMode ? '#262626' : '#ffffff',
        colorBorder: isDarkMode ? '#434343' : '#d9d9d9',
        cellHoverBg: isDarkMode ? '#262626' : '#f5f5f5',
        cellActiveWithRangeBg: isDarkMode ? '#1890ff' : '#e6f7ff',
        borderRadius: 6,
      },
      Upload: {
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBorder: isDarkMode ? '#434343' : '#d9d9d9',
        colorBorderHover: isDarkMode ? '#4096ff' : '#40a9ff',
      },
      Spin: {
        colorPrimary: '#1890ff',
        colorWhite: isDarkMode ? '#ffffff' : '#ffffff',
      },
      Progress: {
        colorSuccess: '#52c41a',
        colorException: '#ff4d4f',
      },
      Divider: {
        colorSplit: isDarkMode ? '#434343' : '#f0f0f0',
        colorText: isDarkMode ? '#ffffff' : '#000000',
        colorTextHeading: isDarkMode ? '#ffffff' : '#000000',
      },
      Typography: {
        titleMarginBottom: 16,
        titleMarginTop: 16,
        fontWeightStrong: 600,
      },
      Empty: {
        colorTextDisabled: isDarkMode ? '#595959' : '#bfbfbf',
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
      },
      Result: {
        titleFontSize: 24,
        subtitleFontSize: 14,
        iconFontSize: 72,
        extraMargin: 24,
      },
      Skeleton: {
        color: isDarkMode ? '#303030' : '#f0f0f0',
        colorGradientEnd: isDarkMode ? '#434343' : '#f0f0f0',
        borderRadius: 4,
      },
      Statistic: {
        titleFontSize: 14,
        contentFontSize: 24,
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif',
      },
      List: {
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBorder: isDarkMode ? '#434343' : '#d9d9d9',
        colorSplit: isDarkMode ? '#303030' : '#f0f0f0',
        itemHoverBg: isDarkMode ? '#262626' : '#f5f5f5',
        itemActiveBg: isDarkMode ? '#1890ff' : '#e6f7ff',
        headerBg: isDarkMode ? '#262626' : '#fafafa',
        footerBg: isDarkMode ? '#262626' : '#fafafa',
      },
      Calendar: {
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBgElevated: isDarkMode ? '#262626' : '#ffffff',
        colorBorder: isDarkMode ? '#434343' : '#d9d9d9',
        colorSplit: isDarkMode ? '#303030' : '#f0f0f0',
        cellHoverBg: isDarkMode ? '#262626' : '#f5f5f5',
        cellActiveWithRangeBg: isDarkMode ? '#1890ff' : '#e6f7ff',
      },
      Descriptions: {
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorFillAlter: isDarkMode ? '#262626' : '#fafafa',
        colorSplit: isDarkMode ? '#303030' : '#f0f0f0',
        labelBg: isDarkMode ? '#262626' : '#fafafa',
        titleColor: isDarkMode ? '#ffffff' : '#000000',
      },
      Rate: {
        colorFillContent: isDarkMode ? '#434343' : '#f0f0f0',
        colorText: isDarkMode ? '#faad14' : '#faad14',
      },
      Slider: {
        colorPrimary: '#1890ff',
        colorPrimaryBorder: isDarkMode ? '#4096ff' : '#40a9ff',
        colorPrimaryBorderHover: isDarkMode ? '#4096ff' : '#40a9ff',
        colorBgElevated: isDarkMode ? '#262626' : '#ffffff',
        handleColor: '#1890ff',
        handleColorHover: isDarkMode ? '#4096ff' : '#40a9ff',
        railBg: isDarkMode ? '#434343' : '#f5f5f5',
        railHoverBg: isDarkMode ? '#595959' : '#e1e1e1',
        trackBg: '#1890ff',
        trackHoverBg: isDarkMode ? '#4096ff' : '#40a9ff',
      },
      Anchor: {
        colorPrimary: '#1890ff',
        colorSplit: isDarkMode ? '#434343' : '#f0f0f0',
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
      },
      Avatar: {
        colorBgContainer: isDarkMode ? '#262626' : '#f5f5f5',
        colorText: isDarkMode ? '#ffffff' : '#000000',
        colorTextPlaceholder: isDarkMode ? '#a6a6a6' : '#999999',
      },
      BackTop: {
        colorBgElevated: isDarkMode ? '#262626' : '#ffffff',
        colorText: isDarkMode ? '#ffffff' : '#000000',
        colorTextDescription: isDarkMode ? '#a6a6a6' : '#666666',
      },
      Image: {
        colorBgMask: isDarkMode ? 'rgba(0, 0, 0, 0.45)' : 'rgba(0, 0, 0, 0.45)',
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
      },
      Checkbox: {
        colorPrimary: '#1890ff',
        colorPrimaryHover: isDarkMode ? '#4096ff' : '#40a9ff',
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBorder: isDarkMode ? '#434343' : '#d9d9d9',
      },
      Radio: {
        colorPrimary: '#1890ff',
        colorPrimaryHover: isDarkMode ? '#4096ff' : '#40a9ff',
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBorder: isDarkMode ? '#434343' : '#d9d9d9',
      },
      Transfer: {
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBgContainerDisabled: isDarkMode ? '#1f1f1f' : '#f5f5f5',
        colorBorder: isDarkMode ? '#434343' : '#d9d9d9',
        headerBg: isDarkMode ? '#262626' : '#fafafa',
        itemHoverBg: isDarkMode ? '#262626' : '#f5f5f5',
        itemSelectedBg: isDarkMode ? '#1890ff' : '#e6f7ff',
      },
      AutoComplete: {
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBgElevated: isDarkMode ? '#262626' : '#ffffff',
        colorBorder: isDarkMode ? '#434343' : '#d9d9d9',
        borderRadius: 6,
      },
      Cascader: {
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBgElevated: isDarkMode ? '#262626' : '#ffffff',
        colorBorder: isDarkMode ? '#434343' : '#d9d9d9',
        borderRadius: 6,
      },
      Mentions: {
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBgElevated: isDarkMode ? '#262626' : '#ffffff',
        colorBorder: isDarkMode ? '#434343' : '#d9d9d9',
        borderRadius: 6,
      },
      Affix: {
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBorder: isDarkMode ? '#434343' : '#d9d9d9',
      },
      PageHeader: {
        colorBgContainer: isDarkMode ? '#1f1f1f' : '#ffffff',
        colorBorder: isDarkMode ? '#434343' : '#d9d9d9',
        colorBorderSecondary: isDarkMode ? '#303030' : '#f0f0f0',
      },
    },
  };

  const value = {
    isDarkMode,
    toggleTheme,
    themeConfig,
  };

  return (
    <ThemeContext.Provider value={value}>
      <ConfigProvider theme={themeConfig}>
        {children}
      </ConfigProvider>
    </ThemeContext.Provider>
  );
};

ThemeProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

export default ThemeProvider;