import axios from 'axios';

// 🔧 변경: 환경에 따라 자동으로 API URL 설정
const getApiBaseUrl = () => {
  // 1. 환경변수에서 API URL 가져오기 (최우선)
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // 2. 프로덕션 환경: 상대 경로 사용 (Render 배포 시)
  if (process.env.NODE_ENV === 'production') {
    return '/api';
  }
  
  // 3. 개발 환경: localhost 사용
  return 'http://localhost:8000/api';
};

const API_BASE_URL = getApiBaseUrl();

console.log('API Base URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // 🔧 추가: 10초 타임아웃
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터: JWT 토큰 자동 추가
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 🔧 추가: 응답 인터셉터 - 에러 처리
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 401 에러: 토큰 만료 또는 인증 실패
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    
    // 네트워크 에러
    if (!error.response) {
      console.error('Network error:', error);
      alert('서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.');
    }
    
    return Promise.reject(error);
  }
);

export default api;
