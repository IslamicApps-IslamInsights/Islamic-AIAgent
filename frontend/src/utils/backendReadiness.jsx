/**
 * Frontend Backend Synchronization
 * ================================
 * 
 * Ensures frontend only initializes when backend is fully ready.
 * Prevents UI race conditions and errors.
 */

import React, { useEffect, useState } from 'react';

/**
 * Backend readiness service - handles synchronization
 */
class BackendReadinessService {
  constructor(apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5010') {
    this.apiUrl = apiUrl;
    this.readinessCheckInterval = null;
    this.listeners = [];
    this.currentStatus = {
      ready: false,
      percentage: 0,
      initialized: false,
      components: {}
    };
  }

  /**
   * Add a listener for readiness changes
   */
  addListener(callback) {
    this.listeners.push(callback);
    // Notify immediately with current status
    callback(this.currentStatus);
  }

  /**
   * Notify all listeners of status change
   */
  notifyListeners() {
    this.listeners.forEach(listener => {
      try {
        listener(this.currentStatus);
      } catch (error) {
        console.error('Error in readiness listener:', error);
      }
    });
  }

  /**
   * Check backend readiness once
   */
  async checkReadiness() {
    try {
      const response = await fetch(`${this.apiUrl}/api/readiness/status`, {
        signal: AbortSignal.timeout(5000) // 5s timeout
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      const readiness = data.readiness || {};

      this.currentStatus = {
        ready: data.ready_for_frontend || readiness.core_ready || false,
        fully_initialized: data.fully_initialized || readiness.initialized || false,
        percentage: this.calculatePercentage(readiness.components || {}),
        components: readiness.components || {},
        startup_time: readiness.startup_time || 0
      };

      this.notifyListeners();
      return this.currentStatus;
    } catch (error) {
      console.warn('⚠️ Backend readiness check failed:', error);
      this.currentStatus = {
        ready: false,
        fully_initialized: false,
        percentage: 0,
        components: {},
        error: error.message
      };
      return this.currentStatus;
    }
  }

  /**
   * Calculate readiness percentage from components
   */
  calculatePercentage(components) {
    if (!components || Object.keys(components).length === 0) return 0;

    const total = Object.keys(components).length;
    const ready = Object.values(components).filter(c => c.ready).length;

    return Math.round((ready / total) * 100);
  }

  /**
   * Poll for backend readiness
   */
  startPolling(interval = 1000) {
    this.stopPolling();

    this.readinessCheckInterval = setInterval(async () => {
      await this.checkReadiness();

      // Stop polling once ready
      if (this.currentStatus.ready) {
        console.log('✅ Backend ready, stopping readiness polls');
        this.stopPolling();
      }
    }, interval);

    // Initial check
    this.checkReadiness();
  }

  /**
   * Stop polling for readiness
   */
  stopPolling() {
    if (this.readinessCheckInterval) {
      clearInterval(this.readinessCheckInterval);
      this.readinessCheckInterval = null;
    }
  }

  /**
   * Wait for backend to be ready (blocking)
   */
  async waitForReady(timeout = 30000) {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      await this.checkReadiness();

      if (this.currentStatus.ready) {
        console.log('✅ Backend ready after', Date.now() - startTime, 'ms');
        return true;
      }

      // Wait before next check
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    console.error('❌ Backend readiness timeout');
    return false;
  }

  /**
   * Get current status
   */
  getStatus() {
    return { ...this.currentStatus };
  }

  /**
   * Verify backend health
   */
  async verifyHealth() {
    try {
      const response = await fetch(`${this.apiUrl}/api/health`, {
        signal: AbortSignal.timeout(3000)
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * Destroy and cleanup
   */
  destroy() {
    this.stopPolling();
    this.listeners = [];
  }
}

/**
 * React Hook: useBackendReady
 * 
 * Usage:
 * const { ready, percentage, error } = useBackendReady();
 * 
 * return ready ? <App /> : <LoadingScreen percentage={percentage} />;
 */
function useBackendReady(apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5010') {
  const [readiness, setReadiness] = useState({
    ready: false,
    percentage: 0,
    error: null,
    components: {}
  });

  useEffect(() => {
    const service = new BackendReadinessService(apiUrl);

    // Set up listener for status changes
    service.addListener((status) => {
      setReadiness({
        ready: status.ready,
        percentage: status.percentage,
        fully_initialized: status.fully_initialized,
        components: status.components,
        error: status.error || null
      });
    });

    // Start polling
    service.startPolling(1000);

    // Cleanup
    return () => {
      service.destroy();
    };
  }, [apiUrl]);

  return readiness;
}

/**
 * React Component: BackendReadinessWrapper
 * 
 * Wraps an app component and shows loading screen until backend is ready
 */
function BackendReadinessWrapper({ children, apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5010' }) {
  const readiness = useBackendReady(apiUrl);

  if (!readiness.ready) {
    return (
      <div style={styles.container}>
        <div style={styles.loadingBox}>
          <h1 style={styles.title}>🌙 Islamic AI Agent</h1>
          <p style={styles.subtitle}>Initializing Backend Systems...</p>

          {/* Progress bar */}
          <div style={styles.progressBar}>
            <div
              style={{
                ...styles.progressFill,
                width: `${readiness.percentage}%`
              }}
            />
          </div>

          <p style={styles.percentage}>{Math.round(readiness.percentage)}%</p>

          {/* Component status */}
          <div style={styles.componentList}>
            {Object.entries(readiness.components || {}).map(([name, status]) => (
              <div key={name} style={styles.componentItem}>
                <span style={styles.componentStatus}>
                  {status.ready ? '✅' : '⏳'}
                </span>
                <span style={styles.componentName}>{name}</span>
              </div>
            ))}
          </div>

          {/* Error message */}
          {readiness.error && (
            <p style={styles.error}>⚠️ {readiness.error}</p>
          )}

          <p style={styles.waitText}>Please wait, this may take a moment...</p>
        </div>
      </div>
    );
  }

  // Backend is ready, render children
  return children;
}

/**
 * Styles for loading screen
 */
const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    backgroundColor: '#0f172a',
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
  },
  loadingBox: {
    textAlign: 'center',
    padding: '40px',
    backgroundColor: '#1e293b',
    borderRadius: '12px',
    boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
    maxWidth: '400px',
    color: '#e2e8f0'
  },
  title: {
    margin: '0 0 10px 0',
    fontSize: '28px',
    color: '#fbbf24'
  },
  subtitle: {
    margin: '0 0 30px 0',
    fontSize: '16px',
    color: '#cbd5e1'
  },
  progressBar: {
    width: '100%',
    height: '8px',
    backgroundColor: '#334155',
    borderRadius: '4px',
    overflow: 'hidden',
    marginBottom: '15px'
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#10b981',
    transition: 'width 0.3s ease',
    borderRadius: '4px'
  },
  percentage: {
    margin: '0 0 20px 0',
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#10b981'
  },
  componentList: {
    textAlign: 'left',
    padding: '15px',
    backgroundColor: '#0f172a',
    borderRadius: '8px',
    marginBottom: '20px',
    maxHeight: '200px',
    overflowY: 'auto'
  },
  componentItem: {
    display: 'flex',
    alignItems: 'center',
    padding: '8px 0',
    fontSize: '14px',
    color: '#cbd5e1'
  },
  componentStatus: {
    marginRight: '10px',
    minWidth: '20px'
  },
  componentName: {
    textTransform: 'capitalize',
    fontFamily: 'monospace'
  },
  error: {
    margin: '0 0 15px 0',
    padding: '10px',
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    color: '#fca5a5',
    borderRadius: '4px',
    fontSize: '14px'
  },
  waitText: {
    margin: '0',
    fontSize: '13px',
    color: '#94a3b8'
  }
};

export {
  BackendReadinessService,
  useBackendReady,
  BackendReadinessWrapper,
  styles as loadingStyles
};
