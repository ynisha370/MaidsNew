module.exports = {
  apps: [
    {
      name: 'maids-backend',
      script: 'venv/bin/python',
      args: 'server.py',
      cwd: '/root/MaidsNew/backend',
      instances: 1,
      exec_mode: 'fork',
      env: {
        NODE_ENV: 'production',
        PORT: 8000
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 8000
      },
      log_file: '/root/MaidsNew/logs/backend.log',
      out_file: '/root/MaidsNew/logs/backend-out.log',
      error_file: '/root/MaidsNew/logs/backend-error.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      max_memory_restart: '1G',
      restart_delay: 4000,
      max_restarts: 10,
      min_uptime: '10s',
      watch: false,
      ignore_watch: ['node_modules', 'logs', '*.log'],
      kill_timeout: 5000,
      wait_ready: true,
      listen_timeout: 10000
    },
    {
      name: 'maids-frontend',
      script: 'npm',
      args: 'start',
      cwd: '/root/MaidsNew/frontend',
      instances: 1,
      exec_mode: 'fork',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
        REACT_APP_BACKEND_URL: 'http://localhost:8000'
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 3000,
        REACT_APP_BACKEND_URL: 'http://localhost:8000'
      },
      log_file: '/root/MaidsNew/logs/frontend.log',
      out_file: '/root/MaidsNew/logs/frontend-out.log',
      error_file: '/root/MaidsNew/logs/frontend-error.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      max_memory_restart: '1G',
      restart_delay: 4000,
      max_restarts: 10,
      min_uptime: '10s',
      watch: false,
      ignore_watch: ['node_modules', 'logs', '*.log', 'build'],
      kill_timeout: 5000,
      wait_ready: true,
      listen_timeout: 10000
    }
  ]
};
