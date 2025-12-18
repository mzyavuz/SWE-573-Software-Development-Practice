/**
 * Centralized Balance Manager
 * Handles all time balance updates across the application
 * Dispatches events to notify all components of balance changes
 */

const BalanceManager = {
    // Track if an update is in progress to prevent concurrent updates
    updating: false,
    
    /**
     * Update the user's time balance from the server
     * @returns {Promise<number|null>} The updated balance or null if failed
     */
    async update() {
        // Prevent concurrent updates
        if (this.updating) {
            console.log('Balance update already in progress, skipping...');
            return null;
        }
        
        this.updating = true;
        
        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                console.warn('No access token found, cannot update balance');
                this.updating = false;
                return null;
            }

            const response = await fetch('/api/auth/profile', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                const data = await response.json();
                const newBalance = data.user.time_balance;
                
                // Update localStorage
                const userData = JSON.parse(localStorage.getItem('user') || '{}');
                const oldBalance = userData.time_balance;
                userData.time_balance = newBalance;
                localStorage.setItem('user', JSON.stringify(userData));

                // Update navbar if available
                if (window.NavBar && window.NavBar.updateBalance) {
                    window.NavBar.updateBalance(newBalance);
                }

                // Dispatch custom event for other components to listen to
                window.dispatchEvent(new CustomEvent('balanceUpdated', {
                    detail: { 
                        balance: newBalance,
                        oldBalance: oldBalance,
                        change: newBalance - (oldBalance || 0)
                    }
                }));
                
                console.log(`Balance updated: ${oldBalance} → ${newBalance}`);
                this.updating = false;
                return newBalance;
            } else {
                console.error('Failed to fetch user balance:', response.status);
                this.updating = false;
                return null;
            }
        } catch (error) {
            console.error('Error updating balance:', error);
            this.updating = false;
            return null;
        }
    },

    /**
     * Get current balance from localStorage (cached value)
     * @returns {number} Current cached balance
     */
    getCurrentBalance() {
        const userData = JSON.parse(localStorage.getItem('user') || '{}');
        return userData.time_balance || 0;
    },

    /**
     * Format balance for display (removes .00 from whole numbers)
     * @param {number} balance - The balance to format
     * @returns {string} Formatted balance string
     */
    formatBalance(balance) {
        const balanceText = balance % 1 === 0 ? Math.round(balance) : balance.toFixed(1);
        const label = balance === 1 ? 'hour' : 'hours';
        return `${balanceText} ${label}`;
    },

    /**
     * Setup automatic balance refresh on page visibility change
     * Updates balance when user returns to the tab
     */
    setupVisibilityListener() {
        if (this.visibilityListenerAdded) return;
        
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                // Page became visible, refresh balance
                console.log('Page visible, refreshing balance...');
                this.update();
            }
        });
        
        this.visibilityListenerAdded = true;
        console.log('Balance visibility listener setup complete');
    },

    /**
     * Setup periodic polling for balance updates
     * @param {number} intervalSeconds - How often to poll (default 60 seconds)
     */
    startPolling(intervalSeconds = 60) {
        if (this.pollingInterval) {
            console.log('Polling already active');
            return;
        }
        
        this.pollingInterval = setInterval(() => {
            console.log('Polling balance update...');
            this.update();
        }, intervalSeconds * 1000);
        
        console.log(`Balance polling started (every ${intervalSeconds} seconds)`);
    },

    /**
     * Stop periodic polling
     */
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
            console.log('Balance polling stopped');
        }
    },

    /**
     * Initialize the balance manager with optional polling
     * @param {boolean} enablePolling - Whether to enable periodic polling
     * @param {number} intervalSeconds - Polling interval if enabled
     */
    init(enablePolling = true, intervalSeconds = 60) {
        // Setup visibility listener (always enabled)
        this.setupVisibilityListener();
        
        // Setup polling if requested
        if (enablePolling) {
            this.startPolling(intervalSeconds);
        }
        
        // Do initial update
        this.update();
        
        console.log('BalanceManager initialized');
    }
};

// Make it globally available
window.BalanceManager = BalanceManager;
