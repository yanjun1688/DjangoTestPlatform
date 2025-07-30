import React from 'react';
import './BackButton.css';

const BackButton = ({ onClick, style = {} }) => {
  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      // Default behavior: go back in history
      window.history.back();
    }
  };

  return (
    <button 
      className="back-button"
      onClick={handleClick}
      style={style}
      title="返回上一页"
    >
      <svg 
        width="16" 
        height="16" 
        viewBox="0 0 24 24" 
        fill="none" 
        stroke="currentColor" 
        strokeWidth="2" 
        strokeLinecap="round" 
        strokeLinejoin="round"
      >
        <path d="M19 12H5M12 19l-7-7 7-7"/>
      </svg>
      返回
    </button>
  );
};

export default BackButton;